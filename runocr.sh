#! /bin/bash
#run the test if no args are passed
export PYTHONPATH=.:ocr_knn/initial_tasks/task3/
if [ $# -eq 0 ]
    then
        #test
        /usr/bin/time python2.7 jpeg_processor.py --newocr --noupload ./emammal/ sedgwick_map.json test.csv
        exit 0
fi

#echo "CJK: OCR as a service"
###/usr/bin/time python2.7 jpeg_processor.py --noupload --newocr --ocrservice 8080 ../photos2/ main_map.json noupload_mainNew2.csv
/usr/bin/time python2.7 jpeg_processor.py --noupload --newocr --checklist list.txt --ocrservice 8080 ../photos2/ main_map.json noupload_mainNew2rest.csv
#/usr/bin/time python2.7 jpeg_processor.py --newocr --noupload ../photos2/ sedgwick_map.json noupload_all2.csv 
#echo "CJK: NEW OCR"
#/usr/bin/time python2.7 jpeg_processor.py --newocr --noupload ../photos2/ main_map.json noupload_mainNew.csv 
#echo "CJK: ORIG OCR"
#/usr/bin/time python2.7 jpeg_processor.py --noupload ../photos2/ sedgwick_map.json noupload_all2orig.csv 
