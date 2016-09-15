'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import random,argparse,json,os,sys,time
import exifread
from contextlib import contextmanager

DEBUG = False
total = 0
count = 0
######################## timer utility ############################
@contextmanager
def timeblock(label):
    global total,count
    start = time.time() #time.process_time() available in python 3
    try:
        yield
    finally:
        end = time.time()
        total += end-start
        count += 1
        if count % 100 == 0:
            print 'Processed {0} images...'.format(count)
        if DEBUG:
            print ('{0} : {1:.10f} secs'.format(label, end - start))

######################## process_local_dir ############################
def process_local_dir(fn,prefix,preflong,pictype):
    lst = []
    for root, subFolders, files in os.walk(fn):
        for ele in files:
            fname = os.path.join(root, ele) #full path name
            if ele.endswith(".JPG") and (preflong in fname):
                hr = 10
		#check that its day time
                with timeblock('EXIF_JPEG'):
                    with open(fname, 'rb') as fjpeg:
                        tags = exifread.process_file(fjpeg)
                    stop_tag = 'Image DateTime'
                    dt_tag = vars(tags[stop_tag])['printable']
                    #dt_tag: 2014:08:01 19:06:50
                    #t: 19:06:50
                    t = dt_tag.split()[1]
		    t = t.split(':')
		    hr = int(t[0])
                    if DEBUG:
                        print 'HOUR: {0}'.format(hr)
		if hr >= 9 and hr <= 16:  #between 9am and 4pm, inclusive
                    if DEBUG:
                        print '\tAppending'
		    lst.append(fname)
    return lst


######################## main ############################
def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='Find all of the pictures under each camera prefix is map and count them')
    parser.add_argument('imgdir',action='store',help='Directory')
    parser.add_argument('map',action='store',help='json map filename with Box directories to check')
    parser.add_argument('out_fname',action='store',help='output filename')
    #json map format: "Lisque": ["7413964473","Lisque Mesa 1"],
    #			prefix	     ID	    actual fname prefix

    '''The output of this program is a file called outfile (name passed in) that holds the full path to the file.
       A client program should read in this file, read each line, identify the file in the filesystem, and 
       pass it to the processing program (TensorFlow) for processing.  The images in the file are randomly
       selected and were taking during the hours of 9am and 4pm.'''

    '''The map file passed in should contain this line for the Main camera:
    		"Main":["7413970457","Main Road Water Hole","2"]
    '''

    #optional arguments
    parser.add_argument('--count',action='store',default=10000,help='number of images to return')
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
    with open(args.out_fname,'w') as ofile:    
        for key in mymap: #process a camera at a time 

            #key is the location prefix specified in the config file
            val = mymap[key] #list of three strings
            myfolder_id = val[0] #folder ID cut/pasted from box after creating 
            #the folder manually (its in the URL when in folder in box)
            prefix = key
            full_prefix = val[1] #used to check if a file belongs to this folder/key
            pictype = int(val[2]) #index indicating which OCR to use
            if DEBUG:
                print '{0}: {1}: {2}'.format(myfolder_id,prefix,full_prefix)

	    #get the list containing the full_filename for this map key (camera location)
            the_list = process_local_dir(args.imgdir,prefix,full_prefix,pictype)
            new_list = random.sample(the_list, args.count)
	    for item in new_list:
		ofile.write(item+'\n')
    print 'Total time for running exif on all Main JPGs: {0}secs for {1} images = {2} secs per image'.format(total,count,float(total/count))


    '''The following reads in the file we just wrote and processes each file.  Modify this example to
	process the file with TensorFlow. Uncomment to print out the sizes of each file listed in out_fname.
    '''
    ''' 
    with open(args.out_fname,'r') as ifile:    
        for line in ifile: 
            #strip off the newline character
	    fname = line.strip()
            with open(args.out_fname,'r') as open_file:    
	        pass #unused, but file is open here if needed
            #get the size of the file in bytes
            size = os.path.getsize(fname)
	    print size
    '''
##################################
if __name__ == '__main__':
    main()
