'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''
'''USAGE:'''
'''grep 'NewOCR\|OrigOCR\|process_JPG\|perform_OCR' old_ocr_main.out > grot'''
'''python2.7 old_ocr_stats.py --debug grot > out'''
'''old_ocr_main.out are the Main entries from runocr.sh/jpeg_processor.py runocr.out output file'''

import json, sys, argparse, csv, logging, os, time
import exifread
import numpy as np

DEBUG = True
########################
def process(img_dir_prefix,lst,ocr_list,newocr):
    #...
    #process_JPG (../photos2/2016 Sedgwick Pictures (8-24-2016 Monthly Update)/Main Road Water Hole (6-27-2016 to 8-10-2016)/Main Road Water Hole 6-27-2016 to 7-10-2016/100RECNX/IMG_9305.JPG) : 0.0000159740 secs
    #process_jpeg: skipping upload for testing purposes
    #OrigOCR: Temp is: 55
    #perform_OCR : 0.3743669987 secs

    #...
    #process_JPG (../photos2/2016 Sedgwick Pictures (8-24-2016 Monthly Update)/Main Road Water Hole (6-27-2016 to 8-10-2016)/Main Road Water Hole 6-27-2016 to 7-10-2016/100RECNX/IMG_7941.JPG) : 0.0000169277 secs
    #NewOCR: Temp is: 74
    #perform_OCR : 0.3260560036 secs

    #sedgwick data across 2013 through 2016 per month from: http://www.wrcc.dri.edu/cgi-bin/rawMAIN.pl?caucse
    #12 months Jan-Dec, max min across years
    #2013
    #min_max = [(25,77), (29,79), (35,86), (30,91), (33,98), (61,103), (44,100), (42,99), (39,98), (38,90), (39,85), (22,83)]
    #2013 & 2014
    #min_max = [(25,86), (29,83), (35,88), (30,95), (33,99), (40,103), (44,100), (42,99), (39,99), (38,101), (37,89), (22,83)]
    #2013 & 2014 & 2015
    #min_max = [(25,86), (29,83), (35,91), (30,95), (33,99), (40,103), (44,100), (42,102), (39,101), (38,101), (31,89), (22,83)]
    #2013 & 2014 & 2015 & 2016
    min_max = [(25,86), (28,87), (31,91), (30,95), (33,99), (40,103), (43,100), (42,102), (39,101), (38,101), (31,89), (22,83)]


    rlist = list(reversed(lst))
    if DEBUG:
        print 'rlist: {0}'.format(rlist)
	#rlist: ['perform_OCR : 0.3612451553 secs\n', 'process_JPG (../photos2/2016 Sedgwick Pictures (8-24-2016 Monthly Update)/Main Road Water Hole (6-27-2016 to 8-10-2016)/Main Road Water Hole 6-27-2016 to 7-10-2016/100RECNX/IMG_9305.JPG) : 0.0000138283 secs\n']

    #verify rlist[0] startsWith 'perform_OCR'
    if not rlist[0].startswith('perform_OCR'):
        print 'error, ele should be perform_OCR line: {0}'.format(rlist[0])
        sys.exit(1)
    ele = rlist[0].split() #perform_OCR : 0.3369410038 secs, extract secs
    ocr_time = float(ele[2])
    ele = rlist[1].split() 
    temp = -9999
    idx = 3
    try:
        temp = int(ele[idx])
    except ValueError as e:
        pass
    
    #skip rlist[2] if not newocr
    if newocr:
        idx = 2
    else: 
        idx = 3
    ele = rlist[idx].split(':')#process_JPG fname_in_parens : val secs
    ftmp = ele[0][13:-2] #grab fname without first and last parens
    ocr_list.append(ocr_time)

    tags = None
    with open(ftmp, 'rb') as fjpeg:
        tags = exifread.process_file(fjpeg)
    if not tags:
        print 'Error: tags is None!'
	sys.exit(1)
    stop_tag = 'Image DateTime'
    dt_tag = vars(tags[stop_tag])['printable']
    #dt_tag: 2014:08:01 19:06:50
    d = (dt_tag.split()[0]).replace(':','-')
    t = dt_tag.split()[1]
    mo_idx = int(d[5:7])-1 #min_max has base_index of 0 not 1 so subtract 1
    mi = min_max[mo_idx][0]
    mx = min_max[mo_idx][1]
    err = False
    if temp < (mi-10) or temp > (mx+10):
        err = True

    #get just the filename without the path
    orig_fname = ftmp[ftmp.rfind('/')+1:]
    if orig_fname.startswith('IMAG'):
        idx = 4
    elif orig_fname.startswith('IMG_'):
        idx = 3
    elif orig_fname.startswith('RCNX'):
        idx = 3
    elif orig_fname.startswith('MFDC'):
        idx = 3
    else:
        idx = orig_fname.rindex(' ') #xxx 500.JPG
    photo_id = orig_fname[idx+1:len(orig_fname)-4]
    newfname = 'Main_{0}_{1}_{2}.JPG'.format(d,t,photo_id)
    if err:
        print '{0} {1} ERR'.format(newfname, temp)
    else:
        print '{0} {1}'.format(newfname, temp)

######################## main ############################
def main():
    global DEBUG
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Process stdout from DEBUG=True check_box.py')
    parser.add_argument('fn',action='store',help='filename')
    parser.add_argument('img_dir_prefix',action='store',help='prefix path to the start of ../photos')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    parser.add_argument('--newocr',action='store_true',default=False,help='Parse for newocr file')
    args = parser.parse_args()
    DEBUG = args.debug
 
    #prepare the lists for collecting float values (ocr, boxcheck, and boxupload)
    ocr_list = []

    #produce the file via grep 'skipping\|upload_\|perform_OCR' main.out > grot
    #read in the file
    with open(args.fn,'r') as f:    
	#record until we hit 'perform_OCR' then back up through recorded list
	recorded_list = []
        for line in f:
	    recorded_list.append(line)
	    if line.startswith('perform_OCR'):
		#process recorded list
		process(args.img_dir_prefix,recorded_list,ocr_list,args.newocr)
		recorded_list = []

    #convert the lists to arrays
    ocr_ary = np.asarray(ocr_list,dtype=np.float64)
    #std = sqrt(mean(abs(x - x.mean())**2))
    #count = N-1 (unbiased) when ddof=1 (N when ddof is unset):
    #np.std(a,ddof=1,dtype=np.float64)
    print 'OCR avg: {0} stdev: {1}, count {2}'.format(np.mean(ocr_ary,dtype=np.float64),
        np.std(ocr_ary,ddof=1,dtype=np.float64),
        len(ocr_ary))

##################################
if __name__ == '__main__':
    main()
