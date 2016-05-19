import argparse,datetime,imutils,time,cv2,sys,os
import matplotlib.pyplot as plt
import categorize_pics

DEBUG=True
SSIM_DIFF=0.7
def convert(fname,blur=True):
    '''
    Read in then resize the frame, convert it to grayscale, and blur it and return it (type cv2.Mat)
    '''
    frame = cv2.imread(fname)
    frame = imutils.resize(frame, width=500)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if blur:
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
    return frame
    
######################################
def main():
    '''
    Loop through images in a directory and compare them (mse,ssim) to a base image
    '''

    parser = argparse.ArgumentParser(description='Image Processing')
    #required arguments
    parser.add_argument('base',action='store',help='base empty image')
    parser.add_argument('dir',action='store',help='image to compare to base')
    #optional arguments
    parser.add_argument('--blur','-b',action='store_true',default=False,help='day threshold')
    parser.add_argument('--plot','-p',action='store_true',default=False,help='day threshold')
    args = parser.parse_args()

    base = convert(args.base,args.blur)
    m,p,s = categorize_pics.compare_images(base, base, "Original vs. Original",plot=args.plot)
    if DEBUG: 
        print 'base vs base: m={0},p={1},s={2}'.format(m,p,s)
    sent_size = 0; sent_count = 0
    total_size = 0; total_count = 0
    for root, dirs, files in os.walk(args.dir):
        for file in files:
            if file.endswith('.JPG') or file.endswith('.jpg'):
                fname = '{0}/{1}'.format(root,file)
                if DEBUG:
                    print 'processing {0}'.format(fname)
                total_size += os.path.getsize(fname)
                total_count += 1
                test = convert(fname,args.blur)

                # compare the images
                m,p,s = categorize_pics.compare_images(base, test, 'base vs. {0}'.format(file),plot=args.plot)
                if DEBUG: 
                    print 'base vs {3}: m={0},p={1},s={2}'.format(m,p,s,fname)
                if s < SSIM_DIFF: #images are different enough
                    sent_size += os.path.getsize(fname)
                    sent_count += 1
    print 'Total: {0}, size: {1}, sent: {2}, sentsize: {3}'.format(total_count,total_size,sent_count,sent_size)
            


######################################
if __name__ == "__main__":
    main()
######################################
