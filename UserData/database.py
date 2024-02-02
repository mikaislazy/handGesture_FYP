import sqlite3
from sqlite3 import Error
import pandas as pd

def create_db():
    try:
        conn = sqlite3.connect('UserData/data.db')
        c = conn.cursor()
        # create database for hand gesture task progress
        c.execute('''
                CREATE TABLE IF NOT EXISTS  Gesture_Task1(
                    gesture_name TEXT NOT NULL,
                    gesture_id INTEGER  PRIMARY KEY,
                    err_rate INTEGER NOT NULL,
                    status BOOLEAN NOT NULL,
                    duration INTEGER NOT NULL,
                    completion_date TEXT NOT NULL
                    );
                ''')
        c.execute('''
                CREATE TABLE IF NOT EXISTS  Gesture_Task2(
                    gesture_name TEXT NOT NULL,
                    gesture_id INTEGER  PRIMARY KEY,
                    err_rate INTEGER NOT NULL,
                    status BOOLEAN NOT NULL,
                    duration INTEGER NOT NULL,
                    completion_date TEXT NOT NULL
                    );
                ''')
        
        # create database for user information
        c.execute('''
                    CREATE TABLE IF NOT EXISTS  User(
                        username TEXT PRIMARY KEY,
                        start_date TEXT NOT NULL
                        );
                    ''')
        user_data = [
            ('user1',  '2022-01-01'),
        ]
        c.executemany('INSERT INTO User VALUES (?, ?)', user_data)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()
    
def retrieve_user_info():
    # Connect to the SQLite database
    conn = sqlite3.connect('UserData/data.db')

    # Query to retrieve user data
    user_data_query = 'SELECT * FROM User;'
    user_data_df = pd.read_sql_query(user_data_query, conn)


    # Close the connection
    conn.close()
    return user_data_df

def retrieve_table_info():
    # Connect to the SQLite database
    conn = sqlite3.connect('UserData/data.db')

    # Query to retrieve table
    sql_query = """SELECT name FROM sqlite_master 
    WHERE type='table';"""
    c = conn.cursor()
    c.execute(sql_query)
    print("list all tables: \n {}".format(c.fetchall()))
    conn.close()
    


if __name__ == '__main__':
    # create_db()
    # print(retrieve_user_info())
    retrieve_table_info()