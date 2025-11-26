#!/usr/bin/env python3
"""
Fix database paths to match flattened file structure
This script updates all file paths in the database to remove subdirectories
and spaces from filenames.
"""

import os
import sys
import sqlite3
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
from config import Config

def sanitize_path(path):
    """Convert old path to new flattened path without spaces"""
    if not path:
        return None
    
    # Remove ../ references
    path = path.replace('/../', '/')
    
    # Split path into parts
    parts = path.split('/')
    
    # Get subject and level (should be parts 1 and 2)
    if len(parts) < 4:
        # Already in correct format
        filename = parts[-1].replace(' ', '')
        parts[-1] = filename
        return '/'.join(parts)
    
    # Extract subject, level, and filename
    subject = parts[1] if len(parts) > 1 else ''
    level = parts[2] if len(parts) > 2 else ''
    filename = parts[-1]
    
    # Remove spaces from filename
    filename = filename.replace(' ', '')
    
    # Build new path: /subject/level/filename
    new_path = f'/{subject}/{level}/{filename}'
    
    return new_path

def main():
    print("="*70)
    print("Fix Database Paths Script")
    print("="*70)
    print("\nThis will update all file paths in the database to:")
    print("  - Remove subdirectories (flatten structure)")
    print("  - Remove spaces from filenames")
    print("\n" + "="*70)
    
    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    print(f"\nDatabase: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all papers
    cursor.execute('SELECT id, past_paper_path, jabchem_marking_path, sqa_marking_path FROM papers')
    papers = cursor.fetchall()
    
    print(f"\nFound {len(papers)} papers in database")
    
    # Show samples of what will change
    print("\nSample changes:")
    sample_count = 0
    for paper_id, past_paper, jabchem, sqa in papers[:10]:
        if past_paper:
            new_past = sanitize_path(past_paper)
            if new_past != past_paper:
                print(f"\n  Paper {paper_id}:")
                print(f"    OLD: {past_paper}")
                print(f"    NEW: {new_past}")
                sample_count += 1
                if sample_count >= 5:
                    break
    
    response = input("\nProceed with updates? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Update all papers
    updated_count = 0
    for paper_id, past_paper, jabchem, sqa in papers:
        new_past = sanitize_path(past_paper)
        new_jabchem = sanitize_path(jabchem)
        new_sqa = sanitize_path(sqa)
        
        if new_past != past_paper or new_jabchem != jabchem or new_sqa != sqa:
            cursor.execute('''
                UPDATE papers 
                SET past_paper_path = ?, jabchem_marking_path = ?, sqa_marking_path = ?
                WHERE id = ?
            ''', (new_past, new_jabchem, new_sqa, paper_id))
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Updated {updated_count} papers in database")
    print("\nNext steps:")
    print("  1. Regenerate markdown files: POST to /api/publish/test")
    print("  2. Rebuild Jekyll site")
    print("  3. Check preview")

if __name__ == '__main__':
    main()
