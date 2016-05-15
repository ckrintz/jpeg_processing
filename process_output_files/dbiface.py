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
        except:
            print 'Problem connecting to DB'
            sys.exit(1)
    
    def getCursor(self):
        return self.conn.cursor()

    def importCSVwHeader(self,fname):
        cur = self.conn.cursor()
        copy_sql = """
           COPY table_name FROM stdin WITH CSV HEADER
           DELIMITER as ','
           """
        with open(path, 'r') as f:
            cur.copy_expert(sql=copy_sql, file=f)
            conn.commit()

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


