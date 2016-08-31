#! /bin/bash

export PYTHONPATH=.:ocr_knn/initial_tasks/task3
echo '*************************************'
echo 'pictype 2, Main: should return temp=98'
python2.7 ocrtest.py 2 testimages/main042.JPG #should return temp=98
echo '*************************************'
echo 'pictype 2, Lisque:should return temp=97'
python2.7 ocrtest.py 2 testimages/lisque030.JPG #should return temp=97
echo '*************************************'
echo 'pictype 2 Blue Schist: should return temp=85'
python2.7 ocrtest.py 2 testimages/blueschist_errpictype2_0550.JPG #should return temp=85
echo '*************************************'
echo 'pictype 1, Blue Schist: should return temp=-9999 (wrong pictype)'
python2.7 ocrtest.py 1 testimages/blueschist_errpictype2_0550.JPG #wrong pictype should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=62'
python2.7 ocrtest.py 2 testimages/windmill0081.JPG #should return temp=62
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=-9999 (wrong pictype)'
python2.7 ocrtest.py 2 testimages/windmill0081.JPG #wrong pictype, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 1 testimages/windmill15-0495.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 2 testimages/windmill15-0495.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 3 testimages/windmill15-0495.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon 1: should return temp=-9999 (has no temp)'
python2.7 ocrtest.py 1 testimages/windmill15.JPG #has no temp, should return -9999
echo '*************************************'
echo 'pictype 2, Windmill Canyon Game: should return temp=82'
python2.7 ocrtest.py 2 testimages/windmill16_works_0761.JPG #should return temp=82
echo '*************************************'
echo 'pictype 2, Windmill Canyon Game: should return temp=97'
python2.7 ocrtest.py 2 testimages/windmill16_div0_0284.JPG #should return temp=97
echo '*************************************'
echo 'pictype 2, Windmill Canyon Game: should return temp=-9999 (wrong pictype)'
python2.7 ocrtest.py 1 testimages/windmill16_works_0761.JPG #wrong pictype, should return -9999
echo '*************************************'
echo 'pictype 2 Vulture: should return temp=92'
python2.7 ocrtest.py 2 testimages/vulture287.JPG #should return temp=92
echo '*************************************'
echo 'pictype 3 Bone Hole: should return temp=78'
python2.7 ocrtest.py 3 testimages/bonehole0609.JPG #should return temp=78
echo '*************************************'
echo 'pictype 2 Bone Hole: should return temp=-9999 (wrong pictype)'
python2.7 ocrtest.py 3 testimages/bonehole0609.JPG #should return temp=-9999 (wrong pictype)
echo '*************************************'
echo 'pictype 1 Bone Trough: should return temp=82'
python2.7 ocrtest.py 1 testimages/bonetrough1878.JPG #should return temp=82
echo '*************************************'
echo 'pictype 3 Bone Trough: should return temp=-9999 (wrong pictype)'
python2.7 ocrtest.py 3 testimages/bonetrough1878.JPG #should return temp=-9999
echo '*************************************'
