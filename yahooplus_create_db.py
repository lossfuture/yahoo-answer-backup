import sqlite3
from sqlite3 import Error
import os.path
import time

'''
Edit on 9/4/2021

'''
def create_database():
    ''' Create new database for saver, it can works indivially'''
    while True:
        db_name=input("Input new database file name >> ")
        if os.path.isfile(db_name):
            print ("Error: File already exist, please enter another name")
        else:
            break

    conn = None
    today=time.strftime("%Y-%m-%d")
    try:
        conn = sqlite3.connect(db_name)
        #print(sqlite3.version)
        print(sqlite3.sqlite_version)
        print("Creating database...")
        c = conn.cursor()
        c.execute('''CREATE TABLE question (
    newqid      TEXT     PRIMARY KEY,
    oldqid      INTEGER,
    category_id INTEGER,
    title       TEXT,
    content     TEXT,
    answercount INTEGER,
    datecreated DATETIME,
    author_link TEXT,
    author_type TEXT,
    author_name TEXT
);


''')

        c.execute('''CREATE TABLE category (
    catid        INTEGER PRIMARY KEY,
    level        INTEGER,
    cat_parentid INTEGER REFERENCES category (catid),
    catname      TEXT
);
''')

        c.execute('''CREATE TABLE answers (
    aid         INTEGER  PRIMARY KEY,
    question_id INTEGER,
    is_accepted BOOLEAN,
    answer      TEXT,
    author_type TEXT,
    author_name TEXT,
    author_link TEXT,
    datecreated DATETIME,
    upvotecount INTEGER
);
''')


        c.executescript('''
CREATE TABLE yahoo_dbsettings (
    name  TEXT PRIMARY KEY,
    value TEXT
);

INSERT INTO yahoo_dbsettings (name, value) VALUES ('version', '1.0');
INSERT INTO yahoo_dbsettings (name, value) VALUES ('timestamp', '');
INSERT INTO yahoo_dbsettings (name, value) VALUES ('pagecount', '24');

''')
        c.execute('''INSERT INTO yahoo_dbsettings (name, value) VALUES ('date', ?);''',(today,))

        conn.commit()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
        input("Database {} create successful!\nPress any key to exit.".format(db_name))

if __name__ == '__main__':
    create_database()
