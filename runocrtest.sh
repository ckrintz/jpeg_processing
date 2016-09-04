#! /bin/bash

export PYTHONPATH=.:ocr_knn/initial_tasks/task3
echo '*************************************'
echo 'pictype 2, Main: should return temp=98'
python2.7 ocrtest.py 2 testimages/main042.JPG #should return temp=98
echo '*************************************'
echo 'pictype 2, Lisque:should return temp=97'
python2.7 ocrtest.py 2 testimages/lisque030.JPG #should return temp=97
echo '*************************************'
echo 'pictype 2, Lisque:should return temp=73'
python2.7 ocrtest.py 2 testimages/lisque2014_029.JPG #should return temp=73
echo '*************************************'
echo 'pictype 2 Blue Schist: should return temp=85'
python2.7 ocrtest.py 2 testimages/blueschist_errpictype2_0550.JPG #should return temp=85
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1 (2014): should return temp=70'
python2.7 ocrtest.py 1 testimages/windmill14_2327.JPG #should return temp=70
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1 (2014): should return temp=91'
python2.7 ocrtest.py 1 testimages/windmill14.JPG #should return temp=91
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1 (2016): should return temp=62'
python2.7 ocrtest.py 1 testimages/windmill0081.JPG #should return temp=62
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1 (2015): should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 1 testimages/windmill15-0495.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1 (2015): should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 1 testimages/windmill15_0091.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 1, Windmill Canyon 1: should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 1 testimages/windmill15.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon Game: should return temp=82'
python2.7 ocrtest.py 2 testimages/windmill16_works_0761.JPG #should return temp=82
echo '*************************************'
echo 'pictype 2, Windmill Canyon Game: should return temp=97'
python2.7 ocrtest.py 2 testimages/windmill16_div0_0284.JPG #should return temp=97
echo '*************************************'
echo 'pictype 2 Vulture: should return temp=92'
python2.7 ocrtest.py 2 testimages/vulture287.JPG #should return temp=92
echo '*************************************'
echo 'pictype ?? Vulture: should return temp=52 - not supported yet'
python2.7 ocrtest.py 2 testimages/vultureMFCD16.JPG #should return temp=52
echo '*************************************'
echo 'pictype 3 Bone Hole: should return temp=78'
python2.7 ocrtest.py 3 testimages/bonehole0609.JPG #should return temp=78
echo '*************************************'
echo 'pictype 1 Bone Trough: should return temp=82'
python2.7 ocrtest.py 1 testimages/bonetrough1878.JPG #should return temp=82
echo '*************************************'
echo 'pictype 2 Northeast: should return temp=59'
python2.7 ocrtest.py 2 testimages/northeast1847.JPG #should return temp=59
echo '*************************************'
echo 'pictype 2 Figueroa: should return temp=84'
python2.7 ocrtest.py 2 testimages/figcreek176.JPG #should return temp=84
echo '*************************************'
echo 'pictype 2 Figueroa: should return temp=71'
python2.7 ocrtest.py 2 testimages/figcreek14_2379.JPG #should return temp=71
echo '*************************************'
echo 'pictype ?? upper reserve: should return temp=-9999 no temp'
python2.7 ocrtest.py 2 testimages/upper_reserve16_1981.JPG #should return temp=-9999
echo '*************************************'
#blueschist_errpictype2_0550.JPG  lisque030.JPG		   vulture287.JPG	windmill15_0091.JPG
#bonehole0609.JPG		 lisque2014_029.JPG	   vultureMFCD16.JPG	windmill15-0495.JPG
#bonetrough1878.JPG		 main042.JPG		   windmill0081.JPG	windmill15.JPG
#figcreek14_2379.JPG		 northeast1847.JPG	   windmill14_2327.JPG	windmill16_div0_0284.JPG
#figcreek176.JPG			 upper_reserve16_1981.JPG  windmill14.JPG	windmill16_works_0761.JPG

