# jpeg_processing
Image processing, OCR, exim, and box.com upload tools

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

You'll use this filename as an argument below<br>

The following program <br>
	- recursively scans a directory and all of its subdirectories<br>
	- finds all *JPG files<br>
	- extracts the metadata from the JPG <br>

if your python version (python -V) is 2.7 then you can just use python here:<br>

<tt>python2.7 jpeg_processor.py /full/path/to/directory/of/interest sedgwick_map.json meta.csv >& meta.out</tt><br>

meta.csv will be created and will hold details on each file that is processed<br>
meta.out will be created and will hold timings of different operations performed by the program<br>

## Additional Info
See the sample_images directory and README for using ocr.py component and test cases.<br>
Additional images can be found there (request access if link doesn't work)<br>
https://ucsb.app.box.com/files/0/f/7411611121/Sedgwick_Camera_Traps<br>
The metadata (all file info) file is in this directory entitled Metadata: Sedgwick Camera Traps.xlsx<br>
