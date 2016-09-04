'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

'''
USAGE: python2.7 csvtest.py noupload_all2.csv ../photos2/ sedgwick_map.json
#noupload_all2.csv comes from jpeg_processor.py
'''

import json, sys, argparse, csv, logging, os, time
import exifread
from datetime import datetime, timedelta
from contextlib import contextmanager
DEBUG = False
#timer utility
@contextmanager
def timeblock(label):
    start = time.time() #time.process_time() available in python 3
    try:
        yield
    finally:
        end = time.time()
        print ('{0} : {1:.10f} secs'.format(label, end - start))

def main():
    global newocr
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='compare entries in csv file against those found in the directory passed in')
    #required arguments
    parser.add_argument('csvfn',action='store',help='csv file containing rows of col1=box_path:filename')
    parser.add_argument('dirname',action='store',help='image directory')
    parser.add_argument('map',action='store',help='prefix filename json map')
    parser.add_argument('--countonly',action='store_true',default=False,help='count number of files under dir only')
    args = parser.parse_args()

    #read in the prefix map
    with open(args.map,'r') as map_file:    
        '''
	mymap keys are location prefix names, values are lists of strings.
	The list contains three elements: (1) box_folder_id of root/parent folder, 
	(2) the full prefix of the original file name (this allows us to skip files that don't belong to the location)
	and (3) the pictype (type of picture indicating the parameter (camera identifier)
	for OCR of the temperature value in the image.
	'''
        mymap = json.loads(map_file.read())

    prefix_dict = {}
    for key in mymap:
        val = mymap[key] #list of three strings
        full_prefix = val[1] #used to check if a file belongs to this folder/key
	prefix_dict[full_prefix] = key


    #construct a dict from the csv: filename as key. filename format: Windmill_2016-04-23_15:23:43_1338.JPG
    namelist = []
    namedict = {}
    with open(args.csvfn,'rt') as f:
        csvFile = csv.reader(f,delimiter=',')
	for row in csvFile:
	    name = row[0]
	    name = name.split(':',1)[1]
	    #                date, time, size, orig_fname
	    namedict[name] = {'date':row[1],'time':row[2],'size':row[4],'orig_fname':row[8]}
    namedict_count = len(namedict)
    count = 0
    notfoundcount = 0
    if args.countonly:
        for pref in prefix_dict:
	    print pref

    print 'Starting directory search'
    #loop through files in directory, construct name, see if name is in the map
    if os.path.isdir(args.dirname):
        for root, subFolders, files in os.walk(args.dirname):
            for ele in files:
                fname = os.path.join(root, ele) #full path name
                if ele.endswith(".JPG"):
		    if args.countonly:
                        count += 1
			if count % 100 == 0:
			    print 'counting... {0}'.format(count)
                        found = False
		        for pref in prefix_dict:
                            if pref in fname:
				found = True
			if not found:
			    print 'not found: {0}'.format(fname)
		        continue
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

		    #open the JPG, read its metainformation (print it out), then send the 
		    #info on to process_jpeg_file (includes date/time taken)
                    with open(fname, 'rb') as fjpeg:
                        tags = exifread.process_file(fjpeg)
                        tag = vars(tags['Image DateTime'])['printable']
			d = tag.split(' ',1)[0].replace(':','-')
			t = tag.split(' ',1)[1]
		    sz = os.path.getsize(fname)
                    found = False
		    for pref in prefix_dict:
                        if pref in fname:
			    if found: #already found?
				print 'Error, found an fname with 2 prefixes: {0}'.format(fname)
				sys.exit(1)
			    found = True
			    pref = prefix_dict[pref]
			    newfname = '{0}_{1}_{2}_{3}.JPG'.format(pref,d,t,photo_id)
                            try:
		 	        flist = namedict[newfname]
			    except Exception as e:
				print e
				print 'Error, missing fname: {0}'.format(newfname)
                                notfoundcount += 1
                                continue

			    if int(flist['size']) == int(sz) and flist['orig_fname'] == ele:
				count += 1
                            else: 
				print 'Error, missing2 fname: {0}'.format(newfname)
				print 'orig sz: {0}, new sz: {1}, True_if_Same: {2}'.format(flist['size'],sz,(flist['size']==sz))
				print 'orig name: {0}, new name: {1}, True_if_Same: {2}'.format(flist['orig_fname'],ele,(flist['orig_fname']==ele))
                                notfoundcount += 1
		    if not found:
			print 'Error, missing3 fname (no prefix match): {0}'.format(fname)
                        notfoundcount += 1

    else: 
        print 'Error: second parameter must be a directory: {0}'.format(args.dirname)

    print 'Name_dict_count: {0}, found: {1}, notfound: {2}, f+nf: {3}'.format(namedict_count, count, notfoundcount, (count+notfoundcount))


if __name__ == '__main__':
    main()
