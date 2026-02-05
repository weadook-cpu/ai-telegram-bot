# database.py
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        logger.info("✅ Veritabanı başlatıldı")
    
    def create_tables(self):
        """Создаём таблицы если их нет"""
        cursor = self.conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                tokens INTEGER DEFAULT 15000,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrals INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                invited_by INTEGER
            )
        ''')
        
        # Таблица операций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                tokens_change INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица изображений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                model TEXT,
                prompt TEXT,
                image_url TEXT,
                tokens_spent INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
        logger.info("✅ Tablolar oluşturuldu")
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    def add_user(self, user_id: int, username: str, first_name: str, 
                 last_name: str, invited_by: Optional[int] = None) -> bool:
        """Добавить нового пользователя"""
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли уже пользователь
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return False
            
            # Добавляем пользователя
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, invited_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, invited_by))
            
            # Если есть пригласивший, начисляем ему бонус
            if invited_by:
                self.add_tokens(invited_by, 2000, "referral_bonus", 
                              f"Arkadaş daveti: {user_id}")
                cursor.execute(
                    "UPDATE users SET referrals = referrals + 1 WHERE user_id = ?",
                    (invited_by,)
                )
            
            self.conn.commit()
            logger.info(f"✅ Yeni kullanıcı eklendi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Kullanıcı eklenemedi: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Получить данные пользователя"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_tokens(self, user_id: int) -> int:
        """Получить баланс токенов пользователя"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT tokens FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row['tokens'] if row else 0
    
    # ========== ТОКЕНЫ ==========
    def add_tokens(self, user_id: int, amount: int, action: str, 
                   details: str = "") -> bool:
        """Добавить токены пользователю"""
        try:
            cursor = self.conn.cursor()
            
            # Обновляем баланс
            cursor.execute(
                "UPDATE users SET tokens = tokens + ? WHERE user_id = ?",
                (amount, user_id)
            )
            
            # Записываем транзакцию
            cursor.execute('''
                INSERT INTO transactions (user_id, action, tokens_change, details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, amount, details))
            
            # Обновляем общую сумму потраченного
            if amount < 0:  # Если списание
                cursor.execute(
                    "UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?",
                    (abs(amount), user_id)
                )
            
            self.conn.commit()
            logger.info(f"✅ Token eklendi: {user_id} -> {amount}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Token eklenemedi: {e}")
            return False
    
    def check_and_deduct_tokens(self, user_id: int, amount: int, 
                                action: str, details: str = "") -> bool:
        """Проверить и списать токены если достаточно"""
        current_tokens = self.get_user_tokens(user_id)
        
        if current_tokens < amount:
            return False
        
        return self.add_tokens(user_id, -amount, action, details)
    
    # ========== ИСТОРИЯ ==========
    def get_user_history(self, user_id: int, limit: int = 10) -> List[dict]:
        """Получить историю операций пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT action, tokens_change, details, timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_image_record(self, user_id: int, model: str, prompt: str, 
                         image_url: str, tokens_spent: int) -> bool:
        """Добавить запись о сгенерированном изображении"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO images (user_id, model, prompt, image_url, tokens_spent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, model, prompt, image_url, tokens_spent))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Görsel kaydedilemedi: {e}")
            return False
    
    # ========== СТАТИСТИКА ==========
    def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя"""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        cursor = self.conn.cursor()
        
        # Количество сгенерированных изображений
        cursor.execute(
            "SELECT COUNT(*) as image_count FROM images WHERE user_id = ?",
            (user_id,)
        )
        image_count = cursor.fetchone()['image_count']
        
        # Общее количество токенов потрачено
        cursor.execute('''
            SELECT COALESCE(SUM(ABS(tokens_change)), 0) as total_spent
            FROM transactions 
            WHERE user_id = ? AND tokens_change < 0
        ''', (user_id,))
        total_spent = cursor.fetchone()['total_spent']
        
        return {
            **user,
            'image_count': image_count,
            'total_spent': total_spent
        }
    
    def close(self):
        """Закрыть соединение с базой"""
        self.conn.close()
