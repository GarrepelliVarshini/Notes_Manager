import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    conn = pymysql.connect(**db_config)
    return conn

def db_init():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS USERS
        (
        USERID INT PRIMARY KEY AUTO_INCREMENT,
        USERNAME VARCHAR(20) NOT NULL,
        USERMAIL VARCHAR(40) NOT NULL UNIQUE,
        USERPASSWORD VARCHAR(15) NOT NULL 
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS USEROTP
        (
        USERNAME VARCHAR(20) NOT NULL,
        USERMAIL VARCHAR(40) NOT NULL UNIQUE,
        USERPASSWORD VARCHAR(15) NOT NULL,
        OTP INT NOT NULL
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS NOTES
        (
        USERID INT NOT NULL,
        NOTESID INT PRIMARY KEY AUTO_INCREMENT,
        TITLE VARCHAR(100) NOT NULL,
        CONTENT VARCHAR(250) NOT NULL
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS FILES
        (
        FID INT PRIMARY KEY AUTO_INCREMENT,
        USERID INT NOT NULL,
        FILENAME VARCHAR(30) NOT NULL,
        FILEPATH VARCHAR(50) NOT NULL
        )
        '''
    )
    cursor.close()
    conn.close()

def registered_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM USERS
        WHERE USERMAIL = %s
        ''', (email,)
    )

    user = cursor.fetchone() # tuple
    return user

def insert_userotp(uname, umail, upassword, uotp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO USEROTP
        VALUES
        (%s, %s, %s, %s)
        ''', (uname, umail, upassword, uotp)
    )
    conn.commit()
    cursor.close()
    conn.close()

def check_userotp(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM USEROTP
        WHERE USERMAIL = %s
        ''', (email,)
    )

    user = cursor.fetchone() # tuple
    return user

def insert_users(uname, umail, upassword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO USERS
        (USERNAME, USERMAIL, USERPASSWORD)
        VALUES
        (%s, %s, %s)
        ''', (uname, umail, upassword)
    )
    conn.commit()
    cursor.close()
    conn.close()

def check_userpassword(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM USERS
        WHERE USERMAIL = %s AND USERPASSWORD = %s
        ''', (email, password)
    )
    user_exist = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_exist

def add_notes(userid, title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO NOTES
        (USERID, TITLE, CONTENT)
        VALUES
        (%s, %s, %s)
        ''', (userid, title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

def display_notes(userid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE USERID = %s
        ''', (userid,)
    )
    user_notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return user_notes

def get_note(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE NOTESID = %s
        ''', (nid,)
    )
    note = cursor.fetchone()
    cursor.close()
    conn.close()
    return note

def update_note_db(nid, n_content, n_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE NOTES SET 
        TITLE = %s, CONTENT = %s
        WHERE NOTESID = %s
        ''', (n_title, n_content, nid)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_note_db(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM NOTES 
        WHERE NOTESID = %s
        ''', (nid,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def add_file_db(fname, fpath, userid):
    conn =get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO FILES
        (FILENAME, FILEPATH, USERID)
        VALUES
        (%s, %s, %s)
        ''',(fname, fpath, userid)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_files_db(userid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM FILES
        WHERE USERID = %s
        ''',(userid,)
    )
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    return files

def get_file_db(fid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM FILES
        WHERE FID = %s
        ''',(fid,)
    )
    file = cursor.fetchone()
    cursor.close()
    conn.close()
    return file

def delete_file_db(fid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM FILES
        WHERE FID = %s
        ''', (fid,)
        )
    conn.commit()
    cursor.close()
    conn.close()

def search_notes(userid, query):
    conn = get_connection()
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE USERID = %s AND (TITLE LIKE %s OR CONTENT LIKE %s)
        ''', (userid, search_pattern, search_pattern)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def password_reset_db(email, new):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE USERS
        SET USERPASSWORD = %s
        WHERE USERMAIL = %s
        ''', (new, email)
    )
    conn.commit()
    cursor.close()
    conn.close()
