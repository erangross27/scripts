import sqlite3
import json


class ConversationManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                history TEXT
            )
        ''')
        self.conn.commit()

    def save_conversation(self, conversation_id, title, history):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO conversations (id, title, history)
            VALUES (?, ?, ?)
        ''', (conversation_id, title, json.dumps(history)))
        self.conn.commit()

    def load_conversations(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM conversations ORDER BY rowid DESC')
        return cursor.fetchall()

    def load_conversation_history(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT history FROM conversations WHERE id = ?', (conversation_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

    def delete_conversation(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        self.conn.commit()

    def rename_conversation(self, conversation_id, new_title):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE conversations SET title = ? WHERE id = ?', (new_title, conversation_id))
        self.conn.commit()