import sqlite3
from pathlib import Path
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "squad.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                assignee TEXT NOT NULL,
                status TEXT DEFAULT 'todo',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                content TEXT,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                skills TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                priority TEXT DEFAULT 'medium'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, assignee: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, assignee) VALUES (?, ?)", (title, assignee))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def update_task_status(self, task_id: int, status: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
        conn.close()
    
    def get_all_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, assignee, status FROM tasks ORDER BY id DESC")
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def index_document(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO documents (path, content) VALUES (?, ?)",
                (path, content)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def search_documents(self, query: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT path, content FROM documents WHERE content LIKE ?",
            (f"%{query}%",)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_team_members(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, skills FROM team_members")
        members = cursor.fetchall()
        conn.close()
        return members
    
    def add_team_member(self, name: str, skills: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO team_members (name, skills) VALUES (?, ?)", (name, skills))
        conn.commit()
        conn.close()
    
    def get_skill_gaps(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, skill_name, priority FROM skill_gaps ORDER BY priority DESC")
        gaps = cursor.fetchall()
        conn.close()
        return gaps
    
    def add_skill_gap(self, skill: str, priority: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO skill_gaps (skill_name, priority) VALUES (?, ?)", (skill, priority))
        conn.commit()
        conn.close()
