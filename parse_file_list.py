'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license

   USAGE: python parse_file_list.py filelist

'''

import argparse,json,os,sys,time,exifread
from contextlib import contextmanager #for timeblock

DEBUG = False

############## main #################
def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='Parse a random_file_list.txt file produced by pick_random_images.py')
    parser.add_argument('fname',action='store',help='filename')
    args = parser.parse_args()

    fname=args.fname
    boxdirID = 0 #0:20
    boxfileID = 0 #0:500
    done18 = False
    done19 = False
    with open(fname, 'rb') as f:
	for fi in f:
            fname_jpeg = fi.strip()
            with open(fname_jpeg, 'rb') as fjpeg:
                tags = exifread.process_file(fjpeg)
            stop_tag = 'Image DateTime'
            dt_tag = vars(tags[stop_tag])['printable']
	    d = (dt_tag.split()[0]).replace(':','-')
            t = dt_tag.split()[1]
            idx = (fname_jpeg).rfind('/') - len(fname_jpeg) + 1 #last / index minus len sb negative
            ele = fname_jpeg[idx:]
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
      
            if done18:
                box_name_string = '18-{0}{1}'.format(boxdirID,boxfileID)
            elif done19:
                box_name_string = '19-{0}{1}'.format(boxdirID,boxfileID)
            else: 
                box_name_string = '{0}-{1}'.format(boxdirID,boxfileID)
            boxfileID += 1

            if not done18:
                if boxfileID >= 500:
                    boxdirID += 1
	            if boxdirID == 18:
                        done18 = True
                        boxdirID = 9
		        boxfileID = 500
	            else: 
                        boxfileID = 0
            else: #in 18 or 19
                if boxfileID >= 9999:
                    done19 = True
		    #start 19
                    boxdirID = 5
		    boxfileID = 0

            newfname = 'Main_{0}_{1}_{2}_{3}.JPG'.format(d,t,photo_id,box_name_string)
            print newfname
        
if __name__ == "__main__":
        main()
