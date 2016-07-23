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
######################## timer utility ############################
@contextmanager
def timeblock(label):
    start = time.time() #time.process_time() available in python 3
    try:
        yield
    finally:
        end = time.time()
        print ('{0} : {1:.10f} secs'.format(label, end - start))

######################## writeIntro ############################
def writeIntro(csvFile):
    csvFile.writerow(('box_path:filename','date','time','ID','size','temp','flash','bad_temp','orig_fname'))

######################## process_local_dir ############################
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

##################################
if __name__ == '__main__':
    main()
