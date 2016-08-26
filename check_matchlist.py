import json, sys, argparse, csv, logging, os, time
DEBUG=True

def main():
    global DEBUG
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Check matchlist file by printing out entries')
    parser.add_argument('--debug',action='store_true',default=False,help='Turn debugging on (default: off)')
    parser.add_argument('--matchlist',action='store',default=None,help='Filename for matchlist to use')
    args = parser.parse_args()
    DEBUG = args.debug

    print 'Matchlist:'
    if os.path.isfile(args.matchlist):
        with open(args.matchlist,'rb') as ml_file:    
            count = 0
            for entry in ml_file:
		if len(entry.strip()) > 0 and entry is not '' and entry is not ' ':
                    print '{0}, size: {1}'.format(entry.strip(),len(entry.strip()))
                else:
                    count += 1
            print 'number of empty entries: {0}'.format(count)
    else: 
        print 'error {0} does not exist'.format(args.matchlist)
    print '<EOF>'

##################################
if __name__ == '__main__':
    main()
