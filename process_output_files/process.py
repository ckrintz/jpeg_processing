'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import csv
import json, sys, argparse, csv, logging, os, time
import numpy as np
from datetime import datetime, timedelta
import dbiface

DEBUG=False
def main():
    global DEBUG #to allow setting DEBUG flag via command line
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='CSV File Processing')
    #required arguments
    parser.add_argument('fname',action='store',help='CSV file (must have header row) to import into DB')
    #optional arguments
    parser.add_argument('--overWrite',action='store_true',default=False,help='overwrite entire db table with data in this CSV (default is to append, skipping keys that exists (date,time,ID))')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on')
    args = parser.parse_args()

    #datetime temp
    dtdict = {}
    DEBUG = args.debug

    dbname = 'wtbdb'
    tname = 'metainfo'

    ''' 
    The following creates a table with a schema that matches the CSV format:
    	Header box_path:filename,date,time,ID,size,temp,flash,bad_temp,orig_fname
    	key/value pairs {'temp': '51', 'flash': 'NoFlash', 'bad_temp': 'False', 'box_path:filename': 'Bone\\2015\\09\\16:BoneH_2015-09-16_22:30:48_1499.JPG', 'time': '22:30:48', 'date': '2015-09-16', 'orig_fname': 'RCNX1499.JPG', 'ID': '1499', 'size': '1700891'}
    temp is text b/c it may contain a ? when there is no temperature 
        in the picture or when OCR fails to extract it
    For info on CONSTRAINT and creating primary keys from multiple columns see:
    http://www.techonthenet.com/postgresql/primary_keys.php

    SQL should be in double quotes so that single quotes can be used for internal/nested strings
    '''
    sql = "CREATE TABLE IF NOT EXISTS {0}(boxfname TEXT, dt DATE, ti TIME, pid INT, size INT, temp TEXT, flash TEXT, badtemp BOOL, origfname TEXT, PRIMARY KEY (dt, ti, pid));".format(tname)
    db = dbiface.DBobj(dbname)
    cur = db.execute_sql(sql)

    #read what is in the db before the import
    sql = "SELECT * FROM {0};".format(tname)
    cur = db.execute_sql(sql)
    if DEBUG: 
        print 'Before:'
        rows = cur.fetchall()
        for row in rows:
            print row
    
    db.importCSV(args.fname,tname,args.overWrite)

    #read what is in the db after the import - use single quotes nested in outer double quotes
    #because SQL requires single
    sql = "SELECT * FROM {0} WHERE dt > '2015-11-08';".format(tname)
    #other examples to try:
    #sql = "SELECT * FROM {0} WHERE dt > '2015-01-01' AND dt < '2015-05-23';".format(tname)
    #sql = "SELECT * FROM {0} WHERE dt > '2015-01-01' AND dt < now();".format(tname)
    #sql = "SELECT * FROM {0} WHERE dt BETWEEN '2015-01-01' AND dt < now();".format(tname)
    #sql = "SELECT count(*) FROM {0} WHERE dt > '2015-01-01' AND dt < '2015-05-23';".format(tname)
    cur = db.execute_sql(sql)
    rows = cur.fetchall()
    for row in rows:
        print row
    db.closeConnection()
    

if __name__ == '__main__':
    main()

