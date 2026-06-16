import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nickname TEXT UNIQUE,
            phone TEXT,
            password_hash TEXT,
            is_registered BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            computer_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_date TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (computer_id) REFERENCES computers(id)
        )
    """)
    # Добавляем колонки, если их нет (для миграции)
    for col in ["start_date", "start_time", "end_date", "end_time"]:
        try:
            cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM computers")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 16):
            cursor.execute("INSERT INTO computers (number) VALUES (?)", (i,))
        conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# --- Users ---
def register_user(user_id: int, nickname: str, name: str, phone: str, password_hash: str,
                  telegram_username: str = None, telegram_full_name: str = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE nickname = ?", (nickname,))
    if cursor.fetchone():
        conn.close()
        return False
    try:
        cursor.execute("""
            INSERT INTO users (user_id, username, full_name, nickname, phone, password_hash, is_registered)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                nickname = excluded.nickname,
                phone = excluded.phone,
                password_hash = excluded.password_hash,
                is_registered = 1
        """, (user_id, telegram_username, telegram_full_name, nickname, phone, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(user_id: int, nickname: str, password_hash: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE nickname = ?", (nickname,))
    row = cursor.fetchone()
    if row and row[0] == password_hash:
        cursor.execute("""
            UPDATE users
            SET user_id = ?, is_registered = 1
            WHERE nickname = ?
        """, (user_id, nickname))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def is_authorized(user_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_registered FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 1

def get_all_users() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, nickname, full_name, username, phone, registered_at
        FROM users
        WHERE is_registered = 1
        ORDER BY registered_at ASC
    """)
    users = cursor.fetchall()
    conn.close()
    return users

# --- Computers ---
def get_computers() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, number FROM computers WHERE is_active = 1 ORDER BY number")
    computers = cursor.fetchall()
    conn.close()
    return computers

# --- Bookings ---
def is_computer_free(computer_id: int, start_date: str, start_time: str, end_date: str, end_time: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM bookings
        WHERE computer_id = ?
        AND NOT (end_date < ? OR end_date = ? AND end_time <= ? OR
                 start_date > ? OR start_date = ? AND start_time >= ?)
    """, (computer_id, start_date, start_date, start_time, end_date, end_date, end_time))
    result = cursor.fetchone()
    conn.close()
    return result is None

def add_booking(user_id: int, computer_id: int, start_date: str, start_time: str, end_date: str, end_time: str) -> bool:
    if not is_computer_free(computer_id, start_date, start_time, end_date, end_time):
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (user_id, computer_id, start_date, start_time, end_date, end_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, computer_id, start_date, start_time, end_date, end_time))
    conn.commit()
    conn.close()
    return True

def get_user_bookings(user_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, c.number, b.start_date, b.start_time, b.end_date, b.end_time
        FROM bookings b
        JOIN computers c ON b.computer_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.start_date, b.start_time
    """, (user_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def cancel_booking(booking_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_all_bookings() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, u.full_name, u.username, c.number, b.start_date, b.start_time, b.end_date, b.end_time
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN computers c ON b.computer_id = c.id
        ORDER BY b.start_date, b.start_time
    """)
    bookings = cursor.fetchall()
    conn.close()
    return bookings