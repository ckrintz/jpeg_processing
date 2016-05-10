# jpeg_processing
Image processing, OCR, exim, and box.com upload tools

## Setup Steps
A) Install python2.7<br>
python -V<br>
Python 2.7.10<br>

If the above does not print 2.7.something then make sure and use python2.7:<br>
python2.7 -V <br>
Python 2.7.10<br>

B) Install pip2.7 (you may need to prefix with sudo (for which you need admin priviledges to run))
//install pip: sudo yum install python-pip
pip --upgrade pip

C) install packages
you may need to prefix with sudo (for which you need admin priviledges to run)

pip2.7 install boxsdk pytesseract Pillow oauth2client httplib2 flask numpy scipy scikit-learn scikit-image python-jose matplotlib
pip2.7 install -U numpy scipy scikit-learn
sudo yum install libffi-devel
sudo pip2.7 install urllib3 pyopenssl ndg-httpsclient pyasn1
# I may have missed some

sudo yum install tesseract
sudo pip2.7 install --upgrade httplib2 requests exifread imutils

install cv2 for python:

switch to root: sudo -s
Assuming Linux Centos6
wget http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/3.1.0/opencv-3.1.0.zip?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fopencvlibrary%2F&ts=1462070500&use_mirror=pilotfiber
unzip opencv-3.1.0.zip
mv opencv-3.1.0.zip\?r\=https\:%2F%2Fsourceforge.net%2Fprojects%2Fopencvlibrary%2F opencv-3.1.0.zip
unzip opencv-3.1.0.zip 
cd opencv-3.1.0
mkdir -p build
cd build

which python2.7
	/opt/rh/python27/root/usr/bin/python2.7
find /opt/rh -name libpython2.7.so -print
	/opt/rh/python27/root/usr/lib64/libpython2.7.so
Whatever the output above displays, replace the full path with the full paths to python2.7 in these variables in the cmake command
-DPYTHON_EXECUTABLE=
-DPYTHON_INCLUDE_DIR=
-DPYTHON_LIBRARY= 
-DPYTHON_NUMPY_INCLUDE_DIR
-DPYTHON_PACKAGES_PATH

cmake ../ -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_EXAMPLES=ON -DBUILD_NEW_PYTHON_SUPPORT=ON -DINSTALL_PYTHON_EXAMPLES=ON -DPYTHON_EXECUTABLE=/opt/rh/python27/root/usr/bin/python2.7 -DPYTHON_INCLUDE_DIR=/opt/rh/python27/root/usr/include/python2.7 -DPYTHON_LIBRARY=/opt/rh/python27/root/usr/lib64/libpython2.7.so -DPYTHON_NUMPY_INCLUDE_DIR=/opt/rh/python27/root/usr/lib64/python2.7/site-packages/numpy/core/include/ -DPYTHON_PACKAGES_PATH=/opt/rh/python27/root/usr/lib64/python2.7/site-packages -DBUILD_PYTHON_SUPPORT=ON

make
make install

yum install numpy opencv*
cp /usr/local/lib/python2.7/site-packages/cv2.so /opt/rh/python27/root/usr/lib/python2.7/site-packages/

test as normal user:
exit 
python2.7
import cv2
//working if no error
quit()

