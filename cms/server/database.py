import sqlite3
import os
from contextlib import contextmanager

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create tables and seed initial data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    icon TEXT,
                    color TEXT,
                    description TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    subject_id INTEGER NOT NULL,
                    description TEXT,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id),
                    UNIQUE(subject_id, slug)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    level_id INTEGER NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    table_config TEXT,
                    FOREIGN KEY (level_id) REFERENCES levels(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    past_paper_path TEXT,
                    jabchem_marking_path TEXT,
                    sqa_marking_path TEXT,
                    additional_files TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publish_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_hash TEXT,
                    message TEXT,
                    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
            ''')
            
            # Seed subjects
            subjects = [
                ('Chemistry', 'chemistry', 'flask', 'c3e8ff', None),
                ('Maths', 'maths', 'calculator', 'edc672', None),
                ('Physics', 'physics', 'atom', 'd7b5e8', None),
                ('Biology', 'biology', 'dna', 'C2D8B2', None)
            ]
            
            for subject in subjects:
                cursor.execute('''
                    INSERT OR IGNORE INTO subjects (name, slug, icon, color, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', subject)
            
            # Seed levels for each subject
            cursor.execute('SELECT id FROM subjects')
            subject_ids = [row[0] for row in cursor.fetchall()]
            
            levels = [
                ('National 5', 'national5', None),
                ('Higher', 'higher', None),
                ('Advanced Higher', 'advancedhigher', None),
                ('Archive', 'archive', None)
            ]
            
            for subject_id in subject_ids:
                for level in levels:
                    cursor.execute('''
                        INSERT OR IGNORE INTO levels (name, slug, subject_id, description)
                        VALUES (?, ?, ?, ?)
                    ''', (level[0], level[1], subject_id, level[2]))
            
            conn.commit()
            print("Database initialized successfully")
