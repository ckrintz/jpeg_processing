'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import csv
from pprint import pprint
import json, sys, argparse, csv, logging, os, time
import numpy as np
from datetime import datetime, timedelta
import dbiface
import upload_files
import tinys3
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

DEBUG=False
SEDGWICK='7411611121' #Shared Sedgwick Images Folder
#SEDGWICK='0'

############## START generate eMammal CSVs -- see ../emammal/CJKREADME for sample ################
def generate_emammal_Deployment(deployID): #only called once
    with open('Deployment.csv','wt') as f:
        csvFile = csv.writer(f)
        csvFile.writerow(('Camera Deployment ID','Camera Site Name','Camera Deployment Begin Date','Camera Deployment End Date','Actual Latitude','Actual Longitude','Camera Failure Details','Bait  ','Bait Description','Feature','Feature Methodology','Camera ID','Quiet Period Setting','Sensitivity Setting'))
        csvFile.writerow((deployID,'Main Road Water Hole','2013/07/13 15:30:00','2013/10/13 22:45:32','34.71995','-120.0363','Camera Functioning','No Bait','','Water source/Spring','water hole','Reconyx_001','0',''))

def generate_emammal_Project(projID,projName,start_date_string):
    with open('Project.csv','wt') as f: #only called once
        csvFile = csv.writer(f)
        csvFile.writerow(('Project ID','Publish Date','Project Name','Project Objectives','Project Owner','Project Owner Email','Principal Investigator','Principal Investigator Email','Project Contact','Project Contact Email','Project Latitude','Project Longitude','Country Code','Project Data Use and Constraints'))
        csvFile.writerow((projID,start_date_string,projName,'Camera trap survey','Kate McCurdy','mccurdy@lifesci.ucsb.edu','Chandra Krintz','ckrintz@cs.ucsb.edu','Chandra Krintz','ckrintz@cs.ucsb.edu','34.6928059','-120.0406417','USA','NE'))

def generate_emammal_Image(deployID,seqID,iID,path,tss,writeHeader=False):
    #called once for each image
    if writeHeader:
        with open('Image.csv','wt') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow(('Deployment ID','Image Sequence ID','Image ID','Location','Image File Name','Photo Type', 'Photo Type Identified by','Genus Species','IUCN ID','IUCN Status','Date_Time','Interest Rank','Age','Sex','Individual ID','Count','Animal recognizable','Individual Animal Notes','Digital Origin','Embargo Period','Restrictions on Access','Image Use Restrictions'))
            csvFile.writerow((deployID,seqID,iID,path,iID,'','','','','',tss,'None','','','',1,'','','born digital','','',''))
    else:
        with open('Image.csv','at') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow((deployID,seqID,iID,path,iID,'','','','','',tss,'None','','','',1,'','','born digital','','',''))

def generate_emammal_Sequence(deployID,seqID,tss_start,tss_end,writeHeader=False):
    '''tss_start and tss_end are string datetime format: YYYY/MM/DD HH/mm/ss'''
    #this is called once for each sequence
    if DEBUG:
	print 'in generate_emammal_Sequence writeHeader={0} seqid: {1}'.format(writeHeader,seqID)
    if writeHeader:
        with open('Sequence.csv','wt') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow(('Observation Type','Deployment ID','Image Sequence ID','Date_Time Begin','Date_Time End','Genus species','Species Common Name','Age','Sex','Individual ID','Count','Animal recognizable','Individual Animal Notes','TSN ID','IUCN ID','IUCN Status'))
            csvFile.writerow(('Researcher',deployID,seqID,tss_start,tss_end,'Unknown Animal','Unknown Animal','','','',1,'','','2','2','NE'))
    else:
        with open('Sequence.csv','at') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow(('Researcher',deployID,seqID,tss_start,tss_end,'Unknown Animal','Unknown Animal','','','',1,'','','2','2','NE'))

############## END generate eMammal CSVs -- see ../emammal/CJKREADME for sample ################

def upload_file_to_s3(fname,bkt,s3key,s3secret,isText=False,fileIsString=None,prefix=None):
    ''' Upload a file called fname to bucket bkt in S3 using credentials s3key and s3secret
        if fnameIsString is not passed in then we treat fname as a file and use its name as the remote s3 file name
		This is used if there is a local file on disk that we wish to upload
	else we use the value passed into fname as the s3 remote file name and the fnameIsString value 
		for the stringIO (in memory file)
		This is used if we are creating a file in memory (e.g. we downloaded it from Box without writing it to disk)
        Set isText to True if uploading a text file (csv/other)
    '''
    # Creating a simple connection
    conn = tinys3.Connection(s3key,s3secret)

    # Get the file object
    if fileIsString is None:
        f = open(fname,'rb')
    else:
        f = StringIO(fileIsString)

    # If prefix is set, then make fname in s3 to be equal prefix/fname
    if prefix:
        fname = '{0}/{1}'.format(prefix,fname)

    try: 
        # Upload the named file, writes to file called fname in the bucket potentially with a directory prefix
        if isText: #assumes text
            conn.upload(fname,f,bkt,content_type='text/plain')
        else: #assumes JPEG
            conn.upload(fname,f,bkt,content_type='image/jpeg')
        print 'uploaded {0} successfully'.format(fname)
    except:
        time.sleep(5) #sleep for 5 seconds and try again
        try: 
            # Upload the named file 
            if isText: #assumes text
                conn.upload(fname,f,bkt,content_type='text/plain')
            else: #assumes JPEG
                conn.upload(fname,f,bkt,content_type='image/jpeg')
            print 'uploaded {0} successfully'.format(fname)
        except:
            print 'Unable to upload file {0}'.format(fname)
            #write the file locally so that it can be uploaded manually via --uploadOnly
	    #csv/text files are already written, just write jpegs if they come in as strings
            if fileIsString is not None:
                with open(fname,'wb') as f:
		    f.write(fileIsString)
                    print 'wrote {0} as a local file -> upload to s3 manually via'.format(fname)
                    print 'python emammal.py --s3acc="AKXXX" --s3sec="xXXX" --s3bkt="bucketname" --uploadOnly="{0}"'.format(fname)
    

def main():
    global DEBUG #to allow setting DEBUG flag via command line
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='JPEG/Box File Processing for Emammal (AWS S3) Upload.  Omit any/all of the s3 option arguments and the program will not perform the s3 upload (good for testing)')
    #required arguments: None
    #optional arguments
    parser.add_argument('--s3acc',default=None,action='store',help='AWS S3_ACCESS_KEY')
    parser.add_argument('--s3sec',default=None,action='store',help='AWS S3_SECRET_KEY')
    parser.add_argument('--s3bkt',default=None,action='store',help='AWS S3 Bucket Name')
    parser.add_argument('--s3prefix',default=None,action='store',help='AWS S3 File (e.g. directory) Prefix')
    parser.add_argument('--uploadOnly',default=None,action='store',help='Local file name in current working directory to upload to S3. This is used if the original run has exceptions with the s3 upload (which then writes the file locally).  Note the file names from this problem run and run this program for each individual name to upload.')
    parser.add_argument('--uploadCSVsOnly',default=False,action='store_true',help='Generate and upload CSV files (metainfo) only to S3 (requires s3acc,s3sec,s3bkt)')
    parser.add_argument('--multimonth',default=False,action='store_true',help='Process all months, by month in the year specified by --year (2013 used if --year not set)')
    parser.add_argument('--year',default='2013',action='store',help='Only works when multimonth is set, must be 2013,2014,2015,or 2016')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on')
    args = parser.parse_args()

    #datetime temp
    dtdict = {}
    DEBUG = args.debug
    acc = args.s3acc
    sec = args.s3sec
    bkt = args.s3bkt
    pref = args.s3prefix
    csvonly = args.uploadCSVsOnly
    upload = args.uploadOnly
    first = True
    if csvonly and upload is not None:
        print 'Error, uploadOnly and uploadCSVsOnly cannot both be set at the same time'
        sys.exit(1)
    if acc and sec and bkt and upload is not None:
        try:
            upload_file_to_s3(upload,bkt,acc,sec,isText=(upload.endswith('.csv')),prefix=pref)
        except:
            time.sleep(5) #sleep for 5 seconds and try again
            upload_file_to_s3(upload,bkt,acc,sec,isText=(upload.endswith('.csv')),prefix=pref)
        sys.exit(0)
    if not csvonly and upload is not None:
        print 'Error, uploadOnly must be set with all three s3 arguments for upload to be performed'
        sys.exit(1)

    deploy_year = '2013'
    months = ['07']
    if args.multimonth:
        deploy_year = args.year

	#tests: all but last should continue to next month with "Error, no files came back"
        #months = ['03','04','05','06'] #tests missing, empty dir,  dir with 1 dir,  one dir with dir and 1 entry

        months = ['01','02','03','04','05','06','07','08','09','10','11','12']


    '''This code assumes we are processing one month maximum (less works) and produces csvs accordingly'''
    #emammal requests each deployment be for a single month in a year.  July (07) 2013 is the first large test:

    #log into box if needed
    auth_client = upload_files.setup()
    projPrefix = 'Sedgwick' #The same for Deployment.csv, Sequence.csv, and Image.csv, use dashes

    #process the months in the months list for the deploy year specified
    for cur_month in months:
        deployment_string = '{0}-{1}'.format(deploy_year,cur_month)
        if not args.s3prefix: #using args.s3prefix here to see if user set the prefix or not (pref changes across loops)
            pref = '{0}{1}'.format(deploy_year,cur_month) #s3 directory name
        if DEBUG:
            print 'Setting prefix to {0}'.format(pref)

        #set fname to JPG file name prefix of interest (one Sedgwick location at a time, here Main only)
        fname = 'Main_{0}'.format(deployment_string) #2013-07: 32260 in dir at 450K each is 14.9GB - 24hrs at 22/min

        #emammal small test:
        #deployment_string = '2013-10'
        #very small emammal test
	#deployment_string = '2013-07-15'
        #very very small emammal test
	#deployment_string = '2013-10-13_02' #350 images in dir at 450K each is 161MB
        if DEBUG:
            print 'searching for prefix: {0}'.format(fname)
    
        #datastructures for image metadata and csv's
        series = {} #values (series number) map to namelist entries
        ids = {} #values (box File IDs) map to namelist entries
        namelist = []
    
        #generate deployment and project csv (this overwrites Deployment.csv and Project.csv
        #separate name sections with underscore (so use dashes within name sections)
        deployID = 'Main-Reconyx-001_{0}'.format(deployment_string) #The same for Deployment.csv, Sequence.csv, and Image.csv, use dashes
        seqPrefix = projPrefix + '_' + deployID + '_'  # seq IDs must be unique within project, append unique counter to this prefix
        #write deployment metainfo to the Deployment CSV
        generate_emammal_Deployment(deployID)
        #write project metainfo to the Project CSV
        generate_emammal_Project(projPrefix,projPrefix,'2016/06/05')
        writeSequenceHeader = True  #write out header the first time only
        writeImageHeader = True  #write out header the first time only

        #the following returns and unordered list, not guaranteed that all entries returned have the prefix
        #get one file as a start so that we can get its folder (day) and (month) folders
        limit = 1
        jpegs = upload_files.get_files(auth_client,SEDGWICK,fname,0,limit) 
        if DEBUG:
            print 'len {0} jpeg {1}'.format(len(jpegs),jpegs[0].name)
        if len(jpegs) == limit and jpegs[0].name.startswith(fname): #sanity check to make sure one was found
            #help/info from: https://docs.box.com/reference#folder-object-1
            day_folder_id = jpegs[0].parent['id'] #get the box ID for the folder of this file (day folder)
            fldr = upload_files.get_folder(auth_client,day_folder_id) #returns folder object from box
            month_folder_id = fldr.parent['id'] #get the box ID for the folder of this file (month folder)
            fldr = upload_files.get_folder(auth_client,month_folder_id) #returns folder object from box 
    
            item_count = fldr['item_collection']['total_count'] #number of items in the folder total
            if DEBUG:
                print 'jpegs (sb 1): {0} folder id: {1} count:{2}'.format(len(jpegs),month_folder_id,item_count)
    
            count = 0
            foundcount = 0
    
            #get all of the items (Folder objects) in the month folder 
            #assumption: there will never be more than 31 folders (days/mo) so additional looping is not needed
            #extra files may get in the way (thus limit=1000), but we should not store anything in month
            #folders except for day folders!  
            days = fldr.get_items(limit=1000,offset=0) 
            if DEBUG: 
                print '#days in month folder {0}: {1}'.format(month_folder_id,len(days))
            for day in days:
                #loop through day folders in month folder
                if DEBUG: 
                    print '#file (in month folder) id: {0} name: {1} type: {2}'.format(day.id,day.name,type(day).__name__)
                if type(day).__name__=='Folder':  
                    #loop through files in the directory 1000 (max on folder get_items) at a time, starting at 0 oset
                    lim = 1000
                    oset = 0
                    jpegs = day.get_items(limit=lim,offset=oset) #get all of the items (File objects) in the folder
                    if DEBUG: 
                        print '#jpegs in day folder {0}: {1}, limit {2}, offset {3}'.format(day.id,len(jpegs),lim,oset)
                    while len(jpegs) > 0:
                        #testfound = 0
                        for ent in jpegs:
                            #make sure that item has type boxsdk.object.file.File; it could be a Folder
                            if type(ent).__name__=='File':  
                                if ent['name'].startswith(fname):
                                    #print 'found one: {0}'.format(ent['name'])
			            foundcount += 1
			            #testfound += 1
                                    namelist.append(ent['name'])
		                    ids[ent['name']] = ent['id']
                            count += 1
                        if len(jpegs) == lim:
                            oset += lim
                            jpegs = day.get_items(limit=lim,offset=oset) #get all of the items (File objects) in the folder
                            if DEBUG:
                                print '\tnext loop: #jpegs in day folder {0}: {1}, limit {2}, offset {3}'.format(day.id,len(jpegs),lim,oset)
                        else: 
                            break
               
            if DEBUG:
                #sanity check, verify that foundcount is the same as the number box says
                print 'total count: {0} foundcount: {1}'.format(count,foundcount)    
    
            first = True
            last = None
            #loop through the jpegs to generate Sequence.csv and a series/sequence ID for each image
            for name in sorted(namelist):
    
	        #file name format: Main_2013-10-13_14:20:40_17274.JPG
    
	        if first:
                    series[name] = seqPrefix + '1' #start series counter at 1 per emammal 6/8/16
	            thissplit = name.split('_')
                    ts = thissplit[1] + " " + thissplit[2]
                    first_in_series_tss = ts.replace('-','/') #used when series/sequence ends as tss_start
                    last_in_series_tss = first_in_series_tss #used when there's only one image and one series/sequence
 		    first = False
		    last = name
                    continue
    
  	        #parse the last name (date time string)
	        lastsplit  = last.split('_')
                ts = lastsplit[1] + " " + lastsplit[2]
                last_in_series_tss = ts.replace('-','/') #used when series/sequence ends
                lastdt = datetime.strptime( ts, '%Y-%m-%d %H:%M:%S')
    
  	        #parse the current name (date time string)
	        thissplit = name.split('_')
                ts = thissplit[1] + " " + thissplit[2]
                thisdt = datetime.strptime( ts, '%Y-%m-%d %H:%M:%S')
    
	        #take the difference
	        td = thisdt - lastdt
	        secs_diff = td.total_seconds()
    
	        #if secs_diff is <= 60 then name is part of the series in which last is in
	        if secs_diff <= 60:
		    series[name] = series[last]
	        else: 
                    #new Sequence -- write sequence metainfo to the Sequence CSV for the previous Sequence that just ended
                    seqID = series[last] #get ID of previous sequence (that is ending)
                    tmp = series[last].split('_')
                    seriesCounter = int(tmp[len(tmp)-1])
		    #use integer for Sequence ID not string per emammal 6/8/16
                    #generate_emammal_Sequence(deployID,seqID,first_in_series_tss,last_in_series_tss,writeSequenceHeader)
                    generate_emammal_Sequence(deployID,seriesCounter,first_in_series_tss,last_in_series_tss,writeSequenceHeader)
		    if writeSequenceHeader:
                        writeSequenceHeader = False
    
		    #update this image with the new Sequence ID
		    series[name] = seqPrefix + '{0}'.format(seriesCounter+1) #set the new sequence ID
                    first_in_series_tss = ts.replace('-','/') #used when series/sequence ends as tss_start
    
	        #now swap in this names info for last for the next iteration and iterate
	        last = name
    
            if last: 
                #write the last Sequence out (above writes are triggered on series change, there is none for last series)
                seqID = series[name] #get ID of this sequence
                #use integer for Sequence ID not string per emammal 6/8/16
                tmp = series[name].split('_')
                seriesCounter = int(tmp[len(tmp)-1])
                #write sequence metainfo to the Sequence CSV (seriesCounter below was seqID before update)
                generate_emammal_Sequence(deployID,seriesCounter,
                    first_in_series_tss,last_in_series_tss,
                    writeSequenceHeader)
        else:
	    print 'Error, no files came back for fname:{0}'.format(fname)
   	    continue  #go to next month
 
        #loop through them again to generate Image.csv and to download each file from box and upload it to S3
        count = 0
        for name in sorted(namelist):
            count += 1
	    if DEBUG:
                print '{0} {1}'.format(name,series[name],ids[name])
  	    #parse the current name (date time string)
	    thissplit = name.split('_')
            ts = thissplit[1] + " " + thissplit[2]
    
            #use integer for Sequence ID not string per emammal 6/8/16
            tmp = series[name].split('_')
            seriesCounter = int(tmp[len(tmp)-1])
            #write file metainfo to the Image CSV
            generate_emammal_Image(deployID,seriesCounter,name,ids[name],ts,writeImageHeader) #use box ID for location in box
	    if writeImageHeader:
                writeImageHeader = False
            
            #download file from Box and write it to s3
            if acc and sec and bkt:
	        if not csvonly:
                    fileObj = upload_files.get_file(auth_client,ids[name]) #get the Box File object from the entity ID
		    try:
                        upload_file_to_s3(name,bkt,acc,sec,fileIsString=fileObj.content(),prefix=pref)
        	    except:
            	        time.sleep(5) #sleep for 5 seconds and try again
                        upload_file_to_s3(name,bkt,acc,sec,fileIsString=fileObj.content(),prefix=pref)
    
        #at this point all csv files are written.  Upload them to s3
        if acc and sec and bkt:
	    try:
                upload_file_to_s3('Deployment.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Project.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Sequence.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Image.csv',bkt,acc,sec,isText=True,prefix=pref)
            except:
                time.sleep(5) #sleep for 5 seconds and try again
                upload_file_to_s3('Deployment.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Project.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Sequence.csv',bkt,acc,sec,isText=True,prefix=pref)
                upload_file_to_s3('Image.csv',bkt,acc,sec,isText=True,prefix=pref)
        else: 
            print 'not uploading files to s3:  s3acc, s3sec, and/or s3bkt is not set'
        print 'processed {0} files from Box for CSV generation for month {1} and prefix {2}'.format(count,cur_month,pref)

        #bottom of cur_month loop.  Do it all over again for the next month
    
    
if __name__ == '__main__':
    main()

