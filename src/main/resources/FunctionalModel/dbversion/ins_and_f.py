import os
import sys
import MySQLdb as mdb
from ins import ins_process
from filtrate import filtrate

db = mdb.connect('localhost', 'root', 'wws85583813')
cursor = db.cursor()
cursor.execute("DROP SCHEMA IF EXISTS `cnPlane`;")
cursor.execute("CREATE SCHEMA `cnPlane`;")
db.close()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sales_path = sys.argv[1]
status_path = os.path.join(os.path.dirname(BASE_DIR), 'uploads/status.txt')
status = open(status_path,'w')
status.write('wait')
print('wait')
status.close()
size = ins_process(sales_path)
filtrate(sales_path, size)
status = open(status_path,'w')
status.write('go')
print('go')
status.close()
