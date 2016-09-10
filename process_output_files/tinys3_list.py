import tinys3,requests,time
from contextlib import contextmanager
######################## timer utility ############################
@contextmanager
def timeblock(label):
    start = time.time() #time.process_time() available in python 3
    try:
        yield
    finally:
        end = time.time()
        print ('{0} : {1:.10f} secs'.format(label, end - start))

###################################################################

######################## main ############################
def main():
    acc = 'XXX'
    sec = 'YYY'
    conn = tinys3.Connection(acc,sec,tls=True)
    bkt = 'incoming-legacy-data'
    fname ='201307/Main_2013-07-13_15:44:14_001.JPG'
    bogusfname = '201307/XXX-07-13_15:44:14_001.JPG'

    #first s3 access is always long (~9s)
    with timeblock('tinys3 get bad fname ({0})'.format(bogusfname)):
        try:
            resp = conn.get(bogusfname,bkt)
        except requests.exceptions.HTTPError as e:
            print e
    
    with timeblock('tinys3 list ({0})'.format(fname)):
        try:
            iter = conn.list(fname,bkt)
            for i in iter:
                print 'size {0}, etag {1}, key {2}'.format(i['size'],i['etag'],i['key'])
        except requests.exceptions.HTTPError as e:
            print e
            print e.response.status_code
    
    with timeblock('tinys3 list on bad name ({0})'.format(bogusfname)):
        try:
            iter = conn.list(bogusfname,bkt)
            if next(iter,None) == None:
                print 'empty list returned'
            for i in iter:
                print 'size {0}, etag {1}, key {2}'.format(i['size'],i['etag'],i['key'])
        except requests.exceptions.HTTPError as e:
            print e
            print e.response.status_code
    
    with timeblock('tinys3 get ({0})'.format(fname)):
        try:
            resp = conn.get(fname,bkt)
        except requests.exceptions.HTTPError as e:
            print e
        print resp.status_code

    ''' fails with 
        400 Client Error: Bad Request for url: 
	https://s3.amazonaws.com/incoming-legacy-data/201307/Main_2013-07-13_15:44:14_001.JPG
	and 404 not found if name not in s3
   
    with timeblock('tinys3 updateMeta ({0})'.format(fname)):
        try:
            resp = conn.update_metadata(fname,metadata=None,bucket=bkt,public=True)
        except requests.exceptions.HTTPError as e:
            print e
    
    with timeblock('tinys3 updateMeta for bad name ({0})'.format(bogusfname)):
        try:
            resp = conn.update_metadata(bogusfname,metadata=None,bucket=bkt,public=True)
        except requests.exceptions.HTTPError as e:
            print e
    '''
    

    fn = 'Main_2013-07-13_15:44:14_001.JPG'
    print 'uploading {0}'.format(fn)
    f = open(fn,'rb')
    with timeblock('tinys3 upload ({0})'.format(fname)):
        try:
            resp = conn.upload(fname,f,bkt)
        except requests.exceptions.HTTPError as e:
            print e
        print resp.status_code

##################################
if __name__ == '__main__':
    main()
