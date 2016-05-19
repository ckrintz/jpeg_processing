'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''
import psycopg2, sys

DEBUG=False

class DBobj(object):
    '''A postgresql instance object
    Attributes:
        conn: A database connection
    '''

    def __init__(self, dbname, host='localhost'):
        args = "dbname='{0}' user='postgres' host='{1}'".format(dbname,host)
        try:
            self.conn = psycopg2.connect(args)
        except Exception as e:
  	    print e
            print 'Problem connecting to DB'
            sys.exit(1)
    
    def execute_sql(self,sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
        except Exception as e:
	    print e
            print 'execute_sql: SQL problem:\n\t{0}'.format(sql)
            sys.exit(1)
        return cur

    def commit(self):
        return self.conn.commit()

    def getCursor(self):
        return self.conn.cursor()

    def importCSVwHeader(self,fname,tname): #CSV file has a header line/row
	#CSV must match db schema exactly
        cur = self.conn.cursor()
        copy_sql = ''
        try:
	    #delete the table if it exists
            cur.execute("DELETE FROM {0};".format(tname))
            cur.execute("SET CLIENT_ENCODING TO 'LATIN1';")
            copy_sql = "COPY {0} FROM stdin WITH CSV HEADER DELIMITER as ',';".format(tname)
            with open(fname, 'r') as f:
                cur.copy_expert(sql=copy_sql, file=f)
                self.conn.commit()
        except Exception as e:
	    print e
            print 'importCSVwHeader: SQL problem:\n\t{0}'.format(copy_sql)
            sys.exit(1)

    def appendCSV(self,fname,tname): #CSV file has no header
	#CSV must match db schema exactly
        cur = self.conn.cursor()
        try: 
            with open(path, 'r') as f:
 	            #disallows adding repeat keys
                cur.copy_from(f, tname, sep=',')
                self.conn.commit()
        except Exception as e:
	    print e
            print 'appendCSV: SQL problem (copy_from)'
            sys.exit(1)

    def closeConnection(self):
        if self.conn:
	    self.conn.close()

def main():
    
    db = DBobj('wtbdb')
    cur = db.getCursor()
    cur.execute('SELECT version()')          
    ver = cur.fetchone()
    print ver 

    db.closeConnection()
    

if __name__ == '__main__':
    main()


