
import mysql.connector
from mysql.connector import errorcode
from app.config import databaseCfg

HOSTNAME = databaseCfg.get("host")
DATABASE = databaseCfg.get("database")
USER = databaseCfg.get("user")
PASSWD = databaseCfg.get("password")

db = mysql.connector.connect(host=HOSTNAME,
                            database=DATABASE,
                            user=USER,
                            password=PASSWD)

def data_exits(sql_stmt, value):
  if db.is_connected():
    print("Database Connected")
  try:
    cursor = db.cursor()
    cursor.execute(sql_stmt, value)
    result = cursor.fetchall() 
    return result[-1][-1]
  except:
    return 0

def fetch_data(sql_stmt, value):
  if db.is_connected():
    print("Database Connected")
  cursor = db.cursor()
  try:
    cursor.execute(sql_stmt, value) 
    result = cursor.fetchall() 
    return result
  except mysql.connector.Error as err: 
    print("Exception raised while processing the request:",err.errno,err) 
    raise

def insert_update_data(sql_stmt, values):
  if db.is_connected():
    print("Database Connected")
  cursor = db.cursor()
  try:
    cursor.execute(sql_stmt, values)
    db.commit()
    print("{} data Inserted".format(cursor.rowcount))

  except mysql.connector.Error as err: 
    print("Exception raised while processing the request:",err.errno,err) 
    raise
    
  


