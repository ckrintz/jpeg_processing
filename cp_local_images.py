'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import random,argparse,json,os,sys,time,exifread
from datetime import datetime, timedelta
from contextlib import contextmanager
from shutil import copyfile
import exifread
import subprocess

DEBUG = False
local = False
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
def process_local_dir(srcdir,destdir,prefix,preflong,pictype):
    size = 0
    count = 0
    for root, subFolders, files in os.walk(srcdir):
        for ele in files:
            fname = os.path.join(root, ele) #full path name
            if ele.endswith(".JPG") and (preflong in fname):
                if ele.startswith('IMAG'):
                    idx = 4
                elif ele.startswith('IMG_'):
                    idx = 3
                elif ele.startswith('RCNX'):
                    idx = 3
                elif ele.startswith('MFDC'):
                    idx = 3
		else:
		    idx = ele.rindex(' ') #xxx 500.JPG
                photo_id = ele[idx+1:len(ele)-4]
                with open(fname, 'rb') as fjpeg:
                    tags = exifread.process_file(fjpeg)
                stop_tag = 'Image DateTime'
                dt_tag = vars(tags[stop_tag])['printable']
                #dt_tag: 2014:08:01 19:06:50
                d = (dt_tag.split()[0]).replace(':','-')
                t = dt_tag.split()[1]
		#directory name YYYYMM
                ddir = datetime.strptime(dt_tag.split()[0], "%Y:%m:%d").strftime('%Y%m')
                newfname = '{0}_{1}_{2}_{3}.jpg'.format(prefix,d,t,photo_id)
		if os.path.exists(newfname):
                    print '{0} exists! not overwriting'
		    continue
                size += os.path.getsize(fname)
		count += 1
		if local:
                    copyfile(fname, newfname) #works locally
		else: 
		    fn = fname.replace(' ','\ ')
		    fn = fn.replace('(','\(')
		    fn = fn.replace(')','\)')
		    cmd = 'rsync -az {0} root@169.231.235.115:/tmp/{1}'.format(fn,newfname)
		    if DEBUG:
			print 'command: {0} {1} {2}'.format(cmd,fn,newfname)
		    os.system(cmd)

    return size,count


######################## main ############################
def main():
    global DEBUG,local
    parser = argparse.ArgumentParser(description='Find all of the pictures under each camera prefix is map and count them')
    parser.add_argument('srcdir',action='store',help='Directory')
    parser.add_argument('destdir',action='store',help='Directory')
    parser.add_argument('map',action='store',help='json map filename that holds which prefixes to copy')
    #json map format: "Lisque": ["7413964473","Lisque Mesa 1"],
    #			prefix	     ID	    actual fname prefix

    #optional arguments
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    parser.add_argument('--local',action='store_true',default=False,help='if False (default), nothing is copied... only counting is performed')
    args = parser.parse_args()
    DEBUG = args.debug
    local = args.local

    #read in the map
    with open(args.map,'r') as map_file:    
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

        #process srcdir and copy any JPG from the camera identified by the key
        sz,cnt = process_local_dir(args.srcdir,args.destdir,prefix,full_prefix,pictype)
        if cnt != 0:
            print 'Copied {0}: size_in_KB: {1} count: {2} avgsize_in_KB: {3}'.format(prefix,sz/1024,cnt,(sz/cnt)/1024)
        else:
	    print 'Copied {0}: nothing'.format(prefix)
        szsum += sz
        cntsum += cnt
    if cntsum != 0:
        print 'TOTAL Copied: size_in_KB: {0} count: {1} avgsize_in_KB: {2}'.format(szsum/1024,cntsum,(szsum/cntsum)/1024)
    else:
	 print 'TOTAL Copied {0}: nothing'.format(prefix)

##################################
if __name__ == '__main__':
    main()
