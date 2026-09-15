import sqlite3, hashlib

class DatabaseManager:
    def __init__(self, db_name='workshop.db'):
        self.dbname = db_name
        self.creer_tables()
        self.creer_admin_default()
    
    def get_connexion(self):
        conn = sqlite3.connect(self.dbname, timeout=10)
        return conn
    
    def creer_tables(self):
        conn = self.get_connexion()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'client'
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def creer_admin_default(self):
        conn = self.get_connexion()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE role="admin"')
            admin_exists = cursor.fetchone()
            if not admin_exists:
                default_admin_password = '123'
                pwd_hash = hashlib.sha256(default_admin_password.encode('utf-8')).hexdigest()
                cursor.execute(
                    'INSERT INTO users (name, password, role) VALUES (?,?,?)',
                    ('admin', pwd_hash, 'admin')
                )
                conn.commit()
        finally:
            conn.close()
    
    def add_user(self, name, password, role='client'):
        pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        conn = self.get_connexion()
        try:
            conn.execute(
                'INSERT INTO users (name, password, role) VALUES (?,?,?)',
                (name, pwd_hash, role)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_user(self, user_id):
        conn = self.get_connexion()
        try:
            conn.execute('DELETE FROM users WHERE id=?', (user_id,))
            conn.commit()
        finally:
            conn.close()
            
    def edit_user(self, user_id, name=None, password=None, role=None):
        conn = self.get_connexion()
        try:
            if name:
                conn.execute('UPDATE users SET name=? WHERE id=?', (name, user_id))
            if password:
                pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                conn.execute('UPDATE users SET password=? WHERE id=?', (pwd_hash, user_id))
            if role:
                conn.execute('UPDATE users SET role=? WHERE id=?', (role, user_id))
            conn.commit()
        finally:
            conn.close()

    def login(self, name, password):
        pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        conn = self.get_connexion()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE name=? AND password=?',
                (name, pwd_hash)
            ).fetchone()
        finally:
            conn.close()
        return user

    def get_users_list(self):
        conn = self.get_connexion()
        try:
            users = conn.execute('SELECT * FROM users').fetchall()
        finally:
            conn.close()
        return users

    def get_user_by_id(self, user_id):
            conn = self.get_connexion()
            try:
                user = conn.execute(
                    'SELECT * FROM users WHERE id=?',
                    (user_id,)
                ).fetchone()
            finally:
                conn.close()
            return user
