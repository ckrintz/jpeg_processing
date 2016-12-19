'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import json, sys, argparse, csv, logging, os, time
from datetime import datetime, timedelta
from contextlib import contextmanager

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
    parser = argparse.ArgumentParser(description='Process the output file from: python2.7 pick_random_images.py --skip ../photos2/ sedgwick_map.json pick.out > imagelist.out')
    parser.add_argument('fname',action='store',default=None,help='filename to process')
    parser.add_argument('map',action='store',help='json map filename')
    #optional arguments
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    args = parser.parse_args()
    DEBUG = args.debug

    #read in the map
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

    for key in mymap: 
        daypics = 0
	daypics_size = 0
        totalpics = 0
	totalsize = 0
        days_with_images = {}
        #process the file
        with open(args.fname,'r') as f:    
            for line in f:
                eles = line.split(';')
                val = mymap[key] #list of three strings, second one is full prefix
                full_prefix = val[1] #used to check if a file belongs to this folder/key
                if eles[0] == 'CJK':
                    #CJK;2015:11:08 23:08:55;1417293;../photos2/2015 - 2016 Sedgwick Pictures/Windmill Canyon 1 (4-03-2015 to 12-29-2015)/Windmill Canyon 1 11-06-2015 to 12-08-2015/100HCOIM/IMAG0091.JPG
                    if full_prefix in eles[3]: # this entry is an image from this key's camera
	                dtime = datetime.strptime(eles[1], '%Y:%m:%d %H:%M:%S')
			days_with_images[dtime.date()] = 1
			starttime = datetime.strptime('2016:08:01 09:00:00','%Y:%m:%d %H:%M:%S')
			endtime = datetime.strptime('2016:08:01 16:00:00','%Y:%m:%d %H:%M:%S')
			if dtime.time() >= starttime.time() and dtime.time() <= endtime.time(): #day
			    daypics += 1
			    daypics_size += long(eles[2])
                        totalpics += 1
                        totalsize += long(eles[2])
        print '{0}: totalpics {1}, daypics {2}, totaldays {3}, daysize {4}, totalsize {5}'.format(key,totalpics,daypics,len(days_with_images),daypics_size,totalsize)


##################################
if __name__ == '__main__':
    main()
