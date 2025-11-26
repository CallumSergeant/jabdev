#!/usr/bin/env python3
"""
Restore from backup created by restructure_files.py
"""

import os
import sys
import shutil

BACKUP_DIR = 'backup_before_restructure'

def list_backups():
    """List available backups"""
    backup_path = os.path.join('..', BACKUP_DIR)
    
    if not os.path.exists(backup_path):
        print("No backups found")
        return []
    
    backups = [d for d in os.listdir(backup_path) if os.path.isdir(os.path.join(backup_path, d))]
    backups.sort(reverse=True)
    
    return backups

def restore_backup(backup_name):
    """Restore from a specific backup"""
    backup_path = os.path.join('..', BACKUP_DIR, backup_name)
    
    if not os.path.exists(backup_path):
        print(f"Backup not found: {backup_path}")
        return False
    
    print(f"Restoring from: {backup_path}")
    
    # Restore database
    db_backup = os.path.join(backup_path, 'jabchem.db')
    if os.path.exists(db_backup):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
        from config import Config
        shutil.copy2(db_backup, Config.DATABASE_PATH)
        print("  ✓ Database restored")
    
    # Restore subject folders
    for item in os.listdir(backup_path):
        item_path = os.path.join(backup_path, item)
        if os.path.isdir(item_path) and item != '_downloads':
            target_path = os.path.join('..', item)
            
            # Remove current
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # Restore from backup
            shutil.copytree(item_path, target_path)
            print(f"  ✓ {item} folder restored")
    
    # Restore _downloads
    downloads_backup = os.path.join(backup_path, '_downloads')
    if os.path.exists(downloads_backup):
        downloads_target = os.path.join('..', '_downloads')
        if os.path.exists(downloads_target):
            shutil.rmtree(downloads_target)
        shutil.copytree(downloads_backup, downloads_target)
        print("  ✓ _downloads folder restored")
    
    print("\n✓ Restore complete!")
    return True

def main():
    print("="*70)
    print("JABchem Backup Restore")
    print("="*70)
    
    backups = list_backups()
    
    if not backups:
        print("\nNo backups available")
        return
    
    print("\nAvailable backups:")
    for i, backup in enumerate(backups, 1):
        print(f"  {i}. {backup}")
    
    if len(sys.argv) > 1:
        backup_name = sys.argv[1]
    else:
        choice = input("\nSelect backup number (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
        
        try:
            idx = int(choice) - 1
            backup_name = backups[idx]
        except (ValueError, IndexError):
            print("Invalid selection")
            return
    
    print(f"\nRestoring from: {backup_name}")
    response = input("This will overwrite current files. Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        restore_backup(backup_name)
    else:
        print("Aborted")

if __name__ == '__main__':
    main()
