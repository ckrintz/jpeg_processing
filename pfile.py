import json, sys, argparse, csv, logging, os, time

DEBUG = False
######################## main ############################
def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='Parse a file of entries that start with Main')
    parser.add_argument('inf',action='store',help='input filename')
    parser.add_argument('outf',action='store',help='output filename')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    args = parser.parse_args()
    DEBUG = args.debug

    with open(args.outf,'wb') as out:    
        with open(args.inf,'rb') as inf:    
	    for line in inf:
	        #parse each Main...JPG entry and write it to a single line
                lst = line.split('Main_')
	        for ele in lst:
                    if ele is not '':
                        out.write('Main_{0}\n'.format(ele))

##################################
if __name__ == '__main__':
    main()
