import sqlite3

DB_NAME = "Database/signals.db"

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_token TEXT NOT NULL,
                        instrument TEXT NOT NULL,
                        take_profit REAL NOT NULL,
                        stop_loss REAL NOT NULL,
                        position_type TEXT NOT NULL,
                        amount REAL NOT NULL
                        )''')

def add_signal(unique_token, instrument, take_profit, stop_loss, position_type, amount):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO signals (unique_token, instrument, take_profit, stop_loss, position_type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                  (unique_token, instrument, take_profit, stop_loss, position_type, amount))
        conn.commit()

def remove_signal(signal_id):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM signals WHERE id=?", (signal_id,))
        conn.commit()

def get_signal_by_instrument(instrument):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM signals WHERE instrument=?", (instrument,))
        signal = cur.fetchone()
    return signal

def get_all_signals():
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM signals")
        signals = cur.fetchall()
    return signals

def get_signals():
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM signals")
        rows = cur.fetchall()

    signals = []
    for row in rows:
        signal = {
            'id': row[0],
            'unique_token': row[1],
            'instrument': row[2],
            'take_profit': row[3],
            'stop_loss': row[4],
            'position_type': row[5],
            'amount': row[6],
        }
        signals.append(signal)

    return signals

def get_signal_by_token(unique_token):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM signals WHERE unique_token = ?", (unique_token,))
        result = cur.fetchone()

    return result if result else None
