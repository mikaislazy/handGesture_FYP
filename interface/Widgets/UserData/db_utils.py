import sqlite3
from sqlite3 import Error
import pandas as pd
from  datetime import date
import os
# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model file
database_name = "data.db"
database_name  = os.path.join(current_dir, database_name)

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
        
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()



def retrieve_table_info():
    conn = sqlite3.connect(database_name)
    sql_query = """SELECT name FROM sqlite_master 
    WHERE type='table';"""
    c = conn.cursor()
    c.execute(sql_query)
    tables = c.fetchall()
    print("list all tables: \n {}".format(tables))
    for table in tables:
        print("table: {}".format(table[0]))
        retrieve_tableData_info(table[0])
    
    conn.close()
    
def retrieve_tableData_info(table_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(table_name))
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

def retrieve_gesture_score_task1(gesture_name):
    # print("database_name:", database_name)
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

# calculation function
def calculate_error_rate_task1(gesture_name):
    gesture_score = retrieve_gesture_score_task1(gesture_name)
    trial = len(gesture_score)
    if gesture_score.empty:
        return None
    else:
        # total_score = gesture_score.sum().values[0]
        all_score = gesture_score['score'].tolist()
        accumulated_score = []
        for i in range(0, len(all_score)):
            if i == 0:
                accumulated_score.append(all_score[i])
            else:
                accumulated_score.append(accumulated_score[i-1] + all_score[i])
        error_rate = []
        for i, score in enumerate(accumulated_score):
            full_score = (i+1) * 4
            rate = accumulated_score[i]/ full_score
            error_rate.append(1 - rate)
        return error_rate

def calculate_error_rate_task2(gesture_name):
    gesture_status = retrieve_gesture_status_task2(gesture_name)
    trial = len(gesture_status)
    if gesture_status.empty:
        return None
    else:
        all_status = gesture_status['status'].tolist()
        error_rate = []
        trial_success = 0
        for i, status in enumerate( all_status):
            if status:
                trial_success += 1
            error_rate.append(1- (trial_success/(i+1)))
    return error_rate
            
# database operation
def insert_record_task1(gesture_name, score ):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('INSERT INTO Gesture_Task1 VALUES (?, ?, ?)', (gesture_name, score, date.today().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    #print to test
    retrieve_tableData_info("Gesture_Task1")
    
def insert_record_task2(gesture_name, status, duration):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('INSERT INTO Gesture_Task2 VALUES (?, ?, ?, ?)', (gesture_name, status, duration, date.today().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    #print to test
    retrieve_tableData_info("Gesture_Task2")
    
# sample data
def populate_test_data():
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    
   

    gesture_task1_data = [
        ('ZhiJiXiangYin', 4, '2022-05-01'),
        ('ZhiJiXiangYin', 3, '2022-05-02'),
        ('ZhiJiXiangYin', 2, '2022-05-03'),
    ]
    c.execute('DELETE FROM Gesture_Task1')
    c.executemany('INSERT INTO Gesture_Task1 VALUES (?, ?, ?)', gesture_task1_data)

    gesture_task2_data = [
        ('ZhiJiXiangYin', True, 120, '2022-05-01'),
        ('ZhiJiXiangYin', False, 150, '2022-05-02'),
        ('ZhiJiXiangYin', True, 130, '2022-05-03'),
    ]
    c.execute('DELETE FROM Gesture_Task2')
    c.executemany('INSERT INTO Gesture_Task2 VALUES (?, ?, ?, ?)', gesture_task2_data)

    conn.commit()
    conn.close()
    


def test_retrieve_gesture_score_task1():
    scores = retrieve_gesture_score_task1('ZhiJiXiangYin')
    print("Scores retrieved from Gesture_Task1:", scores)
    assert scores.shape[0] == 3
    assert scores['score'].tolist() == [4, 3, 2]

def test_retrieve_gesture_status_task2():
    statuses = retrieve_gesture_status_task2('ZhiJiXiangYin')
    print("Statuses retrieved from Gesture_Task2:", statuses)
    assert statuses.shape[0] == 3
    assert statuses['status'].tolist() == [True, False, True]

def test_retrieve_gesture_duration_task2():
    durations = retrieve_gesture_duration_task2('ZhiJiXiangYin')
    print("Durations retrieved from Gesture_Task2:", durations)
    assert durations.shape[0] == 3
    assert durations['duration'].tolist() == [120, 150, 130]

def test_calculate_error_rate_task1():
    # Expected accumulated error rates for 'ZhiJiXiangYin'
    # Given scores: [4, 3, 2]
    # Accumulated scores: [4, 7, 9]
    # Error rates: [0/4, 7/8, 9/12] = [0, 0.875, 0.75]
    expected_error_rates = [0, 1/8, 3/12]
    
    # Calculate the error rates using the function
    calculated_error_rates = calculate_error_rate_task1('ZhiJiXiangYin')
    
    # Check if the calculated error rates match the expected values
    assert calculated_error_rates == expected_error_rates, f"Expected {expected_error_rates}, but got {calculated_error_rates}"


def test_calculate_error_rate_task2():
    error_rates = calculate_error_rate_task2('ZhiJiXiangYin')
    print("Error rates for Gesture_Task2:", error_rates)
    expected_rates = [0, 1/2, 1/3]  # Assuming the test data: [(True), (False), (True)]
    assert len(error_rates) == len(expected_rates)
    for rate, expected in zip(error_rates, expected_rates):
        assert abs(rate - expected) < 1e-6  # Allowing small floating-point error

def clear_db():
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    
    c.execute('DELETE FROM Gesture_Task1')
    c.execute('DELETE FROM Gesture_Task2')
    
    conn.commit()
    conn.close()

def test_database():
    create_db()
    populate_test_data()
    
    test_retrieve_gesture_score_task1()
    test_retrieve_gesture_status_task2()
    test_retrieve_gesture_duration_task2()
    test_calculate_error_rate_task1()
    test_calculate_error_rate_task2()
    
    clear_db()
    print("All tests passed!")

if __name__ == "__main__":
    test_database()
    # clear_db()
    # create_db()
    # retrieve_table_info()
    