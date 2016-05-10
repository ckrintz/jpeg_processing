'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''

import argparse,datetime,imutils,time,cv2,sys,os,subprocess,string,random
import pytesseract
from PIL import Image

DEBUG=False
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def convert(fname,size,blur=True):
    '''
    Read in then resize the frame, convert it to grayscale, and blur it and return it (type cv2.Mat)
    '''
    frame = cv2.imread(fname)
    if size > 0:
        frame = imutils.resize(frame, width=size)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if blur:
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
    return frame
    
######################################
def main():
    '''
    '''

    parser = argparse.ArgumentParser(description='OCR for Sedgwick JPEG Temp')
    #required arguments
    parser.add_argument('pictype',action='store',type=int,help='1,2,3')
    parser.add_argument('base',action='store',help='JPEG image')
    #optional arguments
    #parser.add_argument('--blur','-b',action='store',default=False,type=bool,help='day threshold')
    args = parser.parse_args()
    if args.pictype < -1 and args.pictype > 3:
	#0 is hidden and used for testing
        print 'pictype must be 1,2, or 3'
        sys.exit(1)

    temp,err,basef,roi = process_pic(args.pictype, args.base)

    #turn on DEBUG to see outcome
    if DEBUG:
        print '(x,y) of base image: {0}'.format(basef.shape)
        #(750, 1000, 3) for 1000
        #(2250, 3000) for 3000
        #orig: 2448,3264
        print '(x,y) of roi: {0}'.format(roi.shape)

        cv2.imshow("Base",basef)
        cv2.imshow("cropped", roi)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print 'temp is: {0}, trustworthy_if_false: {1}'.format(temp,err)

######################################
def process_pic(pictype,base):

    #Convert the picture to grayscale and crop down the temp characters
    #this location is in 3 different places (3 different photo formats)
    #specified by pictype (1,2, or 3)
    #turn on DEBUG to see outcome
    
    #orig: 2448,3264
    if pictype == 0: #testing/debugging
        basef = convert(base, 3000, False)
        #(750, 1000, 3) for 1000
    else: 
        #1000 is too small for ocr to work
        #basef = convert(base, -1, False)
        basef = convert(base, 3000, False)
        #(2250, 3000) for 3000

    #rows, cols, channels
    #height, width, _ = basef.shape #color, if grayscale, no 3rd result
    height, width = basef.shape #grayscale
    #x,y = (0,0) is top left, x is left->right, y is top->bottom

    if pictype == 0:
        #windmill temp in F for width=3000, height 2250
        y = 2160
        h = height-10
        x = 750
        w = x+68
    elif pictype == 1:
        #Bushnell: Bone in 
        #../2014\ -\ 2015\ Sedgwick\ Pictures
	#also 
        y = 2160
        h = height #-10
        #x = 730
        #w = x+61
        x = 710
        #w = x+110
        w = x+115
    elif pictype == 2:
	#Hyperfire: Blue, Figueroa, Lisque, main, northeast, vulture
        y = 0
        h = y+50
        x = width-290
        w = width-150
    elif pictype == 3:
	#Other: Bone15rcnx
        y = 0
        h = y+50
        #x = 350
        #w = x+40
        x = 340
        w = x+50
    else:
        print 'pictype must be 1-3, please retry with new value'
        return None,True,None,None

    #crop: img[y: y + h, x: x + w]
    #orig: roi = basef[0:2448, 0:3264]
    #orig_resized_1000w: roi = basef[0:750, 0:1000]
    roi = basef[y:h, x:w]
    #image is stored in tempXXX.png -- make sure XXX is unique so that multiple programs can call this method at the same time
    fname = 'temp{0}.png'.format(id_generator())
    cv2.imwrite(fname,roi)
    temp,err = get_temp(pictype,fname)
    #clean up temp file
    os.remove(fname)

    return temp,err,basef,roi

######################################
def get_temp(pictype,rioname):

    #extract the temperature from the cropped image using OCR
    err = False
    im = Image.open(rioname)
    s = pytesseract.image_to_string(im)
    s = s.strip()
    if DEBUG:
        print 's len: {0}'.format(len(s))
        print 's: {0}'.format(s)

    swapmap = {}
    if len(s) > 1:
        if s[0] == 'B':
            #s[i] = '6' 
            swapmap['0'] = '6'
            err = True        
        if s[0] == 'S':
            #s[i] = '9' 
            swapmap['0'] = '9'
            err = True        
    if len(s) > 1:
        idx = len(s) #just to be safe (when there are no extra characters)
        for i in range(1,len(s)): #assume first char is either - or 1-9 and skip
	    #loop until a non-numeric char is found
            c = s[i]
            if c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '0':
                #cut off string here, and break out of loop
                if DEBUG:
                    print 'index {0} is nonnum: {1}'.format(i,c)
                #risky, but 6s are reported as Bs and 9s as Ss, correct for it
		if c == 'B':
                    #s[i] = '6' 
                    swapmap[str(i)] = '6'
                    err = True        
                    continue
		if c == 'S':
                    #s[i] = '9' 
                    swapmap[str(i)] = '9'
                    err = True        
                    continue
                idx = i
                break
        #chop off non-numeric chars on end (x:y, y is upto index but not including)
        s = s[:idx]
        if DEBUG:
                print 'updated s: {0}'.format(s)
        for idx in swapmap:
            #replace index idx with swapmap[idx]
            i = int(idx)
            if DEBUG:
                print 'replacing {0} with {1}'.format(s[i],swapmap[idx])
            new_s = s[:i] + swapmap[idx] + s[i + 1:]
            s = new_s
            if DEBUG:
                print 'new_s {0}'.format(s)
        if DEBUG:
            print 'idx: {0} new s: {1}'.format(idx,s)
    if len(s) == 0:
        s = '?'
        err = True #something is wrong or missing value

    if DEBUG:
        print 's.strip: ', s.strip()
    return s.strip(),err

######################################
if __name__ == "__main__":
    main()
######################################
