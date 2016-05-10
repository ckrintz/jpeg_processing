'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

'''csv file format:
box_path:filename,date,time,ID,size,temp,flash,bad_temp,orig_fname
Windmill\2015\11\08:Windmill_2015-11-08_23:08:55_091.JPG,2015-11-08,23:08:55,091,1004421,?,Flash,True,IMAG0091.JPG
...
'''

import csv
import json, sys, argparse, csv, logging, os, time
from datetime import datetime, timedelta

DEBUG=False
def main():
    global DEBUG #to allow setting DEBUG flag via command line
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='CSV File Processing')
    #required arguments
    parser.add_argument('fname',action='store',help='CSV file to process')
    parser.add_argument('outfname',action='store',help='text file to output for plotting')
    #optional arguments
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on')
    args = parser.parse_args()

    #datetime temp
    dtdict = {}
    DEBUG = args.debug

    #open the csv file for writing out dataset for plotting: datetime loc1_temp loc2_temp ... loc9_temp
    locs = ["Lisque","Figueroa","Windmill","Main","BoneT","BoneH","NE","Vulture","Blue"]
    with open(args.outfname,'wt') as fout:
        with open(args.fname,'rt') as f:
            csvFile = csv.DictReader(f) #create a dictionary per row with headers as keys
            for row in csvFile:
                print row
	        #{'temp': '51', 'flash': 'NoFlash', 'bad_temp': 'False', 'box_path:filename': 'Bone\\2015\\09\\16:BoneH_2015-09-16_22:30:48_1499.JPG', 'time': '22:30:48', 'date': '2015-09-16', 'orig_fname': 'RCNX1499.JPG', 'ID': '1499', 'size': '1700891'}
                if not row['bad_temp']:
		    #extract filename
		    this_prefix = row['box_path:filename'].split(':')[1]
		    #extract prefix from filename
		    this_loc = this_prefix.split('_')[0]
		    
		    #dt: {loc: value}  however there may be multiple dt's for a loc
			
                    temp = row['temp']
		    ts = '{0} {1}'.format(row['date'],row['time'])
		    dt = datetime.strptime(ts, '%Y-%M-%D %H:%M:%S')
		    dtdict[dt] = temp
	

if __name__ == '__main__':
    main()

