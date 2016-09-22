import requests
IP = 'localhost'
PORT = '8080' # make sure that you started the service on this port (app.run(host='0.0.0.0',port=8080) in flask)

fname = 'test.jpg'
pictype = '2'
remote_fname = 'temp.jpg'
url = 'http://{0}:{1}/upload'.format(IP,PORT)
payload = {'filename': remote_fname, 'pictype': pictype}
print url
print payload
try:
    files = {'files': open(fname, 'rb')}
    resp = requests.post(url, files=files, data=payload)
    if resp.status_code == 200:
        jresp = resp.json()
        temp = jresp['temperature']
    else: 
        print 'Error, status code {0}'.format(resp.status_code)
        temp = -9999
except Exception as e:
    print e 
    temp = -9999
print 'Temperature: {0}'.format(temp)
