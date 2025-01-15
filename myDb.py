import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def createUser(username, password, admin):
    # Хеширование пароля
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Подключение к нашей базе данных
    conn = get_db_connection()
    c = conn.cursor()

    # Добавление нового пользователя
    c.execute('INSERT INTO users (username, password, admin) VALUES (?, ?, ?)', (username, hashed_password, admin))

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()

def createTables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT UNIQUE,
             password TEXT,
             admin BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tests (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT,
             availability BOOLEAN) ''')
    conn.commit()
    conn.close()
get_db_connection()
createTables()
#createUser('миша', 'миша2007_', 0)
#createUser('Елена', 'Pupka1981', 1)


