import sqlite3
from matrixEngine import MatrixGPT

try:

	# Connect to DB and create a cursor
	sqliteConnection = sqlite3.connect('../matrix.db')
	cursor = sqliteConnection.cursor()
	print('DB Init')
	#cursor.execute('''DROP TABLE transcript;''')

	""" cursor.execute('''CREATE TABLE transcript( 
				ID INTEGER PRIMARY KEY,
                CALL_DETAILS TEXT, 
                DATE_OF_CALL TEXT,
                DURATION INTEGER,
                SUMMARY TEXT,
                SENTIMENT TEXT,
                CATEGORY TEXT,
                EMOTION TEXT,
                KEYWORDS TEXT );''')  """
	
	cursor.execute('''DELETE FROM TRANSCRIPT WHERE CATEGORY=""''')
	#MatrixGPT.add_to_DB(cursor,'../calldetails.xlsx')
	sqliteConnection.commit()
	# Close the cursor
	cursor.close()

# Handle errors
except sqlite3.Error as error:
	print('Error occurred - ', error)

# Close DB Connection irrespective of success
# or failure
finally:

	if sqliteConnection:
		sqliteConnection.close()
		print('SQLite Connection closed')
