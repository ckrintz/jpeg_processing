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
        #csvFile.writerow((deployID,'Longitude Resolution','Latitude Resolution','Camera Deployment Begin Date','Camera Deployment End Date','Bait Type','Bait Description','Feature Type','Feature Type methodology','Camera Id','Quiet Period Setting (in seconds)','Restriction on Access (Yes/No only)','Camera Failure Details','','','',''))
        csvFile.writerow(('Camera Deployment ID','Camera Site Name','Camera Deployment Begin Date','Camera Deployment End Date','Actual Latitude','Actual Longitude','Camera Failure Details','Bait  ','Bait Description','Feature','Feature Methodology','Camera ID','Quiet Period Setting','Sensitivity Setting'))
        csvFile.writerow(('Main_Reconyx_001','Main Road Water Hole','2013/07/13 15:30:00','2013/10/13 22:45:32','34.71995','-120.0363','Camera Functioning','No bait','','Water source/spring','water hole','Reconyx_001','0',''))
	#Deployment ID: Main_Reconyx_001 must match in Images.csv

def generate_emammal_Project(projID,projName,start_date_string):
    with open('Project.csv','wt') as f: #only called once
        csvFile = csv.writer(f)
        #csvFile.writerow(('Project Id','Publish Date','Project Name','Project Objectives','Project Owner (organization or individual)','Project Owner Email (if applicable)','Principal Investigator','Principal Investigator Email','Project Contact','Project Contact Email','Country Code','Project Data Use and Constraints','','',''))
        csvFile.writerow(('Project ID','Publish Date','Project Name','Project Objectives','Project Owner','Project Owner Email','Principal Investigator','Principal Investigator Email','Project Contact','Project Contact Email','Project Latitude','Project Longitude','Country Code','Project Data Use and Constraints'))
        csvFile.writerow((projID,start_date_string,projName,'Camera trap survey','Sedgwick Reserve','sedgwick@lifesci.ucsb.edu','Chandra Krintz','ckrintz@cs.ucsb.edu','Chandra Krintz','ckrintz@cs.ucsb.edu','34.6928059','-120.0406417','USA','No constraints'))

def generate_emammal_Image(deployID,seqID,iID,path,tss,writeHeader=False):
    #called once for each image
    if writeHeader:
        with open('Image.csv','wt') as f: 
            csvFile = csv.writer(f)
            #csvFile.writerow(('Deployment ID','Sequence ID','Image Id','Location','Photo Type','Photo Type Identified by','Genus Species','IUCN Identification Number','Date_Time Captured', 'Age', 'Sex', 'Individual ID','Count','Animal recognizable (Y/N, blank)','individual Animal notes','',''))
            csvFile.writerow(('Deployment ID','Image Sequence ID','Image ID','Location','Image File Name','Photo Type', 'Photo Type Identified by','Genus Species','IUCN ID','IUCN Status','Date_Time','Interest Rank','Age','Sex','Individual ID','Count','Animal recognizable','Individual Animal Notes','Digital Origin','Embargo Period','Restrictions on Access','Image Use Restrictions'))
            #csvFile.writerow((deployID,seqID,iID,path,'Animal','','Unknown Animal','2',tss,'','','','','','','',''))
            csvFile.writerow((deployID,seqID,iID,path,iID,'','','','','',tss,'','','','','','','','born digital','','',''))
    else:
        with open('Image.csv','at') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow((deployID,seqID,iID,path,iID,'','','','','',tss,'','','','','','','','born digital','','',''))

def generate_emammal_Sequence(deployID,seqID,tss_start,tss_end,writeHeader=False):
    '''tss_start and tss_end are string datetime format: YYYY/MM/DD HH/mm/ss'''
    #this is called once for each sequence
    if DEBUG:
	print 'in generate_emammal_Sequence writeHeader={0} seqid: {1}'.format(writeHeader,seqID)
    if writeHeader:
        with open('Sequence.csv','wt') as f: 
            csvFile = csv.writer(f)
            #csvFile.writerow(('Observation Type','Deployment ID','Image Sequence ID','Begin Sequence Date Time','End Sequence Date Time','Species Name','Species Common Name','Age','Sex','Individual ID','Count','Animal recognizable (Y/N)','Individual Animal Notes','TSN ID','IUCN ID','',''))
            csvFile.writerow(('Observation Type','Deployment ID','Image Sequence ID','Date_Time Begin','Date_Time End','Genus species','Species Common Name','Age','Sex','Individual ID','Count','Animal recognizable','Individual Animal Notes','TSN ID','IUCN ID','IUCN Status'))
            csvFile.writerow(('Volunteer',deployID,seqID,tss_start,tss_end,'','','','','','','','','','',''))
    else:
        with open('Sequence.csv','at') as f: 
            csvFile = csv.writer(f)
            csvFile.writerow(('Volunteer',deployID,seqID,tss_start,tss_end,'','','','','','','','','','',''))

############## END generate eMammal CSVs -- see ../emammal/CJKREADME for sample ################

def upload_file_to_s3(fname,bkt,s3key,s3secret,isText=False,fileIsString=None):
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

    try: 
        # Upload the named file 
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
    parser.add_argument('--uploadOnly',default=None,action='store',help='Local file name in current working directory to upload to S3. This is used if the original run has exceptions with the s3 upload (which then writes the file locally).  Note the file names from this problem run and run this program for each individual name to upload.')
    parser.add_argument('--uploadCSVsOnly',default=False,action='store_true',help='Generate and upload CSV files (metainfo) only to S3 (requires s3acc,s3sec,s3bkt)')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on')
    args = parser.parse_args()

    #datetime temp
    dtdict = {}
    DEBUG = args.debug
    acc = args.s3acc
    sec = args.s3sec
    bkt = args.s3bkt
    csvonly = args.uploadCSVsOnly
    upload = args.uploadOnly
    first = True
    if csvonly and upload is not None:
        print 'Error, uploadOnly and uploadCSVsOnly cannot both be set at the same time'
        sys.exit(1)
    if acc and sec and bkt and upload is not None:
        upload_file_to_s3(upload,bkt,acc,sec,isText=(upload.endswith('.csv')))
        sys.exit(0)
    if not csvonly and upload is not None:
        print 'Error, uploadOnly must be set with all three s3 arguments for upload to be performed'
        sys.exit(1)

    #set the name of the file prefix to find/search from
    #fname = 'Blue_2015-04-15_14:34:10_00'
    fname = 'Main_2013-10-13_02' #30 in dir at 450K each is 7.3MB
    #fname = 'Sedgwick Camera' 
    #fname = 'Main_2013-10-13' #350 in dir at 450K each is 161MB

    #log into box if needed
    auth_client = upload_files.setup()
    series = {} #values (series number) map to namelist entries
    ids = {} #values (box File IDs) map to namelist entries
    namelist = []

    #generate deployment and project csv (this overwrites Deployment.csv and Project.csv
    #separate name sections with underscore (so use dashes within name sections)
    deployID = 'Main-Reconyx-001' #The same for Deployment.csv, Sequence.csv, and Image.csv, use dashes
    projPrefix = 'Sedgwick-Test1' #The same for Deployment.csv, Sequence.csv, and Image.csv, use dashes
    seqPrefix = projPrefix + '_' + deployID + '_'  # seq IDs must be unique within project, append unique counter to this prefix
    #write deployment metainfo to the Deployment CSV
    generate_emammal_Deployment(deployID)
    #write project metainfo to the Project CSV
    generate_emammal_Project(projPrefix,projPrefix,'2016/06/05')
    writeSequenceHeader = True  #write out header the first time only
    writeImageHeader = True  #write out header the first time only

    #get one file, get its folder, walk folder entries (all guaranteed to be on same day) to find series
    limit = 1
    jpegs = upload_files.get_files(auth_client,SEDGWICK,fname,0,limit) #returns list unordered, not guaranteed to have prefix
    if len(jpegs) == limit and jpegs[0].name.startswith(fname):
        #help/info from: https://docs.box.com/reference#folder-object-1
        jpeg_parent = jpegs[0].parent['id'] #get the box ID for the folder of this file
        fldr = upload_files.get_folder(auth_client,jpeg_parent) #returns folder object from box (here: parent folder)

        item_count = fldr['item_collection']['total_count'] #number of items in the folder total
   	ents = fldr['item_collection']['entries']  #this only contains 100 of the items in the folder max, if total<=100 then use it (not likely for wtb)
        items = fldr.get_items(limit=1000,offset=0) #get all of the items (File objects) in the folder
        if item_count <= 100:  #use folder metadata to check names, else use folder objects (slower)
	    items = ents
        for ent in items:
            if type(ent).__name__=='File':  #make sure that item has type boxsdk.object.file.File; it could be a Folder
                if ent['name'].startswith(fname):
                    namelist.append(ent['name'])
		    ids[ent['name']] = ent['id']
                    #entFileObj = upload_files.get_file(auth_client,ent['id']) #get the Box File object from the entity ID
        first = True
        last = None
        for name in sorted(namelist):

	    #file name format: Main_2013-10-13_14:20:40_17274.JPG

	    if first:
                series[name] = seqPrefix + '0'
	        thissplit = name.split('_')
                ts = thissplit[1] + " " + thissplit[2]
                first_in_series_tss = ts.replace('-','/') #used when series/sequence ends as tss_start
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
                seqID = series[last] #get ID of previous sequence
                #write sequence metainfo to the Sequence CSV
                generate_emammal_Sequence(deployID,seqID,first_in_series_tss,last_in_series_tss,writeSequenceHeader)
		if writeSequenceHeader:
                    writeSequenceHeader = False
                tmp = series[last].split('_')
                seriesCounter = int(tmp[len(tmp)-1])
		series[name] = seqPrefix + '{0}'.format(seriesCounter+1) #set the new sequence ID
                first_in_series_tss = ts.replace('-','/') #used when series/sequence ends as tss_start

	    #now swap in this names info for last for the next iteration and iterate
	    last = name

        if last: 
            #write the last series out (above writes are triggered on series change, there is none for last series)
            seqID = series[last] #get ID of previous sequence
            #write sequence metainfo to the Sequence CSV
            generate_emammal_Sequence(deployID,seqID,first_in_series_tss,last_in_series_tss,writeSequenceHeader)
    else:
	print 'Error, no files came back for fname:{0}'.format(fname)
        sys.exit(1)

    count = 0
    for name in sorted(namelist):
        count += 1
	if DEBUG:
            print '{0} {1}'.format(name,series[name],ids[name])
  	#parse the current name (date time string)
	thissplit = name.split('_')
        ts = thissplit[1] + " " + thissplit[2]
        #write file metainfo to the Image CSV
        generate_emammal_Image(deployID,series[name],name,ids[name],ts,writeImageHeader) #use box ID for location in box
	if writeImageHeader:
            writeImageHeader = False
        
        #download file from Box and write it to s3
        if acc and sec and bkt:
	    if not csvonly:
                fileObj = upload_files.get_file(auth_client,ids[name]) #get the Box File object from the entity ID
                upload_file_to_s3(name,bkt,acc,sec,fileIsString=fileObj.content())

    #at this point all csv files are written.  Upload them to s3
    if acc and sec and bkt:
        upload_file_to_s3('Deployment.csv',bkt,acc,sec,isText=True)
        upload_file_to_s3('Project.csv',bkt,acc,sec,isText=True)
        upload_file_to_s3('Sequence.csv',bkt,acc,sec,isText=True)
        upload_file_to_s3('Image.csv',bkt,acc,sec,isText=True)
    else: 
        print 'not uploading files to s3:  s3acc, s3sec, and/or s3bkt is not set'
    print 'processed {0} files from Box for CSV generation'.format(count)


if __name__ == '__main__':
    main()

