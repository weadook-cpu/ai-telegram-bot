# database.py - ДЕМО РЕЖИМ
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
        logger.info("✅ Veritabanı başlatıldı (Demo Modu)")
    
    def create_tables(self):
        """Создаём таблицы если их нет"""
        cursor = self.conn.cursor()
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                tokens_change INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                model TEXT,
                prompt TEXT,
                image_url TEXT,
                tokens_spent INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    def add_user(self, user_id: int, username: str, first_name: str, 
                 last_name: str, invited_by: Optional[int] = None) -> bool:
        """Добавить нового пользователя (всегда 15.000 токенов)"""
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли уже пользователь
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                logger.info(f"✅ Kullanıcı zaten var: {user_id}")
                return True  # Уже есть
            
            # Добавляем пользователя с 15.000 токенами
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, tokens, invited_by)
                VALUES (?, ?, ?, ?, 15000, ?)
            ''', (user_id, username, first_name, last_name, invited_by))
            
            self.conn.commit()
            logger.info(f"✅ Yeni kullanıcı: {user_id} - 15.000 token verildi")
            return True
            
        except Exception as e:
            logger.error(f"❌ Kullanıcı eklenemedi: {e}")
            return False
    
    def get_user_tokens(self, user_id: int) -> int:
        """Получить баланс токенов (в демо всегда минимум 15.000)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT tokens FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                tokens = row['tokens']
                # В демо-режиме если меньше 15.000, показываем 15.000
                if tokens < 15000:
                    logger.info(f"⚠️ Düşük bakiye: {user_id} -> {tokens}, 15000 gösteriliyor")
                    return 15000
                return tokens
            else:
                # Если пользователя нет, создаём с 15.000
                logger.info(f"⚠️ Kullanıcı yok, demo bakiye: 15000")
                return 15000
                
        except Exception as e:
            logger.error(f"❌ Token okunamadı: {e}")
            return 15000  # Всегда 15.000 в демо
    
    # ========== ТОКЕНЫ ==========
    def add_tokens(self, user_id: int, amount: int, action: str, 
                   details: str = "") -> bool:
        """Добавить/списать токены (в демо только логируем)"""
        try:
            logger.info(f"📝 Token işlemi: {user_id} -> {amount} ({action})")
            
            # В демо-режиме реально не списываем, только логируем
            if amount < 0:
                logger.info(f"🪙 Demo harcama: {-amount} token - {details}")
            
            # Но записываем в историю для отображения
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, action, tokens_change, details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, amount, details))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Token işlemi hatası: {e}")
            return True  # В демо всегда успешно
    
    # ========== ИСТОРИЯ ==========
    def get_user_history(self, user_id: int, limit: int = 5) -> List[dict]:
        """Получить историю операций пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT action, tokens_change, details, timestamp
                FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
    
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
    
    def close(self):
        """Закрыть соединение с базой"""
        self.conn.close()
