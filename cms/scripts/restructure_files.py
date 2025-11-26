#!/usr/bin/env python3
"""
Major restructuring script for JABchem files
- Flattens folder structure (moves all PDFs to level folders)
- Removes spaces from filenames
- Updates markdown files with new paths
- Updates database with new paths
- Creates backup before making changes
"""

import os
import sys
import shutil
import re
import sqlite3
import yaml
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
from config import Config

BACKUP_DIR = 'backup_before_restructure'
SUBJECTS = ['chemistry', 'maths', 'physics', 'biology']
LEVELS = ['additional', 'advancedhigher', 'archive', 'higher', 'national5']

def create_backup():
    """Create a complete backup of files and database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join('..', BACKUP_DIR, timestamp)
    
    print(f"Creating backup at {backup_path}...")
    os.makedirs(backup_path, exist_ok=True)
    
    # Backup database
    db_path = Config.DATABASE_PATH
    if os.path.exists(db_path):
        shutil.copy2(db_path, os.path.join(backup_path, 'jabchem.db'))
        print(f"  ✓ Database backed up")
    
    # Backup all subject folders
    for subject in SUBJECTS:
        subject_path = os.path.join('..', subject)
        if os.path.exists(subject_path):
            backup_subject = os.path.join(backup_path, subject)
            shutil.copytree(subject_path, backup_subject)
            print(f"  ✓ {subject} folder backed up")
    
    # Backup _downloads folder
    downloads_path = os.path.join('..', '_downloads')
    if os.path.exists(downloads_path):
        shutil.copytree(downloads_path, os.path.join(backup_path, '_downloads'))
        print(f"  ✓ _downloads folder backed up")
    
    print(f"\n✓ Backup complete: {backup_path}")
    return backup_path

def sanitize_filename(filename):
    """Remove spaces from filename"""
    # Remove all spaces
    filename = filename.replace(' ', '')
    return filename

def find_all_pdfs(subject, level):
    """Find all PDF files in a subject/level directory tree"""
    base_path = os.path.join('..', '..', subject, level)
    pdfs = []
    
    if not os.path.exists(base_path):
        return pdfs
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.join('..', '..'))
                pdfs.append({
                    'old_path': full_path,
                    'old_rel_path': '/' + rel_path,
                    'filename': file
                })
    
    return pdfs

def move_and_rename_pdfs():
    """Move all PDFs to level folders and rename them"""
    moves = []
    
    for subject in SUBJECTS:
        for level in LEVELS:
            print(f"\nProcessing {subject}/{level}...")
            
            # Find all PDFs
            pdfs = find_all_pdfs(subject, level)
            
            if not pdfs:
                print(f"  No PDFs found")
                continue
            
            print(f"  Found {len(pdfs)} PDFs")
            
            # Target directory
            target_dir = os.path.join('..', '..', subject, level)
            os.makedirs(target_dir, exist_ok=True)
            
            for pdf in pdfs:
                old_path = pdf['old_path']
                old_filename = pdf['filename']
                
                # Sanitize filename
                new_filename = sanitize_filename(old_filename)
                new_path = os.path.join(target_dir, new_filename)
                
                # Handle duplicates
                counter = 1
                while os.path.exists(new_path) and new_path != old_path:
                    base, ext = os.path.splitext(new_filename)
                    new_filename = f"{base}_{counter}{ext}"
                    new_path = os.path.join(target_dir, new_filename)
                    counter += 1
                
                # Only move if different
                if old_path != new_path:
                    new_rel_path = '/' + os.path.relpath(new_path, '..')
                    
                    moves.append({
                        'old_path': old_path,
                        'new_path': new_path,
                        'old_rel_path': pdf['old_rel_path'],
                        'new_rel_path': new_rel_path,
                        'subject': subject,
                        'level': level
                    })
    
    return moves

def update_markdown_files(moves):
    """Update all markdown files with new paths"""
    # Create path mapping
    path_map = {move['old_rel_path']: move['new_rel_path'] for move in moves}
    
    print("\nUpdating markdown files...")
    updated_count = 0
    
    downloads_dir = os.path.join('..', '..', '_downloads')
    for root, dirs, files in os.walk(downloads_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace all old paths with new paths
                for old_path, new_path in path_map.items():
                    if old_path in content:
                        content = content.replace(old_path, new_path)
                
                # Write back if changed
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    print(f"  ✓ Updated {os.path.relpath(filepath, os.path.join('..', '..'))}")
            
            except Exception as e:
                print(f"  ✗ Error updating {filepath}: {e}")
    
    print(f"\n✓ Updated {updated_count} markdown files")

def update_database(moves):
    """Update database with new file paths"""
    # Create path mapping
    path_map = {move['old_rel_path']: move['new_rel_path'] for move in moves}
    
    print("\nUpdating database...")
    
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Update papers table
    cursor.execute('SELECT id, past_paper_path, jabchem_marking_path, sqa_marking_path FROM papers')
    papers = cursor.fetchall()
    
    updated_count = 0
    for paper_id, past_paper, jabchem, sqa in papers:
        new_past = path_map.get(past_paper, past_paper) if past_paper else None
        new_jabchem = path_map.get(jabchem, jabchem) if jabchem else None
        new_sqa = path_map.get(sqa, sqa) if sqa else None
        
        if new_past != past_paper or new_jabchem != jabchem or new_sqa != sqa:
            cursor.execute('''
                UPDATE papers 
                SET past_paper_path = ?, jabchem_marking_path = ?, sqa_marking_path = ?
                WHERE id = ?
            ''', (new_past, new_jabchem, new_sqa, paper_id))
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Updated {updated_count} database records")

def execute_moves(moves):
    """Actually move the files"""
    print(f"\nMoving {len(moves)} files...")
    
    for move in moves:
        try:
            # Create parent directory if needed
            os.makedirs(os.path.dirname(move['new_path']), exist_ok=True)
            
            # Move file
            shutil.move(move['old_path'], move['new_path'])
            print(f"  ✓ {move['old_rel_path']} -> {move['new_rel_path']}")
        
        except Exception as e:
            print(f"  ✗ Error moving {move['old_path']}: {e}")
    
    print(f"\n✓ Moved {len(moves)} files")

def cleanup_empty_dirs():
    """Remove empty directories after moving files"""
    print("\nCleaning up empty directories...")
    
    removed = 0
    for subject in SUBJECTS:
        subject_path = os.path.join('..', subject)
        if not os.path.exists(subject_path):
            continue
        
        # Walk bottom-up to remove empty dirs
        for root, dirs, files in os.walk(subject_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Empty directory
                        os.rmdir(dir_path)
                        removed += 1
                        print(f"  ✓ Removed empty: {os.path.relpath(dir_path, '..')}")
                except:
                    pass
    
    print(f"\n✓ Removed {removed} empty directories")

def main():
    print("="*70)
    print("JABchem File Restructuring Script")
    print("="*70)
    print("\nThis will:")
    print("  1. Create a backup")
    print("  2. Flatten folder structure (move all PDFs to level folders)")
    print("  3. Remove spaces from filenames")
    print("  4. Update markdown files")
    print("  5. Update database")
    print("  6. Clean up empty directories")
    print("\n" + "="*70)
    
    response = input("\nProceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Step 1: Create backup
    backup_path = create_backup()
    
    # Step 2: Find all files and plan moves
    print("\n" + "="*70)
    print("Planning file moves...")
    print("="*70)
    moves = move_and_rename_pdfs()
    
    if not moves:
        print("\nNo files to move!")
        return
    
    print(f"\nPlanned {len(moves)} file moves")
    
    # Show sample
    print("\nSample moves:")
    for move in moves[:5]:
        print(f"  {move['old_rel_path']}")
        print(f"    -> {move['new_rel_path']}")
    
    if len(moves) > 5:
        print(f"  ... and {len(moves) - 5} more")
    
    response = input("\nExecute moves? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Step 3: Execute moves
    print("\n" + "="*70)
    print("Executing file moves...")
    print("="*70)
    execute_moves(moves)
    
    # Step 4: Update markdown files
    print("\n" + "="*70)
    print("Updating markdown files...")
    print("="*70)
    update_markdown_files(moves)
    
    # Step 5: Update database
    print("\n" + "="*70)
    print("Updating database...")
    print("="*70)
    update_database(moves)
    
    # Step 6: Cleanup
    print("\n" + "="*70)
    print("Cleaning up...")
    print("="*70)
    cleanup_empty_dirs()
    
    print("\n" + "="*70)
    print("✓ RESTRUCTURING COMPLETE!")
    print("="*70)
    print(f"\nBackup location: {backup_path}")
    print("\nTo restore from backup if needed:")
    print(f"  python scripts/restore_backup.py {os.path.basename(backup_path)}")

if __name__ == '__main__':
    main()
