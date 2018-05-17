import sqlite3
import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

dbPath = 'data.db'

conn = sqlite3.connect(dbPath)

ingTable = ('CREATE TABLE IF NOT EXISTS ingredients( '
             '   id integer primary key autoincrement not null, '
             '   name varchar(255) unique not null, '
             '   jar_pos integer unique ,'
             '   mixer integer default 0'
             ');')

conn.execute(ingTable)

drinkTable = ('CREATE TABLE IF NOT EXISTS drinks( '
             '  id integer primary key autoincrement not null, '
             '  name varchar(255) unique not null, '
             '  image varchar(255), '
             '  notes TEXT'
             ');')

conn.execute(drinkTable)

drinkIngTable = ('CREATE TABLE IF NOT EXISTS drink_ingredient( '
             '  drink_id integer not null, '
             '  ingredient_id integer not null, '
             '  oz real not null,'
             '  FOREIGN KEY(drink_id) REFERENCES drinks(id) ON DELETE CASCADE, '
             '  FOREIGN KEY(ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE '
             ');')

conn.execute(drinkIngTable)

conn.commit()
conn.close()
