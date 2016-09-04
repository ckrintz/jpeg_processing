'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

'''
USAGE: python2.7 jpeg_processor.py --newocr --noupload ../photos2/ sedgwick_map.json noupload_all2.csv >& jpp_noupload.out 
or

USAGE: python2.7 check_box.py mainCJK mymap.json --debug --delete --checkmatches ../photos2/ --matchlist mainCJK_matchlist.txt
        - reads in mymap.json for list of box directory to consider
        - performs handshake with box API to setup access (upload_files.py)
        - for each entry in the json file do the following:
                - get the parent folder for the camera location in box (ID is in json file)
                - check each file in box to make sure it is in the right directory.  Delete it (--delete) if it is not.
                - generate a list of files in the box hierarchy below this folder
                        - called matchlist
                        - there are two options for generation of matchlist
                                - read it in (--matchlist arg) from a previously generated run
                                - or call process_box_folder on the folder (more on this below)
                        - save off the matchlist to the same file name as the one passed in if any
        - loop through each JPG file (for this camera) in the local directory passed in (checkmatches argument)
                - if the file is not in matchlist, upload it (jpeg_processor.py,upload_files.py) to box in the right directory
                - call validation_problem in jpeg_processor.py to verify the directory is correct, exit upon error (bug!)
	- Dumps progress and details to stdout (--debug)
'''

import json, sys, argparse, csv, logging, os, time
import exifread
from datetime import datetime, timedelta
from contextlib import contextmanager
import upload_files
import ocr,crop_and_recognize
from boxsdk.exception import BoxAPIException
from boxsdk.exception import BoxOAuthException
from requests.exceptions import ConnectionError
import OpenSSL
import urllib3
urllib3.disable_warnings()

DEBUG = False
fcache = {}
newocr = False

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
                    elif ele.startswith('MFDC'):
                        idx = 3
			'''
			#this is a new Vulture Trough camera, change the pictype from 2 to TBD
			if 'Vulture Trough' in preflong:
			    #pictype = TBD
			    print 'Error: new Vulture Trough pictype not yet supported (skipping) (MFDC): {0}'.format(fname)
			    continue
			else: 
			    print 'Error: cannot process this filename (MFDC): {0}'.format(fname)
			    continue
			'''
		    else:
		        idx = ele.rindex(' ') #xxx 500.JPG
                    photo_id = ele[idx+1:len(ele)-4]
                    #print 'PID: {0}, {1}'.format(ele, photo_id)
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

def validation_problem(folder, fileName):
    #check that folder hierarchy (foldername, parent foldername, grandparent foldername, greatgrandparent folder name) matches that of the fileName
    parname = folder['name']
    col = folder['path_collection']
    pathlen = col['total_count']
    dirary = col['entries']
    prefix = '{0}_{1}-{2}-{3}'.format(
        dirary[pathlen-3]['name'], #camera
        dirary[pathlen-2]['name'], #year
        dirary[pathlen-1]['name'], #month
        parname #day
        )
    if not fileName.startswith(prefix):
        print 'Error in validation of box and filename: {0}:{1}'.format(fileName,prefix)
	return True
    else:
        print 'Box validation passed: {0}:{1}'.format(fileName,prefix)
    return False

def process_jpeg_file(tags,fname,csvFile,folder,prefix,client,pictype,photo_id,key,testing=False):
    #fname is full path and file name, key is the name of the entry in the map (sedgwick_map.json)
    #testing=True skips the box file upload step

    #get just the filename without the path
    orig_fname = fname[fname.rfind('/')+1:]

    wid_tag = 0
    len_tag = 0
    #set timer around processing the metadata from JPG file
    with timeblock('process_JPG ({0})'.format(fname)):
        stop_tag = 'Image DateTime'
        dt_tag = vars(tags[stop_tag])['printable']
        flash = 'NoFlash'
        stop_tag = 'EXIF Flash'
        fmsg = vars(tags[stop_tag])['printable']
        if 'Flash fired' in fmsg:
            flash = 'Flash'
        stop_tag = 'EXIF ExifImageWidth'
        wid_tag = vars(tags[stop_tag])['printable']
        stop_tag = 'EXIF ExifImageLength'
        len_tag = vars(tags[stop_tag])['printable']
        #print 'Filename: {0}, datetime {1}, res {2}x{3}, pictype {4}'.format(fn,dt_tag,wid_tag,len_tag,pictype)

        #dt_tag: 2014:08:01 19:06:50
        d = (dt_tag.split()[0]).replace(':','-')
        t = dt_tag.split()[1]

    if wid_tag ==0 or len_tag ==0:
	print 'Error: JPG processing has failed for {0}'.format(fname)
	sys.exit(1)

    day_folder = None  #set either from cache (fast) or by going to box (slow)
    day_folder_name = None  #set either from cache (fast) or by going to box (slow)
    folder_name = prefix

    #check folder, create if needed
    splitd = d.split('-')
    yr = splitd[0]
    mo = splitd[1]
    dy = splitd[2]
    nody = '00'
    if DEBUG:
        print 'yr: {0}, mo: {1}, dy: {2}, foldername: {3}, testing: {4}'.format(yr,mo,dy,folder_name,testing)

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
        #if DEBUG:
        print 'cache_key: {0}'.format(cache_key)

        if dy in flist: #check if dy is a key in the dictionary, if so, get the folder
            print 'day in flist: {0}'.format(dy)
	    day_folder = flist[dy]
	    try:
	        day_folder_name = day_folder.get()['name']
            except Exception as e:
                print e
                print 'retrying1'
	        day_folder_name = day_folder.get()['name']
        elif nody in flist:
            print 'nody (no yr_mo_day) in flist'
            #yr_mo_day is not in the cache for this location 
	    #if yr_mo_0 is (no days created yet), then use it to create dy folder
	    mo_folder = flist['0']
	    day_folder = mo_folder.create_subfolder(dy)
            flist[dy] = day_folder
  	    try:
	        day_folder_name = day_folder.get()['name']
            except Exception as e:
                print e
                print 'retrying2'
	        day_folder_name = day_folder.get()['name']
        #else, we need to create the year and month folder or just the month folder, 
        #leaving day_folder None will trigger this lookup
        
        if day_folder is None:
            with timeblock('checkOrCreateFolder_BOX'):
                #check if there is a directory called yr in the folder, if not make it
                try:
                    items = folder.get_items(limit=100, offset=0)
                except Exception as e:
                    print e
                    print 'retrying3'
                    items = folder.get_items(limit=100, offset=0)
                for ikey in items:
                    try:
                        yrf = ikey.get()
                    except Exception as e:
                        print e
                        print 'retrying4'
                        yrf = ikey.get()
                    if yr == yrf['name']:
                        #found the year folder, check for the month folder
                        try:
                            moitems = yrf.get_items(limit=100,offset=0)
                        except Exception as e:
                            print e
                            print 'retrying5'
                            moitems = yrf.get_items(limit=100,offset=0)
                        if moitems is not None:
                            for mokey in moitems:
                                try:
                                    mof = mokey.get()       
                                except Exception as e:
                                    print e
                                    print 'retrying6'
                                    mof = mokey.get()       
                                if mo == mof['name']:
                                    #found the month folder, check for the day folder
				    try:
                                        dyitems = mof.get_items(limit=100,offset=0)
                                    except Exception as e:
                                        print e
                                        print 'retrying7'
                                        dyitems = mof.get_items(limit=100,offset=0)
                                    if dyitems is not None:
                                        for dykey in dyitems:
                                            try:
                                                dyf = dykey.get()       
                                            except Exception as e:
                                                print e
                                                print 'retrying8'
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
                            mof = yrf.create_subfolder(mo)
                            day_folder = mof.create_subfolder(dy)
        	            flist[dy] = day_folder #cache it
                        break #out of ikey (yr) loop b/c we have a day_folder
            
            #if we reach here, yr folder was not found, create a year, month and day folder 
            if day_folder is None:
                yr_folder = folder.create_subfolder(yr)
                mof = yr_folder.create_subfolder(mo)
                day_folder = mof.create_subfolder(dy)
                flist[dy] = day_folder #cache it
            try:
                day_folder_name = day_folder.get()['name']
            except Exception as e:
                print e
                print 'retrying9'
                day_folder_name = day_folder.get()['name']
        
        assert day_folder is not None
        assert day_folder_name is not None


    #upload file to box day_folder or elsewhere
    newfname = '{0}_{1}_{2}_{3}.JPG'.format(prefix,d,t,photo_id)

    if DEBUG:
        print 'filename to ship: {0} remote fname: {1}'.format(fname,newfname)
    
    temp = None
    err = False #no error
    if not testing:
        if DEBUG:
            print 'day folder name {0}'.format(day_folder_name)
        #verify that we have it right
        with timeblock('validate_BOX_folder'):
            if validation_problem(day_folder, newfname):
                sys.exit(1)

        #upload to box
        with timeblock('upload_BOX'):
            upload_files.runit(fname,day_folder,client,newfname)

    else: 
        print 'process_jpeg: skipping upload for testing purposes'

    #process image via OCR to get temperature 
    with timeblock('perform_OCR'):
        if not newocr: #err is a boolean, False if there was an issue
            temp,err,_,_ = ocr.process_pic(pictype, fname)
            print 'OrigOCR: Temp is: {0}'.format(temp)
        else:
            print 'Using newocr, image name is: {0}'.format(fname)
            #wid_tag x len_tag
            err = False # no error
	    try:
	        if int(wid_tag) == 2560 and int(len_tag) == 1920: #Windmill1, UpperRes no temp
		    temp = -9998 #no temp
	        elif int(wid_tag) == 3264 and int(len_tag) == 2448: #Windmill1 2014, BoneT
                    temp = crop_and_recognize.run_c1(fname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_1/')
	        elif int(wid_tag) == 1920 and int(len_tag) == 1080: #main,lisque,fig,ne,vulture_pre16
                    temp = crop_and_recognize.run_c2(fname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_2/')
	        elif int(wid_tag) == 3776 and int(len_tag) == 2124: #boneH
                    temp = crop_and_recognize.run_c3(fname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_3/')
	        elif int(wid_tag) == 2688 and int(len_tag) == 1512: #vulture16
		    temp = -9997 #TBD rerun these when supported
		    err = True #error
	        elif int(wid_tag) == 2048 and int(len_tag) == 1536: #windmillG,blue
		    temp = -9997 #TBD rerun these when supported
		    err = True #error
	        else:
		    print 'Error: unsupported OCR resolution: {0}x{1}'.format(wid_tag,len_tag)
		    temp = -9996
		    err = True #error
            except Exception as e:
		    print e
		    print 'Error: OCR exception for: {0}x{1}'.format(wid_tag,len_tag)
		    temp = -9995
		    err = True #error
            print "NewOCR: Temp is: {0}".format(temp)

    
    check_temp = err
    if temp is None:
        print 'Unknown Error in OCR call, temp is None'
        temp = -9999
        check_temp = True

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


def main():
    global newocr
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='JPEG Processing')
    #required arguments
    parser.add_argument('img',action='store',help='JPEG image, if Directory, will walk it recursively to find all *.JPG below and process them')
    parser.add_argument('map',action='store',help='json map filename')
    #json map format: "Lisque": ["7413964473","Lisque Mesa 1"],
    #			prefix	     ID	    actual fname prefix
    parser.add_argument('csvfn',action='store',help='CSV output filename')
    #optional arguments
    parser.add_argument('--debug',action='store',default=False,type=bool,help='Turn debugging on')
    parser.add_argument('--newocr',action='store_true',default=False,help='Use Andys OCR')
    parser.add_argument('--noupload',action='store_true',default=False,help='Turn uploading to box off')
    args = parser.parse_args()
    testing = args.noupload
    newocr = args.newocr

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
    if not testing:
        #log into Box
        auth_client = upload_files.setup()

    #open the csv file for writing out the metainformation per JPG file
    with open(args.csvfn,'wt') as f:
        csvFile = csv.writer(f)
        writeIntro(csvFile)
        #For each entry in the map (camera location, process the directory 
	#passed in looking for JPG files from that camera (prefix))
        for key in mymap: #key is passed through to process_jpeg_file

            #key is the location prefix specified in the config file
            val = mymap[key] #list of three strings
            myfolder_id = val[0] #folder ID cut/pasted from box after creating 
	    #the folder manually (its in the URL when in folder in box)
            prefix = key
            full_prefix = val[1] #used to check if a file belongs to this folder/key
            pictype = int(val[2]) #passed through to OCR
            if DEBUG:
                print '{0}: {1}: {2}'.format(myfolder_id,prefix,full_prefix)

            folder = None
	    if not testing:
                #get the box folder object for the parent (camera location) folder
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
    	    else: 
                #set last param (testing/printAll) to True if you don't want to write to box 
	        #but want to see the jpeg info per file (generate the metadata for csv file)
	        print 'testing is set to True: Not uploading to box. Prefix {0}'.format(prefix)

            #process the file or directory, outputing metainformation to the csvfile 
            get_exif(args.img,folder,csvFile,auth_client,prefix,full_prefix,pictype,key,testing)

if __name__ == '__main__':
    main()
