'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import json, sys, argparse, csv, logging, os, time
import exifread
from datetime import datetime, timedelta
from contextlib import contextmanager
from boxsdk.exception import BoxAPIException
from boxsdk.exception import BoxOAuthException
from requests.exceptions import ConnectionError
import OpenSSL
import urllib3
urllib3.disable_warnings()
import upload_files, jpeg_processor, ocr

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

######################## process_local_dir ############################
def process_local_dir(fn,prefix,preflong,pictype):
    size = 0
    count = 0
    for root, subFolders, files in os.walk(fn):
        for ele in files:
            fname = os.path.join(root, ele) #full path name
            if ele.endswith(".JPG") and (preflong in fname):
                size += os.path.getsize(fname)
		count += 1
    return size,count


######################## main ############################
def main():
    global DEBUG
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Find all of the pictures under each camera prefix is map and count them')
    parser.add_argument('imgdir',action='store',help='Directory')
    parser.add_argument('map',action='store',help='json map filename with Box directories to check')
    #json map format: "Lisque": ["7413964473","Lisque Mesa 1"],
    #			prefix	     ID	    actual fname prefix

    #optional arguments
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
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

    szsum = 0
    cntsum = 0
    for key in mymap: 

        #key is the location prefix specified in the config file
        val = mymap[key] #list of three strings
        myfolder_id = val[0] #folder ID cut/pasted from box after creating 
        #the folder manually (its in the URL when in folder in box)
        prefix = key
        full_prefix = val[1] #used to check if a file belongs to this folder/key
        pictype = int(val[2]) #index indicating which OCR to use
        if DEBUG:
            print '{0}: {1}: {2}'.format(myfolder_id,prefix,full_prefix)

        #next, process the directory passed in to upload what doesn't match
        sz,cnt = process_local_dir(args.imgdir,prefix,full_prefix,pictype)
        print '{0}: size_in_KB: {1} count: {2} avgsize_in_KB: {3}'.format(prefix,sz/1024,cnt,(sz/cnt)/1024)
        szsum += sz
        cntsum += cnt
    print 'TOTAL: size_in_KB: {0} count: {1} avgsize_in_KB: {2}'.format(szsum/1024,cntsum,(szsum/cntsum)/1024)

##################################
if __name__ == '__main__':
    main()
