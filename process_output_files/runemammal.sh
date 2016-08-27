#! /bin/bash

#run the test if no args are passed
if [ $# -eq 0 ]
    then

        python2.7 emammal.py --s3acc='AKIAJK6LLE3WVIB6LZBQ' --s3sec='whKJK7Z0yXxsMyngxcN/j1OF5hh4WZ7c3QDR6+Q7' --s3bkt='incoming-legacy-data' --debug
        exit 0

else #any number of args greater than 0 will work

    python2.7 emammal.py --s3acc='AKIAJK6LLE3WVIB6LZBQ' --s3sec='whKJK7Z0yXxsMyngxcN/j1OF5hh4WZ7c3QDR6+Q7' --s3bkt='incoming-legacy-data' --multimonth --year 2013 --debug >& emammal2013.out

    python2.7 emammal.py --s3acc='AKIAJK6LLE3WVIB6LZBQ' --s3sec='whKJK7Z0yXxsMyngxcN/j1OF5hh4WZ7c3QDR6+Q7' --s3bkt='incoming-legacy-data' --multimonth --year 2014 --debug >& emammal2014.out
    
    python2.7 emammal.py --s3acc='AKIAJK6LLE3WVIB6LZBQ' --s3sec='whKJK7Z0yXxsMyngxcN/j1OF5hh4WZ7c3QDR6+Q7' --s3bkt='incoming-legacy-data' --multimonth --year 2015 --debug >& emammal2015.out

    python2.7 emammal.py --s3acc='AKIAJK6LLE3WVIB6LZBQ' --s3sec='whKJK7Z0yXxsMyngxcN/j1OF5hh4WZ7c3QDR6+Q7' --s3bkt='incoming-legacy-data' --multimonth --year 2016 --debug >& emammal2016.out

fi
