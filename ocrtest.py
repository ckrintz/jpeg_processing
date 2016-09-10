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
	#uncomment this to see all of the keys in tags:
	#print 'All tags in jpeg metadata:\n{0}'.format(tags)
        dt_tag = vars(tags[stop_tag])['printable']
        stop_tag = 'EXIF ExifImageLength'
        len_tag = vars(tags[stop_tag])['printable']
        stop_tag = 'EXIF ExifImageWidth'
        wid_tag = vars(tags[stop_tag])['printable']
        print 'Filename: {0}, datetime {1}, res {2}x{3}, pictype {4}'.format(fn,dt_tag,wid_tag,len_tag,pictype)
	try:
	    if int(wid_tag) == 2560 and int(len_tag) == 1920: #Windmill1, UpperRes no temp
		temp = -9998 #no temp
	    elif int(wid_tag) == 3264 and int(len_tag) == 2448: #Windmill1 2014, BoneT
                temp = crop_and_recognize.run_c1(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_1/')
	    elif int(wid_tag) == 1920 and int(len_tag) == 1080: #main,lisque,fig,ne,vulture_pre16
                    temp = crop_and_recognize.run_c2(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_2/')
	    elif int(wid_tag) == 3776 and int(len_tag) == 2124: #boneH
                    temp = crop_and_recognize.run_c3(fullfname, 'ocr_knn/flask_ocr/backend/data/data_files/camera_3/')
	    elif int(wid_tag) == 2688 and int(len_tag) == 1512: #vulture16
		    temp = -9997 #TBD rerun these when supported
		    err = True #error
	    elif int(wid_tag) == 2048 and int(len_tag) == 1536: #windmillG,blue
		    temp = -9997 #TBD rerun these when supported
	    else:
		    print 'Error: unsupported OCR resolution: {0}x{1}'.format(wid_tag,len_tag)
		    temp = -9996
        except Exception as e:
	    print e
	    print 'Error: OCR exception for: {0}x{1}'.format(wid_tag,len_tag)
	    temp = -9995

        print 'temp {0}'.format(temp)

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
