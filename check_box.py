'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import json, sys, argparse, csv, logging, os, time
import exifread
from datetime import datetime, timedelta
from contextlib import contextmanager
import upload_files
import ocr
from boxsdk.exception import BoxAPIException
from boxsdk.exception import BoxOAuthException
from requests.exceptions import ConnectionError
import OpenSSL
import urllib3
urllib3.disable_warnings()

DEBUG = False
fcache = {}

#timer utility
@contextmanager
def timeblock(label):
    start = time.time() #time.process_time() available in python 3
    try:
        yield
    finally:
        end = time.time()
        print ('{0} : {1:.10f} secs'.format(label, end - start))

def get_exif(fn,folder,csvFile,client,prefix,preflong,pictype,key,printAll=False):
    '''  Extract the jpeg metadata from JPG files (recursively 
	 below fn if fn is a directory) that have filenames that start with preflong 
 	 (files for which the camera location that maps to folder).
	 - csvFile is the output csv file
	 - client is the oauth handle to box
	 - folder is the directory in box
	 - pictype indicates which OCR cropping method to use to find the temperature
	 - key is the key in the map to use to access the global cache
	 Most every arg is passed to process_jpeg_file
	 printAll is just used to print debug info
    '''
    stop_tag = 'Image DateTime' #token to search for in the JPG info

    #if its a directory, walk it recursively pulling out every JPG file and checking whether has the right prefix (preflong)
    #if it does, then pull out the JPEG metadata (to write to the csvfile)
    #and pass the file along to process_jpeg_file for performing OCR on the temperature (if any) and writing to box
    if os.path.isdir(fn):
        for root, subFolders, files in os.walk(fn):
            for ele in files:
                fname = os.path.join(root, ele) #full path name
                #if ele.endswith(".JPG"):
                if ele.endswith(".JPG") and (preflong in fname):

                    #extract the photo ID from the file name
		    #filenames are IMAG0ID.JPG, IMG_ID.JPG, RCNXID.JPG for each different camera
                    if printAll:
		        print 'ele: {0}'.format(ele)
                    if ele.startswith('IMAG'):
                        idx = 4
                    elif ele.startswith('IMG_'):
                        idx = 3
                    elif ele.startswith('RCNX'):
                        idx = 3
		    else:
		        idx = ele.rindex(' ') #xxx 500.JPG
                    photo_id = ele[idx+1:len(ele)-4]
                    print 'PID: {0}, {1}'.format(ele, photo_id)
                    if printAll:
                        print 'processing {0}'.format(ele)

		    #open the JPG, read its metainformation (print it out), then send the 
		    #info on to process_jpeg_file (includes date/time taken)
                    with open(fname, 'rb') as fjpeg:
                        tags = exifread.process_file(fjpeg)
                        if printAll and DEBUG:
                            for tag in tags.keys():
                                if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):
                                    print 'Key: {0} --> value {1}'.format(tag, tags[tag])
                        try:
                            process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
                        except Exception as e:
   			    #try again
                            process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
                        except ConnectionError as e:
                            #try to get a new client and try again
                            client = upload_files.setup()
                            process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
    else:
        with open(fn, 'rb') as f:
            if printAll:
                tags = exifread.process_file(f)
            else:
                tags = exifread.process_file(f, stop_tag=stop_tag)
                if printAll:
                    print 'Key: {0}, value {1}'.format(stop_tag, tags[stop_tag])
                fname = os.path.abspath(fn)
                #prefix = 'fake_prefix'
                try:
                    process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
                except Exception as e:
   		    #try again
                    process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
                except ConnectionError as e:
                    #try to get a new client and try again
                    client = upload_files.setup()
                    process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,printAll)
		    #will just throw an exception and terminate the execution if there is an issue at this point
        if printAll:
            for tag in tags.keys():
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):
                    print "Key: %s, value %s" % (tag, tags[tag])


def process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,testing=False):
    #fname is full path and file name, key is the name of the entry in the map (sedgwick_map.json)
    #testing=True skips the box file upload step

    #get just the filename without the path
    orig_fname = fname[fname.rfind('/')+1:]

    #set timer around processing the metadata from JPG file
    with timeblock('process_JPG ({0})'.format(fname)):
        stop_tag = 'Image DateTime'
        dt_tag = vars(tags[stop_tag])['printable']
        flash = 'NoFlash'
        stop_tag = 'EXIF Flash'
        fmsg = vars(tags[stop_tag])['printable']
        if 'Flash fired' in fmsg:
            flash = 'Flash'

        #dt_tag: 2014:08:01 19:06:50
        d = (dt_tag.split()[0]).replace(':','-')
        t = dt_tag.split()[1]

    day_folder = None  #set either from cache (fast) or by going to box (slow)
    folder_name = prefix

    #check folder, create if needed
    splitd = d.split('-')
    yr = splitd[0]
    mo = splitd[1]
    dy = splitd[2]
    nody = '00'
    if DEBUG:
        print 'yr: {0}, mo: {1}, dy: {2}, foldername: {3}'.format(yr,mo,dy,folder_name)

    if not testing: #none of this is needed if we aren't uploading to box
        folder_name = folder['name']
        global fcache  #we are going to update it so make it global, key is
        #fcache contains one dictionary for each unique key_yr_mo, key is location prefix, e.g. "Lisque"

        cache_key = '{0}_{1}_{2}'.format(key,yr,mo) # one dictionary per month
        if cache_key not in fcache:
            #dictionary flist contains name=folder_obj pairs where name is 
	    #day string, folder_obj is box folder once created
            flist = {} 
            fcache[cache_key] = flist
        else: 
            flist = fcache[cache_key]
        #regardless of path above, we have a valid flist at this point for this year and month

        if dy in flist: #check if dy is a key in the dictionary, if so, get the folder
	    day_folder = flist[dy]
	    day_folder_name = day_folder.get()['name']
        elif nody in flist:
            #yr_mo_day is not in the cache for this location 
	    #if yr_mo_0 is (no days created yet), then use it to create dy folder
	    mo_folder = flist['0']
	    day_folder = mo_folder.create_subfolder(dy)
            flist[dy] = day_folder
	    day_folder_name = day_folder.get()['name']
        #else, we need to create the year and month folder or just the month folder, 
        #leaving day_folder None will trigger this lookup
        
        if day_folder is None:
            with timeblock('checkOrCreateFolder_BOX'):
                #check if there is a directory called yr in the folder, if not make it
                items = folder.get_items(limit=100, offset=0)
                for ikey in items:
                    yrf = ikey.get()
                    if yr == yrf['name']:
                        #found the year folder, check for the month folder
                        moitems = yrf.get_items(limit=100,offset=0)
                        if moitems is not None:
                            for mokey in moitems:
                                mof = mokey.get()       
                                if mo == mof['name']:
                                    #found the month folder, check for the day folder
                                    dyitems = mof.get_items(limit=100,offset=0)
                                    if dyitems is not None:
                                        for dykey in dyitems:
                                            dyf = dykey.get()       
                                            if dy == dyf['name']:
                                                #found the day folder, cache it
			                        day_folder = dyf
        				        flist[dy] = day_folder
                                                break #out of dykey loop, we have the folder
                                        if day_folder is not None: #we have the folder
                                            break #out of mokey loop
    
                                    #create day folder here: dyitems is None 
                                    #or loop completed without setting day_folder
                                    day_folder = mof.create_subfolder(dy)
        			    flist[dy] = day_folder #cache it
                                    break
            
                        #outside fo mof loop, day_folder has been found 
		        #or has been created if mof was found. 
                        #if neither of the above occured, it will be None here
                        if day_folder is None: #create it
                            mo_folder = yrf.create_subfolder(mo)
                            day_folder = mof.create_subfolder(dy)
        	            flist[dy] = day_folder #cache it
                        break #out of ikey (yr) loop b/c we have a day_folder
            
            #if we reach here, yr folder was not found, create a year, month and day folder 
            if day_folder is None:
                yr_folder = folder.create_subfolder(yr)
                mo_folder = yr_folder.create_subfolder(mo)
                day_folder = mo_folder.create_subfolder(dy)
                flist[dy] = day_folder #cache it
            day_folder_name = day_folder.get()['name']
        
        assert day_folder is not None
        assert day_folder_name is not None

        if DEBUG:
            print 'day folder name {0}'.format(day_folder_name)

    #upload file to box day_folder or elsewhere
    newfname = '{0}_{1}_{2}_{3}.JPG'.format(prefix,d,t,photo_id)
    if DEBUG:
        print 'filename to ship: {0} remote fname: {1}'.format(
            fname,newfname)

    temp = None
    err = 'TESTING'
    if not testing:
        #upload to box
        with timeblock('upload_BOX'):
            upload_files.runit(fname,day_folder,client,newfname)

    else: 
        print 'process_jpeg: skipping upload for testing purposes'

    #process image via OCR to get temperature 
    with timeblock('perform_OCR'):
        temp,err,_,_ = ocr.process_pic(pictype, fname)
    
    if temp is None and not testing:
        print 'Error in process_pic call, temp is None'
    check_temp = err

    #store metainfo in the csv file
    sz = os.path.getsize(fname) #size in bytes
    newfname = '{0}\{1}\{2}\{3}:{4}'.format(folder_name,yr,mo,dy,newfname) #rewrite it to include folder name
    if DEBUG:
        print '{1},{2},{3},{4},{5},{6},{7},{8}'.format( 
            newfname, d, t, photo_id, sz, temp, flash, check_temp,orig_fname)
    meta = (newfname,d,t,photo_id,sz,temp,flash,check_temp,orig_fname)
    #append meta to csv file
    csvFile.writerow(meta)


def writeIntro(csvFile):
    csvFile.writerow(('box_path:filename','date','time','ID','size','temp','flash','bad_temp','orig_fname'))

######################## main ############################
def process_local_dir(fn,folder,csvFile,client,prefix,preflong,pictype,key,matchlist,uploadIt):
    for root, subFolders, files in os.walk(fn):
        for ele in files:
            fname = os.path.join(root, ele) #full path name
            if ele.endswith(".JPG") and (preflong in fname):
                orig_fname = fname[fname.rfind('/')+1:]

                #extract the photo ID from the file name
	        #filenames are IMAG0ID.JPG, IMG_ID.JPG, RCNXID.JPG for each different camera
                if ele.startswith('IMAG'):
                    idx = 4
                elif ele.startswith('IMG_'):
                    idx = 3
                elif ele.startswith('RCNX'):
                    idx = 3
		else:
		    idx = ele.rindex(' ') #xxx 500.JPG
                photo_id = ele[idx+1:len(ele)-4]
                if DEBUG:
                    print 'processing: {0}, {1}'.format(ele, photo_id)

		#open the JPG, read its metainformation to construct name
		tags = None
                with open(fname, 'rb') as fjpeg:
                    tags = exifread.process_file(fjpeg)
                stop_tag = 'Image DateTime'
                dt_tag = vars(tags[stop_tag])['printable']
                #dt_tag: 2014:08:01 19:06:50
                d = (dt_tag.split()[0]).replace(':','-')
                t = dt_tag.split()[1]
		#now we have the file name used to store this file in box
                newfname = '{0}_{1}_{2}_{3}.JPG'.format(prefix,d,t,photo_id)
		#check to see if it is in box, if not, print out the name to stdout
                testing = True #don't upload it to box
		if newfname not in matchlist:
                    testing = not uploadIt  #upload if missing and uploadIt is True
		    print 'missing:{0}:{1}'.format(orig_fname,newfname)
                #process the file and generate the CSV, only upload to box according to testing
		process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,testing)


######################## process_box_folder ############################
def process_box_folder(folder,deleteIt):

    #folder is a camera folder, loop through year folders, then through month and day folders
    #check to make sure that the file name in box matches the directory structure
    #delete any files that don't match if they are files and if deleteIt is True
    #return list of matched filenames if any

    matchlist = []
    yearfolders = folder.get_items(limit=10, offset=0) #max sb < 10
    if DEBUG: 
        print 'Folder: {0}'.format(folder['name'])
        print '{0} year folders'.format(len(yearfolders))
    camera = folder['name']
    for yr in yearfolders:
      if type(yr).__name__=='Folder':  
            mofolders = yr.get_items(limit=13,offset=0) #max sb 12
            if DEBUG: 
                print '{0} month folders'.format(len(mofolders))
            for mo in mofolders:
                if type(mo).__name__=='Folder':  
                    dayfolders = mo.get_items(limit=32,offset=0) #max sb < 32
                    if DEBUG: 
                        print '{0} day folders'.format(len(dayfolders))
                        if len(dayfolders) == 0:
                            print '{0}_{1}_?: 0'.format(yr['name'],mo['name'])
                    count = 0
                    for dy in dayfolders:
                        if type(dy).__name__=='Folder':  
                            prefix = '{0}_{1}-{2}-{3}_'.format(
                                camera,yr['name'],mo['name'],dy['name'])
                            lim = 1000
                            oset = 0
                            files = dy.get_items(limit=lim,offset=oset) #max unknown
                            count = len(files)
                            while len(files) > 0:
                                for f in files:
				    if type(f).__name__=='File' and f['name'].startswith(prefix):
                                        matchlist.append(f['name'])
				    else:
					#found a file that doesn't below, or a directory
                                        print 'DELETING {0}_{1}_{2}: {3}'.format(yr['name'],mo['name'],dy['name'],f['name'])
					if deleteIt:
                                            f.delete()

                                oset += lim
                                files = dy.get_items(limit=lim,offset=oset) #max unknown
                                count += len(files)
                        print '{0}_{1}_{2}: {3}'.format(yr['name'],mo['name'],dy['name'],count)
    return matchlist

######################## main ############################

def main():
    global DEBUG
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Check/clean Box directories: remove/report any files that do not match')
    parser.add_argument('imgdir',action='store',default=None,help='(local) Parent directory with camera folders and JPG files')
    parser.add_argument('csvfn',action='store',help='CSV output filename prefix (one per camera)')
    parser.add_argument('map',action='store',help='json map filename with Box directories to check')
    #json map format: "Lisque": ["7413964473","Lisque Mesa 1"],
    #			prefix	     ID	    actual fname prefix

    #optional arguments
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    parser.add_argument('--delete',action='store_true',default=False,help='Turn deletion of box files on, just report if off (default)')
    parser.add_argument('--checkmatches',action='store',default=None,help='Compare box list with files in the directory passed in to this argument')
    args = parser.parse_args()
    DEBUG = args.debug

    #read in the map
    with open(args.map,'r') as map_file:    
        '''
	mymap keys are location prefix names, values are lists of strings.
	The list contains three elements: (1) box_folder_id of root/parent folder, 
	(2) the full prefix of the original file name (this allows us to skip files that don't belong to the location)
	and (3) the pictype (type of picture indicating the parameter (camera identifier)
	for OCR of the temperature value in the image.
	'''
        mymap = json.loads(map_file.read())

    auth_client = None
    #log into Box
    auth_client = upload_files.setup()

    for key in mymap: 

        #key is the location prefix specified in the config file
        val = mymap[key] #list of three strings
        myfolder_id = val[0] #folder ID cut/pasted from box after creating 
        #the folder manually (its in the URL when in folder in box)
        prefix = key
        full_prefix = val[1] #used to check if a file belongs to this folder/key
        if DEBUG:
            print '{0}: {1}: {2}'.format(myfolder_id,prefix,full_prefix)
        folder = None
        try: 
            folder = auth_client.folder( folder_id=myfolder_id, ).get()
        except BoxOAuthException as e:
            print e
            print 'Unable to open primary folder, retrying auth... '
            try:
                auth_client = upload_files.setup()
                folder = auth_client.folder( folder_id=myfolder_id, ).get()
            except Exception as e:
                print e
                print 'Unable to open primary folder, check your tokens and Box service!'
                return

        if folder: 
            matchlist = process_box_folder(folder,args.delete)
            if DEBUG:
                print 'matchlist length: {0}'.format(len(matchlist))

            if args.checkmatches:
                #open the csv file for writing out the metainformation per JPG file
                csvfname = '{0}_{1}.csv'.format(prefix,args.csvfn)
                with open(csvfname,'wt') as f:
                    csvFile = csv.writer(f)
                    writeIntro(csvFile)

	            #next, process the directory passed in to upload what doesn't match
                    process_local_dir(args.imgdir,folder,csvFile,auth_client,prefix,full_prefix,pictype,key,matchlist,False) #change last arg to True to upload missing files to box, False skips upload for testing purposes

if __name__ == '__main__':
    main()
