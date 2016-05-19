import argparse,datetime,imutils,time,cv2,sys,os,glob,math
#from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial import distance as dist
from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np

#library used by test.py and image_sim.py

DEBUG=True
index = {} #dictionary to hold the histograms
PIXEL_MAX = 255.0

def mse(imageA, imageB):
    ''' 
    The 'Mean Squared Error' between the two images is the
    sum of the squared difference between the two images;
    NOTE: the two images must have the same dimension
    '''
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    #pnsr = peak signal to noise ratio
    if err == 0:
        pnsr = 100
    else: 
	pnsr = 20 * math.log10(PIXEL_MAX / math.sqrt(err))
    return err,pnsr

def compare_images(imageA, imageB, title, plot=True):
	'''
        Compute the mean squared error and structural similarity
	index for the images
        '''
	m,p = mse(imageA, imageB)
	s = ssim(imageA, imageB)
        if DEBUG:
            print '\tMSE: {0} PNSR: {1} SSIM {2}'.format(m,p,s)
        if not plot:
            return m,p,s
 
	# setup the figure
	fig = plt.figure(title)
	plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
 
	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
	plt.axis("off")
 
	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")
 
	# show the images
	plt.show()
        return m,p,s

def get_image(fname):
    '''
    Read in then resize the image, convert it to grayscale, and blur it and return it (type cv2.Mat)
    '''
    frame = cv2.imread(fname)
    frame = imutils.resize(frame, width=500)
    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame,grayframe

######################################
def convert(fname):
    '''
    Process image and compute its grayscale histogram and store it
    ''' 
    _,frame = get_image(fname)
    hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    #if fname in index:
        #print 'Error, duplicate file names: {0}'.format(fname)
    index[fname] = hist
    return frame
    
######################################
def get_clusters(basename,dirname,methodID,numClusters):
    base = convert(basename)
    if DEBUG:
        cv2.imshow("Base",base)

    fnbase = os.path.basename(basename)
    for fn in os.listdir(dirname):
        if fn.endswith(".JPEG") or fn.endswith(".JPG") or fn.endswith(".jpg") or fn.endswith(".jpeg"):
            #if fn.endswith(fnbase):
                #continue
            if "Empty" in fn: #will catch all possible base files
                continue
  
            fn = '{0}/{1}'.format(dirname,fn)
            print 'processing file: {0}'.format(fn)
            #process the file 
            test = convert(fn)

    results = {}
    for (k, hist) in index.items():
	# compute the distance between the two histograms
	# using the method and update the results dictionary
	# enumeration assumed in http://docs.opencv.org/3.0-beta/modules/imgproc/doc/histograms.html
        # in testing: 0-5 works, 0 and 3 higher is better (correl and intersection, rest lower is better
	# 1=chisqr, 2=chisqr_alt, 4=bhattacharya/hellinger, 5=Kullback-Leibler divergence
	d = cv2.compareHist(index[basename], hist, methodID) #4=Bhattacharyya (0 base assumed)
	results[k] = d
 
    # sort the results - turns results into a list from a dictionary
    results = sorted([(v, k) for (k, v) in results.items()])
    vals = np.reshape([v for (v,k) in results],(-1,1))
    clt = KMeans(n_clusters = numClusters)
    clt.fit(vals)
    if DEBUG:
        print clt.labels_
    return clt,results

######################################
def main():
    '''
    '''

    parser = argparse.ArgumentParser(description='Image Processing')
    #required arguments
    parser.add_argument('base',action='store',help='base empty image')
    parser.add_argument('dir',action='store',help='directory with images to compare to base (compares all except if it has the same name as the base)')
    #optional arguments
    parser.add_argument('--method',action='store',default=4,type=int,help='compareHist method ID')
    parser.add_argument('--clusters','-c',action='store',default=4,type=int,help='K in K-means')
    args = parser.parse_args()

    clt,results = get_clusters(args.base,args.dir,args.method,args.clusters)

    for (i, (v, k)) in enumerate(results):
        #k is the file name
        name = '{0}_{1}'.format(k,v)
        print '{0}, {1}, {2}, {3}'.format(i,k,v,clt.labels_[i])

        
######################################
if __name__ == "__main__":
    main()
######################################
