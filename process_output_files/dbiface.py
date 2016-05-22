'''Author: Chandra Krintz, UCSB, ckrintz@cs.ucsb.edu, AppScale BSD license'''
import psycopg2, sys

DEBUG=False

class DBobj(object):
    '''A postgresql instance object
    Attributes:
        conn: A database connection
    '''

    #constructor of a DBobj object
    def __init__(self, dbname, host='localhost'):
        args = "dbname='{0}' user='postgres' host='{1}'".format(dbname,host)
        try:
            self.conn = psycopg2.connect(args)
        except Exception as e:
  	    print e
            print 'Problem connecting to DB'
            sys.exit(1)
    
    #invoke an SQL query on the db
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

    #import a CVS file into a table (empty the table first)
    #we expect that the caller has created the table already with the right schema
    #the table schema must match the CSV columns exactly or there will be error
    def importCSV(self,fname,tname,overwrite=False): 
	#CSV must match db schema exactly
        cur = self.conn.cursor()
        copy_sql = ''
        try:
            if overwrite:
	        #delete the table if it exists
                cur.execute("DELETE FROM {0};".format(tname))

	    #create a temp table that matches tname
	    cur.execute("CREATE TEMP TABLE tmp_table AS SELECT * FROM {0} WITH NO DATA;".format(tname))

	    #account for header if there is one -- this mass copy only works with header 
	    #http://www.postgresql.org/docs/9.2/static/sql-copy.html
            copy_sql = "COPY tmp_table FROM STDIN WITH CSV HEADER DELIMITER as ',';"
	    #avoid getting utf8 errors reading in data
            cur.execute("SET CLIENT_ENCODING TO 'latin1';")
	    #read in the file
            with open(fname, 'r') as f:
                cur.copy_expert(sql=copy_sql, file=f)
                self.conn.commit()

	    #copy the data from tmp_table (if not in tname) to tname then delete tmp_table
	    #sql = "INSERT INTO {0} SELECT DISTINCT ON (dt,ti,pid) * FROM tmp_table ORDER BY dt,ti,pid;".format(tname)
	    sql = "BEGIN; LOCK TABLE {0} IN SHARE ROW EXCLUSIVE MODE; INSERT INTO {0} SELECT * FROM tmp_table tt WHERE NOT EXISTS ( SELECT dt,ti,pid FROM {0} WHERE dt=tt.dt AND ti=tt.ti AND pid=tt.pid ); COMMIT;".format(tname)
	    cur.execute(sql)
	    cur.execute("DROP TABLE tmp_table;".format(tname))
            self.conn.commit()

        except Exception as e:
	    print e
            print 'importCSV: SQL problem:\n\t{0}\n\t'.format(copy_sql,sql)
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


