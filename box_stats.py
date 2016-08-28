'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''
'''USAGE:'''
'''grep 'skipping\|upload_\|perform_OCR' main.out > grot'''
'''python2.7 box_stats.py --debug grot > out'''

import json, sys, argparse, csv, logging, os, time
import numpy as np

DEBUG = True
########################
def process(lst,ocr_list,boxcheck_list,boxupload_list):
    #Box conflict after lookup - record lookup time and ocr time
    #upload_it: uploading file via API: Main_2016-07-26_05:42:43_5692.JPG
    #skipping Main_2016-07-26_05:42:43_5692.JPG, already uploaded
    #upload_BOX : 2.2590510845 secs
    #perform_OCR : 0.3369410038 secs

    #Box upload - record lookup time and ocr time
    #upload_it: uploading file via API: Main_2016-07-06_14:33:06_9724.JPG
    #upload_it: upload complete: Main_2016-07-06_14:33:06_9724.JPG
    #upload_BOX : 2.2590510845 secs
    #perform_OCR : 0.3369410038 secs

    #skip all Box lookups - record ocr time only (note no upload_it)
    #skipping Main_2016-07-06_09:40:39_9305.JPG
    #upload_BOX : 2.2590510845 secs
    #perform_OCR : 0.3369410038 secs

    rlist = list(reversed(lst))
    if DEBUG:
        print 'rlist:\n{0} {1} {2}'.format(rlist[0],rlist[1],rlist[2])
    #verify rlist[0] startsWith 'perform_OCR'
    if not rlist[0].startswith('perform_OCR'):
        print 'error, ele should be perform_OCR line: {0}'.format(rlist[0])
        sys.exit(1)
    ele = rlist[0].split() #perform_OCR : 0.3369410038 secs, extract secs
    ocr_time = float(ele[2])
    ele = rlist[1].split() #upload_BOX : 2.2590510845 secs, extract secs
    upload_time = float(ele[2])
    if DEBUG:
        print '\tOCR time: {0}; upload time: {1}'.format(ocr_time,upload_time)
    ele = rlist[2] #skipping,upload_it, skipping ... already uploaded
    ocr_list.append(ocr_time)
    if 'skipping' in ele:
	if 'already uploaded' in ele:
            #Box conflict after lookup - record lookup time and ocr time
            if DEBUG:
                print '\tbox conflict {0}'.format(upload_time)
            boxcheck_list.append(upload_time)
        else:
            #skip all Box lookups - record ocr time only (note no upload_it)
            if DEBUG:
                print '\tskipping box altogether'.format(upload_time)
    else: #Box upload - record lookup time and ocr time
        if DEBUG:
            print '\tbox upload'.format(upload_time)
        boxupload_list.append(upload_time)
   

######################## main ############################
def main():
    global DEBUG
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Process stdout from DEBUG=True check_box.py')
    parser.add_argument('fn',action='store',help='filename')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    args = parser.parse_args()
    DEBUG = args.debug
 
    #prepare the lists for collecting float values (ocr, boxcheck, and boxupload)
    ocr_list = []
    boxcheck_list = []
    boxupload_list = []

    #produce the file via grep 'skipping\|upload_\|perform_OCR' main.out > grot
    #read in the file
    with open(args.fn,'r') as f:    
	#record until we hit 'perform_OCR' then back up through recorded list
	recorded_list = []
        for line in f:
	    recorded_list.append(line)
	    if line.startswith('perform_OCR'):
		#process recorded list
		process(recorded_list,ocr_list,boxcheck_list,boxupload_list)
		recorded_list = []

    #convert the lists to arrays
    ocr_ary = np.asarray(ocr_list,dtype=np.float64)
    boxcheck_ary = np.asarray(boxcheck_list,dtype=np.float64)
    boxupload_ary = np.asarray(boxupload_list,dtype=np.float64)
    #std = sqrt(mean(abs(x - x.mean())**2))
    #count = N-1 (unbiased) when ddof=1 (N when ddof is unset):
    #np.std(a,ddof=1,dtype=np.float64)
    print 'OCR avg: {0} stdev: {1}, count {2}'.format(np.mean(ocr_ary,dtype=np.float64),
        np.std(ocr_ary,ddof=1,dtype=np.float64),
        len(ocr_ary))
    print 'CHECK avg: {0} stdev: {1}, count {2}'.format(np.mean(boxcheck_ary,dtype=np.float64),
        np.std(boxcheck_ary,ddof=1,dtype=np.float64),
        len(boxcheck_ary))
    print 'UPLOAD avg: {0} stdev: {1}, count {2}'.format(np.mean(boxupload_ary,dtype=np.float64),
        np.std(boxupload_ary,ddof=1,dtype=np.float64),
        len(boxupload_ary))

##################################
if __name__ == '__main__':
    main()
