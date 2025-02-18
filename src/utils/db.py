import aiosqlite
import json
from datetime import datetime

async def init_db():
    async with aiosqlite.connect('data/conversations.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conv_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conv_id) REFERENCES conversations(id)
            )
        ''')
        await db.commit()

async def save_conversation(conv_id, messages=[]):
    """
    Saves a new conversation with the given conversation ID and initial messages.
    """
    async with aiosqlite.connect('data/conversations.db') as db:
        await db.execute('''
            INSERT INTO conversations (id)
            VALUES (?)
        ''', (conv_id,))
        
        for message in messages:
            await db.execute('''
                INSERT INTO messages (conv_id, role, content)
                VALUES (?, ?, ?)
            ''', (conv_id, message["role"], message["content"]))
        
        await db.commit()


async def save_message(conv_id, role, content):
    async with aiosqlite.connect('data/conversations.db') as db:
        await db.execute('''
            INSERT INTO messages (conv_id, role, content)
            VALUES (?, ?, ?)
        ''', (conv_id, role, content))
        await db.commit()

async def get_messages(conv_id):
    async with aiosqlite.connect('data/conversations.db') as db:
        cursor = await db.execute('''
            SELECT role, content FROM messages WHERE conv_id = ?
        ''', (conv_id,))
        
        rows = await cursor.fetchall()
        print("DEBUG: Rows fetched from DB:", rows)  # ✅ Add this to check data

        return [dict(zip(["role", "content"], row)) for row in rows]  # ✅ Fix dict conversion

