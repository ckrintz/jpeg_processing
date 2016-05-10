# jpeg_processing
Image processing, OCR, exim, and box.com upload tools

Do not add/commit app.cfg or tokens.json into the repository!  They hold your private box app details. tokens.json is created for your automatically when you complete the oauth handshake initially.  The oauth handshake code is in upload_files.py.

## Setup Steps
A) Install python2.7<br>
python -V<br>
Python 2.7.10<br>

If the above does not print 2.7.something then make sure and use python2.7:<br>
python2.7 -V <br>
Python 2.7.10<br>

B) Install pip2.7 (you may need to prefix with sudo (for which you need admin priviledges to run))<br>
//install pip: sudo yum install python-pip<br>
pip --upgrade pip<br>

C) install packages<br>
you may need to prefix with sudo (for which you need admin priviledges to run)<br>

you can remove the 2.7 if you are working directly with python2.7:<br>
pip2.7 install boxsdk pytesseract Pillow oauth2client httplib2 flask numpy scipy scikit-learn scikit-image python-jose matplotlib<br>
pip2.7 install -U numpy scipy scikit-learn<br>
sudo yum install libffi-devel<br>
sudo pip2.7 install urllib3 pyopenssl ndg-httpsclient pyasn1<br>

sudo yum install tesseract<br>
sudo pip2.7 install --upgrade httplib2 requests exifread imutils<br>

install cv2 for python:<br>
switch to root: sudo -s<br>
Assuming Linux Centos6 throughout<br>

<tt>wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/3.1.0/opencv-3.1.0.zip?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fopencvlibrary%2F&ts=1462070500&use_mirror=pilotfiber<br>
unzip opencv-3.1.0.zip<br>
mv opencv-3.1.0.zip\?r\=https\:%2F%2Fsourceforge.net%2Fprojects%2Fopencvlibrary%2F opencv-3.1.0.zip<br>
unzip opencv-3.1.0.zip <br>
cd opencv-3.1.0<br>
mkdir -p build<br>
cd build<br>
</tt>

fyi: <br>
which python2.7<br>
	/opt/rh/python27/root/usr/bin/python2.7<br>
find /opt/rh -name libpython2.7.so -print<br>
	/opt/rh/python27/root/usr/lib64/libpython2.7.so<br>

Whatever the output above displays, replace the full path with the full paths to python2.7 in these variables in the cmake command below<br>
-DPYTHON_EXECUTABLE=<br>
-DPYTHON_INCLUDE_DIR=<br>
-DPYTHON_LIBRARY= <br>
-DPYTHON_NUMPY_INCLUDE_DIR<br>
-DPYTHON_PACKAGES_PATH<br>

<tt>cmake ../ -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_EXAMPLES=ON -DBUILD_NEW_PYTHON_SUPPORT=ON -DINSTALL_PYTHON_EXAMPLES=ON -DPYTHON_EXECUTABLE=/opt/rh/python27/root/usr/bin/python2.7 -DPYTHON_INCLUDE_DIR=/opt/rh/python27/root/usr/include/python2.7 -DPYTHON_LIBRARY=/opt/rh/python27/root/usr/lib64/libpython2.7.so -DPYTHON_NUMPY_INCLUDE_DIR=/opt/rh/python27/root/usr/lib64/python2.7/site-packages/numpy/core/include/ -DPYTHON_PACKAGES_PATH=/opt/rh/python27/root/usr/lib64/python2.7/site-packages -DBUILD_PYTHON_SUPPORT=ON
</tt><br>

make<br>
make install<br>

yum install numpy opencv*<br>
cp /usr/local/lib/python2.7/site-packages/cv2.so /opt/rh/python27/root/usr/lib/python2.7/site-packages/<br>

test as normal user:<br>
exit <br>
python2.7<br>
import cv2<br>
//working if no error<br>
quit()<br>

## Program Input Setup
Create a map in json format for each of the folders in box:<br>
"shortname": ["folder_ID", "original filename prefix"]<br>

sedgwick_map.json:
<tt><pre>
{
    "Lisque": ["7413964473","Lisque Mesa 1"],
    "Figueroa": ["7413966585","Figueroa Creek"],
    "Windmill": ["7413968941","Lisque Mesa 1"],
    "Main": ["7413970457","Main Road Water Hole"],
    "Bone": ["7413971853","Bone Canyon Water Trough"],
    "Northeast": ["7413973301","Northeast Corner Spring"],
    "Vulture": ["7413975069","Vulture Trough"],
    "Blue": ["7413976713","Blue Schist Water Hole"]
}
</pre></tt>

Next, create your app.cfg file:
<tt><pre>
6y3m...ACCESS...TOKEN...FROM...BOX
2yca...SECRET...TOKEN...FROM...BOX
https://localhost
</pre></tt>

upload_files.py expects this file to be in your local directory when you run it or a calling program (jpeg_processor.py).

You'll use these files as argument to the program jpeg_processor.py<br>

The following program <br>
	- recursively scans a directory and all of its subdirectories<br>
	- finds all *JPG files<br>
	- extracts the metadata from the JPG <br>

if your python version (python -V) is 2.7 then you can just use python here:<br>

<tt>python2.7 jpeg_processor.py /full/path/to/directory/of/interest sedgwick_map.json meta.csv >& meta.out</tt><br>

meta.csv will be created and will hold details on each file that is processed<br>
meta.out will be created and will hold timings of different operations performed by the program<br>

## Background and Box setup

jpeg_processor.py uses the following other python programs:

A) upload_files.py - uploads the files to box <br>
	//you can run this program by itself (there is a main routine), separate<br>
	//from jpeg_processor.py to learn and test it:<br>

<pre>
python upload_files.py -h

	//before you run this, you must set up box first (see (i) below)
	//Also you must create a directory folder in box, go into ucsb.box.com 
	//using your browser, create a new fold, open it, note the folder ID 
	//in the URL (directory name just prior to the folder name and /)
	//EX: https://ucsb.app.box.com/files/0/f/5757220117/INT_94RY  has an ID of 5757220117
	//replace 5802215677 below with your folder ID

	python upload_files.py 5802215677 testdir
	//testdir is a local directory that should hold JPG files and/or directories.  
	//The program walks testdir and uploads the files to box

	//successful output looks like this 
	//(depending on what you have in testdir, I have directories
	//and JPG files in different directories.  See how the directories are 
	//recursively searched:

	uploading to folder: test
	dir: testdir/
	processing file: test_1_chandra.JPG
	processing file: test_1.JPG
	processing file: test2_foo_1_bar.JPG
	processing file: test2_foo_1_boo.JPG
	processing file: test2_foo_1_foo.JPG
	

	//if you get an error, make sure you have completed the steps below
	//next, check the error message to see if you did something wrong
	//edit upload_files.py and set DEBUG to True and rerun to get more info
	//make sure and set DEBUG to False before running this on lots of files/production
	//as it is very verbose!
	//next, contact Chandra (ckrintz@cs.ucsb.edu) about it

</pre>

(i) setting up box so that you can upload to your own account:<br/>
//you only need to do this once; you also can make multiple apps (1 per each machine<br/>
//you want to run from)<br/>
in browser, goto: https://ucsb.app.box.com/developers/services<br/>
<pre>
	Select Create a Box Application on the right
	Name it (e.g. box_are1) and select create
	Scroll down and copy/paste (save off) the
		client_id 
		and
		client_secret
	Put this in the redirect_uri box:
		https://localhost
	Under scope, select
		Read and write all files and folders stored in Box 
</pre>

    (ii) Now go back to your machine and in the directory in which upload_files.py is in,<br>
	create a file called app.cfg and add 3 lines to it replace client_id and client_secret<br>
	with the values you downloaded and saved off in (i) above:<br>
		client_id<br>
		client_secret<br>
		https://localhost<br>

	The program upload_files.py reads this file in auth() to authorize use of<br>
	your box account by the program.<br>
	Save off this file so that you remember which box app it belongs to<br>
	<tt>cp app.cfg boxare1.cfg</tt><br>
	You will need to update app.cfg when/if you change apps or client id/secrets<br>

     (iii) upload_files.py also expects/uses a tokens files in the local directory called<br>
	tokens.json  (saved in global var TOKENS).  The program looks here to see<br>
	if there are old tokens it can use.  You can delete this file the first time<br>
	you run the program or to generate new tokens.  If you run the program<br>
	and you get the following error:<br>
<pre>
		boxsdk.exception.BoxOAuthException: 
		Message: {"error":"invalid_grant","error_description":"Invalid refresh token"}
		Status: 400
		URL: https://api.box.com/oauth2/token
		Method: POST
</pre>
<p>
	It means that your tokens have expired or are invalid and you need to create new ones.
	In this case, delete tokens.json and rerun.  This will step you through
	the authorization process which requires manual intervention.  You will
	only need to do this once if you only use this app and these tokens from the 
	same machine.  If you move machines and run this elsewhere, you will need to 
	copy over the tokens.json file back and forth.  There can only be one tokens.json
	file in use for a box app at a time.
</p>

<p>
	When you run upload_files.py without a tokens.json file it will give you a URL
	to navigate to in your browser (manual step): cut/paste this URL and go there
	with your browser.  It will ask you to Grant Access to Box (do so).
	It will then give you a page that says "Unable to Connect".  While on this page,
	cut/paste these two values from the URL in of the page:
</p>
<pre>
		code=...
		state=box_csrf_token_App...
</pre>

	These are arguments (the payload) of the URL.  The URL has a route<br>
		https://localhost/<br>
		Then there is a ? (used as a delimiter)<br>
		Followed by key-value pairs separated by & (another delimiter)<br>
	E.g: https://localhost/?state=box_csrf_token_yH1sKQq5sL75BEt2&code=q2cmsBoEmie4f5YN6HF6ZcEGuGSAlwtD<br>
		keys here are state and code<br>
		The = sign is a delimiter between the key and value<br>
		So here the value for state is: box_csrf_token_yH1sKQq5sL75BEt2<br>
		And the value for code is: q2cmsBoEmie4f5YN6HF6ZcEGuGSAlwtD<br>

<p>
	The state and code change each time you run the program (oauth handshake) to 
	generate the tokens.  When you do this, the first question asks you for the code
	and the second asks you for the csrf token (state).  Cut and paste these and 
	the program uses them to get the access and refresh tokens from box for all
	future uses.  It stores them in tokens.json so that you don't need to go through
	this step each time.  You can though, by just deleting tokens.json and going through
	all of the above step again. It doesn't hurt to do this repeatedly.  You can also
	press ctrl-C to quit and restart.
</p>
	
<pre>
		Type in the code that appears after             "code="
		in the URL box in your browser window, 
		and press enter: q2cmsBoEmie4f5YN6HF6ZcEGuGSAlwtD

		Type in the csrf in the URI: box_csrf_token_yH1sKQq5sL75BEt2

</pre>
	Note that if you take too long to cut/paste the code will expire and you'll have 
	to do the steps again (iii).
		
### ocr.py
Image processing toolkit, uses opencv (python cv2 -- which is a challenge to install)<br>
http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_image_display/py_image_display.html<br>

you will likely need/use/want matplotlib:<br>
http://matplotlib.org/<br>
http://matplotlib.org/users/pyplot_tutorial.html<br>


//you can run this program by itself (there is a main routine), separate<br>
//from jpeg_processor.py to learn and test it:<br>
python ocr.py -h<br>


This program use OCR to crop the JPEGs and extract the temperature from them as text.  There are 3 different cameras and each puts the temp in a different place.  The argument pictype to ocr.py distinquishes which of the three it is. See sample_files/README for details and examples<br>

Successful output: python ocr.py 1 bone14.JPG <br>
temp is: 70, trustworthy_if_false: False<br>

If trustworthy_if_false is True then the OCR failed (see the code).<br>
We perform no training on the data (something we should do if there are errors).<br>
To see if there are errors, see the csv file produced by jpeg_processor.py<br>
gzipped and checked into this directory:<br>
	2014run.csv.gz 2015run.csv.gz 2015run.out.gz<br>
The format of the csv file is:<br>
   folder\subfolder\...\:prefix_YY-MM-DD_HH-MM-SS_ID,YY-MM-DD,HH-MM-SS,ID,size,temp,flash<br>

edit ocr.py and set DEBUG to True and rerun to get more info<br>
make sure and set DEBUG to False before running this on lots of files/production<br>
as it is very verbose!<br>

There are many different image processing operations in this file for reference.<br>


## Additional Info
See the sample_images directory and README for using ocr.py component and test cases.<br>
Additional images can be found there (request access if link doesn't work)<br>
https://ucsb.app.box.com/files/0/f/7411611121/Sedgwick_Camera_Traps<br>
The metadata (all file info) file is in this directory entitled Metadata: Sedgwick Camera Traps.xlsx<br>
