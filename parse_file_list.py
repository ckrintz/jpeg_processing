'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license

   USAGE: python parse_file_list.py filelist

'''

import argparse,json,os,sys,time
from contextlib import contextmanager #for timeblock

DEBUG = False

############## main #################
def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='Parse a random_file_list.txt file produced by pick_random_images.py')
    parser.add_argument('fname',action='store',help='filename')
    args = parser.parse_args()

    fname=args.fname

    with open(fname, 'rb') as f:
	for fi in f:
            print fi.strip()

if __name__ == "__main__":
        main()
