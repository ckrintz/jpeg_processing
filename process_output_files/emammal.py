'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import csv
import json, sys, argparse, csv, logging, os, time
import numpy as np
from datetime import datetime, timedelta
import dbiface
import upload_files

DEBUG=False
SEDGWICK='7411611121'

def main():
    global DEBUG #to allow setting DEBUG flag via command line
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='JPEG/Box File Processing for Emammal Upload')
    #required arguments
    parser.add_argument('fname',action='store',help='CSV file (must have header row) to import into DB')
    parser.add_argument('ofname',action='store',help='Output JPEG file')
    #optional arguments
    parser.add_argument('--overWrite',action='store_true',default=False,help='overwrite entire db table with data in this CSV (default is to append, skipping keys that exists (date,time,ID))')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on')
    args = parser.parse_args()

    #datetime temp
    dtdict = {}
    DEBUG = args.debug
    first = True
    #fname = 'Blue_2015-04-15_14:34:10_00'
    fname = 'Main_2013-10-13' #350 in dir at 450K each is 161MB
    #log into box if needed
    auth_client = upload_files.setup()

    #get one file, get its folder, walk folder entries (guaranteed to be on same day) to find series
    limit = 1
    jpegs = upload_files.get_files(auth_client,SEDGWICK,fname,0,limit) #returns list unordered, not guaranteed to have prefix
    if len(jpegs) == limit and jpegs[0].name.startswith(fname):
        #help/info from: https://docs.box.com/reference#folder-object-1
        print 'found a file: {0}'.format(jpegs[0].name)
        jpeg_parent = jpegs[0].parent['id']
        fldr = upload_files.get_folder(auth_client,jpeg_parent) #returns folder object from box
        print 'item count: {0}'.format(fldr['item_collection']['total_count'])
        print 'path: {0}'.format(fldr['path_collection']['entries'])
        count = 0
        for ent in fldr['item_collection']['entries']:
            print ent
            if ent.name.startswith(fname):
                count += 1
        print count
    sys.exit(1)

    offset = 0 #starts at 0, max is 200 returned
    limit = 200
    mx = 350 #from https://ucsb.app.box.com/files/0/f/7825943021/10 for 10-13
    jpegs = upload_files.get_files(auth_client,SEDGWICK,fname,offset,limit) #returns list unordered, not guaranteed to have prefix
    count = len(jpegs)
    if count == 0:  #try again
        jpegs = upload_files.get_files(auth_client,SEDGWICK,fname,offset,limit) #returns list unordered, not guaranteed to have prefix
    count = len(jpegs)
    print count

    if count == 0: #something bad happened in the call
	print 'Error, no files came back for fname:{0}'.format(fname)
        sys.exit(1)
    for j in jpegs:
        print j.name
    jpeg_parent = jpegs[0].parent['id']
    fldr = upload_files.get_folder(auth_client,jpeg_parent) #returns folder object from box
    #get the number of entries in the folder containing this file
    print fldr['item_collection']['total_count']
    
    print 'mx: {0} count: {1}'.format(mx,count)
    while count < mx: #should we be setting limit here to be the difference of max and limit?
        offset = offset+limit
        print '\t looping offset: {0} limit: {1}'.format(offset,limit)
        newjpegs = upload_files.get_files(auth_client,SEDGWICK,fname,offset,limit) #returns list unordered, not guaranteed to have prefix
	count = count + len(newjpegs)
        jpegs = jpegs + newjpegs
    print 'mx: {0} count: {1}'.format(mx,count)

    with open(args.ofname,'wb') as f:
        for j in jpegs:
	    f.write('{0}\n'.format(j.name))
        
    sys.exit(1)
    for j in jpegs:
        if first: #download the first one for testing
            with open(args.ofname,'wb') as f:
	        j.download_to(f)
            first = False
            break
        print j.name,j.id
    

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

