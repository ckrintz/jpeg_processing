import dbiface


DEBUG=False
def main():
    cur = dbiface.getConnection('wtbdb')
    cur.execute('SELECT version()')          
    ver = cur.fetchone()
    print ver 

    dbiface.closeConnection()
    

    

if __name__ == '__main__':
    main()
