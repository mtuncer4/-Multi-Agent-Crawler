import sqlite3
import threading
import os

DB_FILE = 'crawler_state.db'
# A global lock in Python to prevent "database is locked" errors during simultaneous writes.
# SQLite handles concurrent reads okay, but writes should be serialized in basic setups.
write_lock = threading.Lock()

def get_connection():
    # check_same_thread=False is needed so we can share connections across threads if necessary,
    # though it's safer for each thread to open its own connection.
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute('pragma journal_mode=wal') # Write-Ahead Logging allows simultaneous readers and writers
    return conn

def init_db():
    with write_lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Table for queue and states
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                origin_url TEXT,
                depth INTEGER NOT NULL,
                max_depth INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        ''')
        
        # Table for document index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                text_content TEXT,
                FOREIGN KEY (url_id) REFERENCES urls(id)
            )
        ''')
        
        # Recovery: on init, anything that was 'processing' might have failed abruptly. Reset them to 'pending'.
        cursor.execute("UPDATE urls SET status = 'pending' WHERE status = 'processing'")
        
        conn.commit()
        conn.close()

def add_to_queue(url, origin_url, depth, max_depth):
    with write_lock:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO urls (url, origin_url, depth, max_depth, status) VALUES (?, ?, ?, ?, 'pending')", 
                (url, origin_url, depth, max_depth)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # URL already exists (never crawl same page twice requirement)
            return False
        finally:
            conn.close()

def get_next_pending():
    # Readers don't necessarily need the strict write lock, but status update is write
    with write_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, depth, origin_url, max_depth FROM urls WHERE status = 'pending' LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            cursor.execute("UPDATE urls SET status = 'processing' WHERE id = ?", (row[0],))
            conn.commit()
        
        conn.close()
        return row

def mark_crawled(url_id, text_content):
    with write_lock:
        conn = get_connection()
        try:
            # Update status
            conn.execute("UPDATE urls SET status = 'crawled' WHERE id = ?", (url_id,))
            # Insert content
            if text_content:
                conn.execute("INSERT INTO content_index (url_id, text_content) VALUES (?, ?)", (url_id, text_content))
            conn.commit()
        finally:
            conn.close()

def mark_failed(url_id):
    with write_lock:
        conn = get_connection()
        conn.execute("UPDATE urls SET status = 'failed' WHERE id = ?", (url_id,))
        conn.commit()
        conn.close()

def get_queue_depth():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_crawled_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status = 'crawled'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_failed_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status = 'failed'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_active_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status = 'processing'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_max_seen_depth():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(depth) FROM urls")
    res = cursor.fetchone()[0]
    conn.close()
    return res if res is not None else 0

def force_resume_all():
    with write_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE urls SET status = 'pending' WHERE status IN ('processing', 'failed')")
        conn.commit()
        conn.close()
