'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

'''
USAGE: python2.7 ocrtest.py pictype image.JPG
'''

import json, sys, argparse, csv, logging, os, time
import exifread
#from datetime import datetime, timedelta
from contextlib import contextmanager
#import upload_files
import crop_and_recognize

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

def get_exif(fn,pictype):
    '''  Extract the jpeg metadata from JPG files and call OCR on it, returning image date and temp'''
    stop_tag = 'Image DateTime' #token to search for in the JPG info
    dt_tag = None
    fullfname = os.path.abspath(fn)
    print 'Full filename: {0}'.format(fullfname)
    with open(fullfname, 'rb') as f:
        tags = exifread.process_file(f)
        dt_tag = vars(tags[stop_tag])['printable']

        if pictype == 1:
            temp = crop_and_recognize.run_c1(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_1/')
        elif pictype == 2:
            temp = crop_and_recognize.run_c2(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_2/')
        elif pictype == 3:
            temp = crop_and_recognize.run_c3(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_3/')
        else:
	    print 'Error unknown pictype: {0}'.format(pictype)
	    temp = -9999
    print 'Filename: {0}, datetime {1}, pictype {2}, temp {3}'.format(fn,dt_tag,pictype,temp)

def main():
    global newocr
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='JPEG OCR tester')
    #required arguments
    parser.add_argument('pictype',action='store',type=int,help='OCR pictype 1,2,3')
    parser.add_argument('img',action='store',help='JPEG image')
    args = parser.parse_args()

    get_exif(args.img,args.pictype)

if __name__ == '__main__':
    main()
