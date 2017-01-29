'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license
   required: python2.7
   USAGE: python parse_file_list.py filelist.txt 
          python parse_file_list.py --printcsv random_file_listORIG.txt > random_file_map.csv
          python parse_file_list.py --copy random_file_listORIG.txt > filelist.txt
   The first usage generates a list of new file names with date_time_ID_dir_fnameprefix
	ID is the camera ID
	dir is the Box directory under animal_classifciation 
	and fnameprefix is the filename (without .JPG) in box under dir.
   The second usage generates a csv file with lines: orig_filename, dir, fnameprefix
	dir and fnameprefix are the same as above
   The third usage is the same as the first only it copies the file via rsync to a remote hardcoded location

'''

import argparse,json,os,sys,time,exifread
from contextlib import contextmanager #for timeblock
import cv2

DEBUG = False

############## main #################
def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='Parse a random_file_list.txt file produced by pick_random_images.py and map the file names to Andys filenames in Box directory animal_classification.')
    #required args
    parser.add_argument('fname',action='store',help='filename')
    #optional args
    parser.add_argument('--printcsv',action='store_true',default=False,help='Generate a CSV file of the map')
    parser.add_argument('--copy',action='store_true',default=False,help='copy to remote directory via rsync (hardcoded)')
    args = parser.parse_args()

    fname=args.fname
    printCSV=args.printcsv
    copyThem=args.copy
    rootstr = 'root@169.231.235.52:/opt2/sedgwick/images/'
    count = 0
    size = 0

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
                if printCSV:
                    print '{0},18,{1}{2}'.format(fname_jpeg,boxdirID,boxfileID)
            if done19: #overwrite if done18 and done19
                box_name_string = '19-{0}'.format(boxfileID)
                if printCSV:
                    print '{0},19,{1}'.format(fname_jpeg,boxfileID)
            if not done18 and not done19:
                box_name_string = '{0}-{1}'.format(boxdirID,boxfileID)
                if printCSV:
                    print '{0},{1},{2}'.format(fname_jpeg,boxdirID,boxfileID)

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
                if not done19:
                    if boxfileID >= 1000:
                        done19 = True #done18 should remain true
		        #start 19
		        boxfileID = 5000

            newfname = 'Main_{0}_{1}_{2}_{3}.jpg'.format(d,t,photo_id,box_name_string)
            if not printCSV:
                print newfname

	    if copyThem:
                size += os.path.getsize(fname_jpeg)
                count += 1
                fn = fname_jpeg.replace(' ','\ ')
                fn = fn.replace('(','\(')
                fn = fn.replace(')','\)')
                #cmd = 'rsync -az {0} {1}/{2}/{3}/{4}'.format(fn,rootstr,yr,mo,newfname)
                cmd = 'rsync -az {0} {1}/zooniverse/{2}'.format(fn,rootstr,newfname)
                os.system(cmd)

                #make thumbnail 300 pixels wide
                image = cv2.imread(fname_jpeg)
                r = 300.0/image.shape[1] #shape: rows,cols,channels, so width is index 1
                dim = (300, int(image.shape[0] *r)) #height is index 0
                resized = cv2.resize(image,dim,interpolation=cv2.INTER_AREA)
                fnsmall = 'tmp112.jpg'
                cv2.imwrite(fnsmall,resized)
                nfn = newfname.replace('.jpg','_t.jpg')
                #cmd = 'rsync -az {0} {1}/{2}/{3}/{4}'.format(fnsmall,rootstr,yr,mo,nfn)
                cmd = 'rsync -az {0} {1}/zooniverse/{2}'.format(fnsmall,rootstr,nfn)
                os.system(cmd)
                if DEBUG:
                    print 'command: {0} {1} {2}'.format(cmd,fn,newfname)
                    print 'command: {0} {1}'.format(fnsmall,nfn)
    print 'copied {0} files and {1} bytes'.format(count, size)

if __name__ == "__main__":
        main()
