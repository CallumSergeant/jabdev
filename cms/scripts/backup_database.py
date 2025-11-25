#!/usr/bin/env python3
"""
Database backup script
"""

import os
import sys
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from config import Config

def backup_database():
    """Create a backup of the database"""
    db_path = Config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return False
    
    # Create backup directory
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"jabchem_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copy database
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up successfully to: {backup_path}")
        
        # Get file size
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        print(f"Backup size: {size_mb:.2f} MB")
        
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False

if __name__ == '__main__':
    print("JABchem CMS - Database Backup")
    print("="*50)
    backup_database()
