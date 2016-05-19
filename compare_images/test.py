import argparse,datetime,imutils,time,cv2,sys,os
import matplotlib.pyplot as plt
import categorize_pics

DEBUG=True
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
    '''

    parser = argparse.ArgumentParser(description='Image Processing')
    #required arguments
    parser.add_argument('base',action='store',help='base empty image')
    parser.add_argument('pic',action='store',help='image to compare to base')
    #optional arguments
    parser.add_argument('--blur','-b',action='store',default=False,type=bool,help='day threshold')
    parser.add_argument('--min_area','-m',action='store',default=500,type=int,help='minimum area to consider as a new creature in pixels')
    parser.add_argument('--thresh','-t',action='store',default=100,type=int,help='day threshold')
    parser.add_argument('--x1',action='store',default=0,type=int,help='top left x in pixels')
    parser.add_argument('--y1',action='store',default=0,type=int,help='top left y in pixels')
    parser.add_argument('--x2',action='store',default=0,type=int,help='bottom right x in pixels')
    parser.add_argument('--y2',action='store',default=0,type=int,help='bottom right y in pixels')
    args = parser.parse_args()

    base = convert(args.base,args.blur)
    #grab the original from test to draw the box on later
    basef = cv2.imread(args.base)
    basef = imutils.resize(basef, width=500)
    test = convert(args.pic,args.blur)
    #grab the original from test to draw the box on later
    frame = cv2.imread(args.pic)
    frame = imutils.resize(frame, width=500)

    ''' only if you want to look at them
    # initialize the figure
    fig = plt.figure("Images")
    images = ("Original", base), ("Contrast", test)
 
    # loop over the images
    for (i, (name, image)) in enumerate(images):
	    # show the image
	    ax = fig.add_subplot(1, 3, i + 1)
	    ax.set_title(name)
	    plt.imshow(image, cmap = plt.cm.gray)
	    plt.axis("off")
 
    # show the figure
    plt.show()
    '''

    # compare the images
    print 'Base vs Base:'
    categorize_pics.compare_images(base, base, "Original vs. Original",plot=False)
    print 'Base vs Test:'
    categorize_pics.compare_images(base, test, "Original vs. Contrast",plot=False)

    
    height, width = base.shape #binary images have no 3rd dim (channels)
    print 'Base height {0} and width {1}'.format(height,width)
    #(0,0) is top left, x is left->right, y is top->bottom
    #(x1,y1) as the top-left vertex and (x2,y2) is bottom-right
    #width is set above to be 500 - which make height 281
    #x1=0; y1=0; x2=width; y2=height  #as it is now
    #tested for lisque dark
    #x1=50; y1=80; x2=width-50; y2=height
    #tested for figcreek day
    #x1=100; y1=50; x2=width-100; y2=250  
    x1=args.x1; y1=args.y1; x2=args.x2; y2=args.y2  #as it is now
    if x2 == 0:
        x2 = width
    if y2 == 0:
        y2 =height
    roi = base[y1:y2, x1:x2]
    roinew = test[y1:y2, x1:x2]

    # compare the images
    print 'Base vs Base:'
    categorize_pics.compare_images(roi, roi, "Original vs. Original",plot=False)
    print 'Base vs Test:'
    categorize_pics.compare_images(roi, roinew, "Original vs. Contrast",plot=False)

    if DEBUG:
        cv2.imshow("Base",basef)
        cv2.imshow("Test",frame)
        cv2.imshow("cropped", roi)
        cv2.imshow("cropped new", roinew)
    
    # compute the absolute difference between the base and new test image
    #frameDelta = cv2.absdiff(base, test)
    frameDelta = cv2.absdiff(roi, roinew)
    #these params can/should be tuned or our app!
    #thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.threshold(frameDelta, args.thresh, 255, cv2.THRESH_BINARY)[1]
    min_area = args.min_area

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    #(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print 'min_area: {0}'.format(args.min_area)
    text = 'No Contours'
    # loop over the contours
    roinew = frame[y1:y2, x1:x2]
    for c in cnts:
	# if the contour is too small, ignore it
	if cv2.contourArea(c) < args.min_area:
	    continue

	# compute the bounding box for the contour, draw it on the frame,
	# and update the text
	(x, y, w, h) = cv2.boundingRect(c)
	#cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
	cv2.rectangle(roinew, (x, y), (x + w, y + h), (0, 255, 0), 2)
	text = "Occupied"

    # draw the text and timestamp on the frame
    #changed to roinew from frame
    cv2.putText(roinew, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(roinew, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, roinew.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", roinew)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    cv2.waitKey(0)

######################################
if __name__ == "__main__":
    main()
######################################
