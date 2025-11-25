#!/usr/bin/env python3
"""
Migration script to import existing markdown files into the database
"""

import os
import sys
import yaml
import re
from pathlib import Path

# Add parent directory to path to import from server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from database import Database
from config import Config

def parse_frontmatter(filepath):
    """Parse YAML frontmatter from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter - handle both complete and incomplete closing ---
    # Match from --- to either another --- or end of file
    match = re.match(r'^---\s*\n(.*?)(?:\n---\s*(?:\n|$)|\Z)', content, re.DOTALL)
    if not match:
        return None
    
    try:
        # PyYAML handles # comments automatically, so just load it
        yaml_content = match.group(1)
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {filepath}: {e}")
        return None

def extract_file_path(file_data):
    """Extract file path from frontmatter data"""
    if not file_data:
        return None
    
    if isinstance(file_data, list) and len(file_data) > 0:
        return file_data[0].get('url')
    elif isinstance(file_data, dict):
        return file_data.get('url')
    
    return None

def normalize_year(year_value):
    """Normalize year value to string"""
    if year_value is None:
        return None
    return str(year_value).strip()

def migrate_papers(db, downloads_dir='../_downloads'):
    """Migrate papers from markdown files to database"""
    
    if not os.path.exists(downloads_dir):
        print(f"Downloads directory not found: {downloads_dir}")
        return
    
    stats = {
        'processed': 0,
        'imported': 0,
        'skipped': 0,
        'errors': 0
    }
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get subject and level mappings
        cursor.execute('SELECT id, slug FROM subjects')
        subjects = {row['slug']: row['id'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT id, slug, subject_id FROM levels')
        levels = {(row['subject_id'], row['slug']): row['id'] for row in cursor.fetchall()}
        
        # Walk through downloads directory
        for root, dirs, files in os.walk(downloads_dir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                filepath = os.path.join(root, filename)
                stats['processed'] += 1
                
                # Parse frontmatter
                frontmatter = parse_frontmatter(filepath)
                if not frontmatter:
                    print(f"Skipping {filepath}: No frontmatter")
                    stats['skipped'] += 1
                    continue
                
                # Extract year - try multiple fields
                # For additional materials, use title or filename as year
                year = frontmatter.get('Year') or frontmatter.get('year') or frontmatter.get('title')
                
                # If still no year and it's in 'additional' folder, use filename
                if not year and 'additional' in filepath:
                    year = os.path.splitext(os.path.basename(filepath))[0]
                
                if not year:
                    print(f"Skipping {filepath}: No year field")
                    stats['skipped'] += 1
                    continue
                
                year = normalize_year(year)
                
                # Extract subject and level from path
                path_parts = Path(filepath).parts
                try:
                    downloads_idx = path_parts.index('_downloads')
                    subject_slug = path_parts[downloads_idx + 1]
                    level_slug = path_parts[downloads_idx + 2]
                except (ValueError, IndexError):
                    print(f"Skipping {filepath}: Cannot determine subject/level from path")
                    stats['skipped'] += 1
                    continue
                
                # Get subject and level IDs
                subject_id = subjects.get(subject_slug)
                if not subject_id:
                    print(f"Skipping {filepath}: Unknown subject '{subject_slug}'")
                    stats['skipped'] += 1
                    continue
                
                level_id = levels.get((subject_id, level_slug))
                if not level_id:
                    print(f"Skipping {filepath}: Unknown level '{level_slug}' for subject '{subject_slug}'")
                    stats['skipped'] += 1
                    continue
                
                # Get or create category
                category_slug = frontmatter.get('category', 'default')
                category_name = frontmatter.get('category', 'Default Category')
                
                cursor.execute('''
                    SELECT id FROM categories 
                    WHERE level_id = ? AND slug = ?
                ''', (level_id, category_slug))
                
                category_row = cursor.fetchone()
                if category_row:
                    category_id = category_row['id']
                else:
                    # Create category
                    cursor.execute('''
                        INSERT INTO categories (name, slug, level_id)
                        VALUES (?, ?, ?)
                    ''', (category_name, category_slug, level_id))
                    category_id = cursor.lastrowid
                    print(f"Created category: {category_name} ({category_slug})")
                
                # Extract file paths - try multiple field names
                past_paper_path = extract_file_path(frontmatter.get('Past Paper'))
                jabchem_marking_path = extract_file_path(frontmatter.get('JABchem Marking Scheme'))
                sqa_marking_path = (extract_file_path(frontmatter.get('SQA Marking Scheme')) or 
                                   extract_file_path(frontmatter.get('SQA Marking Solutions')))
                
                # For additional materials, store all custom fields as JSON
                additional_files = None
                if level_slug == 'additional':
                    # Store all non-standard fields
                    additional_data = {}
                    standard_fields = {'title', 'level', 'category', 'subject', 'Year', 'year', 
                                     'Past Paper', 'JABchem Marking Scheme', 'SQA Marking Scheme', 
                                     'SQA Marking Solutions'}
                    for key, value in frontmatter.items():
                        if key not in standard_fields:
                            additional_data[key] = value
                    
                    if additional_data:
                        import json
                        additional_files = json.dumps(additional_data)
                
                # Check if paper already exists
                cursor.execute('''
                    SELECT id, past_paper_path, jabchem_marking_path, sqa_marking_path FROM papers 
                    WHERE year = ? AND category_id = ?
                ''', (year, category_id))
                
                existing = cursor.fetchone()
                if existing:
                    # Update if new paths are provided
                    needs_update = False
                    if past_paper_path and not existing['past_paper_path']:
                        needs_update = True
                    if jabchem_marking_path and not existing['jabchem_marking_path']:
                        needs_update = True
                    if sqa_marking_path and not existing['sqa_marking_path']:
                        needs_update = True
                    
                    if needs_update:
                        cursor.execute('''
                            UPDATE papers SET
                                past_paper_path = COALESCE(?, past_paper_path),
                                jabchem_marking_path = COALESCE(?, jabchem_marking_path),
                                sqa_marking_path = COALESCE(?, sqa_marking_path)
                            WHERE id = ?
                        ''', (past_paper_path, jabchem_marking_path, sqa_marking_path, existing['id']))
                        print(f"Updated: {subject_slug}/{level_slug}/{year}")
                        stats['imported'] += 1
                    else:
                        print(f"Skipping {filepath}: Paper already exists (year={year}, category_id={category_id})")
                        stats['skipped'] += 1
                    continue
                
                # Insert paper
                try:
                    cursor.execute('''
                        INSERT INTO papers (
                            year, category_id, past_paper_path,
                            jabchem_marking_path, sqa_marking_path, additional_files
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(year), category_id, past_paper_path,
                        jabchem_marking_path, sqa_marking_path, additional_files
                    ))
                    
                    stats['imported'] += 1
                    print(f"Imported: {subject_slug}/{level_slug}/{year}")
                    
                except Exception as e:
                    print(f"Error importing {filepath}: {e}")
                    stats['errors'] += 1
    
    # Print summary
    print("\n" + "="*50)
    print("Migration Summary")
    print("="*50)
    print(f"Files processed: {stats['processed']}")
    print(f"Papers imported: {stats['imported']}")
    print(f"Files skipped:   {stats['skipped']}")
    print(f"Errors:          {stats['errors']}")
    print("="*50)

if __name__ == '__main__':
    print("JABchem CMS - Data Migration Script")
    print("="*50)
    
    # Initialize database
    db = Database(Config.DATABASE_PATH)
    
    # Run migration
    migrate_papers(db)
    
    print("\nMigration complete!")
