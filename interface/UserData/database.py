import sqlite3
from sqlite3 import Error
import pandas as pd

database_name = "data.db"

def create_db():
    conn = None
    try:
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        # Create database for hand gesture task progress
        c.execute('''
                CREATE TABLE IF NOT EXISTS Gesture_Task1(
                    gesture_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    completion_date TEXT NOT NULL
                );
                ''')
        c.execute('''
                CREATE TABLE IF NOT EXISTS Gesture_Task2(
                    gesture_name TEXT NOT NULL,
                    status BOOLEAN NOT NULL,
                    duration INTEGER NOT NULL,
                    completion_date TEXT NOT NULL
                );
                ''')
        
        # Create database for user information
        c.execute('''
                    CREATE TABLE IF NOT EXISTS User(
                        username TEXT PRIMARY KEY,
                        start_date TEXT NOT NULL
                    );
                    ''')
        
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()
    
def retrieve_user_info():
    conn = sqlite3.connect(database_name)
    user_data_query = 'SELECT * FROM User;'
    user_data_df = pd.read_sql_query(user_data_query, conn)
    conn.close()
    return user_data_df

def retrieve_table_info():
    conn = sqlite3.connect(database_name)
    sql_query = """SELECT name FROM sqlite_master 
    WHERE type='table';"""
    c = conn.cursor()
    c.execute(sql_query)
    tables = c.fetchall()
    print("list all tables: \n {}".format(tables))
    for table in tables:
        retrieve_tableData_info(table)
    
    conn.close()
    
def retrieve_tableData_info(table_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(table_name[0]))
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

def retrieve_gesture_score_task1(gesture_name):
    conn = sqlite3.connect(database_name)
    user_data_query = 'SELECT score FROM Gesture_Task1 WHERE gesture_name = "{}";'.format(gesture_name)
    user_data_df = pd.read_sql_query(user_data_query, conn)
    conn.close()
    return user_data_df

def retrieve_gesture_status_task2(gesture_name):
    conn = sqlite3.connect(database_name)
    user_data_query = 'SELECT status FROM Gesture_Task2 WHERE gesture_name = "{}";'.format(gesture_name)
    user_data_df = pd.read_sql_query(user_data_query, conn)
    conn.close()
    return user_data_df

def retrieve_gesture_duration_task2(gesture_name):
    conn = sqlite3.connect(database_name)
    user_data_query = 'SELECT duration FROM Gesture_Task2 WHERE gesture_name = "{}";'.format(gesture_name)
    user_data_df = pd.read_sql_query(user_data_query, conn)
    conn.close()
    return user_data_df

def calculate_error_rate_task1(gesture_name):
    gesture_score = retrieve_gesture_score_task1(gesture_name)
    trial = len(gesture_score)
    if gesture_score.empty:
        return None
    else:
        total_score = gesture_score.sum().values[0]
        full_score = trial * 4
        error_rate = (full_score - total_score) / full_score
        return error_rate

def calculate_error_rate_task2(gesture_name):
    gesture_status = retrieve_gesture_status_task2(gesture_name)
    trial = len(gesture_status)
    if gesture_status.empty:
        return None
    else:
        fail_trials = (gesture_status['status'] == False).sum()
        error_rate = fail_trials / trial
        return error_rate

def populate_test_data():
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    
    user_data = [
        ('test_user1', '2022-01-01'),
    ]
    c.execute('DELETE FROM User')
    c.executemany('INSERT INTO User VALUES (?, ?)', user_data)

    gesture_task1_data = [
        ('gesture1', 4, '2022-05-01'),
        ('gesture1', 3, '2022-05-02'),
        ('gesture1', 2, '2022-05-03'),
    ]
    c.execute('DELETE FROM Gesture_Task1')
    c.executemany('INSERT INTO Gesture_Task1 VALUES (?, ?, ?)', gesture_task1_data)

    gesture_task2_data = [
        ('gesture1', True, 120, '2022-05-01'),
        ('gesture1', False, 150, '2022-05-02'),
        ('gesture1', True, 130, '2022-05-03'),
    ]
    c.execute('DELETE FROM Gesture_Task2')
    c.executemany('INSERT INTO Gesture_Task2 VALUES (?, ?, ?, ?)', gesture_task2_data)

    conn.commit()
    conn.close()

# Test case functions
def test_retrieve_user_info():
    user_data_df = retrieve_user_info()
    print("User data retrieved:", user_data_df)
    assert user_data_df.shape[0] == 1
    assert user_data_df.iloc[0]['username'] == 'test_user1'

def test_retrieve_gesture_score_task1():
    scores = retrieve_gesture_score_task1('gesture1')
    print("Scores retrieved from Gesture_Task1:", scores)
    assert scores.shape[0] == 3
    assert scores['score'].tolist() == [4, 3, 2]

def test_retrieve_gesture_status_task2():
    statuses = retrieve_gesture_status_task2('gesture1')
    print("Statuses retrieved from Gesture_Task2:", statuses)
    assert statuses.shape[0] == 3
    assert statuses['status'].tolist() == [True, False, True]

def test_retrieve_gesture_duration_task2():
    durations = retrieve_gesture_duration_task2('gesture1')
    print("Durations retrieved from Gesture_Task2:", durations)
    assert durations.shape[0] == 3
    assert durations['duration'].tolist() == [120, 150, 130]

def test_calculate_error_rate_task1():
    error_rate = calculate_error_rate_task1('gesture1')
    print("Error rate for Gesture_Task1:", error_rate)
    assert error_rate == 0.25  # Total score: 9, Full score: 12, Error rate: (12 - 9) / 12

def test_calculate_error_rate_task2():
    error_rate = calculate_error_rate_task2('gesture1')
    print("Error rate for Gesture_Task2:", error_rate)
    assert error_rate == 1/3  # One failure out of three trials

def teardown_test_db():
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    
    c.execute('DROP TABLE IF EXISTS User')
    c.execute('DROP TABLE IF EXISTS Gesture_Task1')
    c.execute('DROP TABLE IF EXISTS Gesture_Task2')
    
    conn.commit()
    conn.close()

def test_database():
    create_db()
    populate_test_data()
    
    test_retrieve_user_info()
    test_retrieve_gesture_score_task1()
    test_retrieve_gesture_status_task2()
    test_retrieve_gesture_duration_task2()
    test_calculate_error_rate_task1()
    test_calculate_error_rate_task2()
    
    teardown_test_db()
    print("All tests passed!")

if __name__ == "__main__":
    create_db()
    # retrieve_table_info()
    