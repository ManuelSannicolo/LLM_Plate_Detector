"""
Database Manager for authorized plates
Uses SQLite for simplicity and portability
"""
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """Manages all database operations for plates"""
    
    def __init__(self, db_path: str = "authorized_plates.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if not exist"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Authorized plates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authorized_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL,
                expiration_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Access log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                frame_number INTEGER,
                confidence REAL,
                status TEXT NOT NULL,
                track_id INTEGER
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plate_number 
            ON authorized_plates(plate_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_access_timestamp 
            ON access_log(timestamp)
        """)
        
        self.connection.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    def add_authorized_plate(self, plate_number: str, first_name: str, 
                            last_name: str, role: str, 
                            expiration_date: str = None) -> bool:
        """Add new authorized plate"""
        try:
            plate_number = plate_number.upper().strip()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO authorized_plates 
                (plate_number, first_name, last_name, role, expiration_date)
                VALUES (?, ?, ?, ?, ?)
            """, (plate_number, first_name, last_name, role, expiration_date))
            
            self.connection.commit()
            print(f"✅ Plate added: {plate_number}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️ Plate {plate_number} already exists")
            return False
        except Exception as e:
            print(f"❌ Error adding plate: {e}")
            return False
    
    def is_plate_authorized(self, plate_number: str) -> Tuple[bool, Optional[Dict]]:
        """Check if plate is authorized and not expired"""
        try:
            plate_number = plate_number.upper().strip()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM authorized_plates 
                WHERE plate_number = ?
            """, (plate_number,))
            
            row = cursor.fetchone()
            
            if not row:
                return False, None
            
            plate_info = dict(row)
            
            # Check expiration
            expiration_date_str = plate_info.get('expiration_date')
            
            if expiration_date_str and expiration_date_str.strip() != "":
                expiration_date = datetime.strptime(
                    expiration_date_str, '%Y-%m-%d'
                ).date()
                today = date.today()
                
                if expiration_date < today:
                    plate_info['status'] = 'expired'
                    return False, plate_info
            
            plate_info['status'] = 'valid'
            return True, plate_info
            
        except Exception as e:
            print(f"❌ Error checking plate: {e}")
            return False, None
    
    def get_all_valid_plates(self) -> List[str]:
        """Get all valid (non-expired) plates"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT plate_number FROM authorized_plates
                WHERE expiration_date IS NULL 
                   OR expiration_date >= date('now')
                ORDER BY plate_number
            """)
            
            plates = [row['plate_number'] for row in cursor.fetchall()]
            return plates
            
        except Exception as e:
            print(f"❌ Error getting plates: {e}")
            return []
    
    def log_access(self, plate_number: str, frame_number: int, 
                   confidence: float, status: str, track_id: int = None):
        """Log vehicle access attempt"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO access_log 
                (plate_number, frame_number, confidence, status, track_id)
                VALUES (?, ?, ?, ?, ?)
            """, (plate_number, frame_number, confidence, status, track_id))
            
            self.connection.commit()
            
        except Exception as e:
            print(f"❌ Error logging access: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database closed")

# Test
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Add test plates
    db.add_authorized_plate("NA13NRU", "Mario", "Rossi", "Docente", "2026-12-31")
    db.add_authorized_plate("GX150GJ", "Giulia", "Bianchi", "Studente", "2026-06-30")
    
    # Check authorization
    is_auth, info = db.is_plate_authorized("NA13NRU")
    print(f"NA13NRU authorized: {is_auth}")
    
    db.close()
