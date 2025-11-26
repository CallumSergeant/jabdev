#!/usr/bin/env python3
"""
Fix missing data by re-migrating from backup markdown files
Specifically handles:
- Missing SQA marking schemes
- Missing self-evaluation materials
- Missing course notes and exercises
- Missing additional materials
"""

import os
import sys
import sqlite3
import yaml
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def parse_markdown_frontmatter(filepath):
    """Extract frontmatter from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter
    except Exception as e:
        return None

def fix_path(path):
    """Fix relative paths"""
    if not path:
        return None
    return path.replace('/../', '/')

def update_sqa_marking_schemes(db_path, backup_dir):
    """Update missing SQA marking schemes from backup"""
    print("\n" + "="*70)
    print("Fixing SQA Marking Schemes")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find papers with past papers but no SQA marking
    cursor.execute('''
        SELECT p.id, p.year, p.past_paper_path, s.slug, l.slug
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE p.past_paper_path IS NOT NULL 
        AND p.sqa_marking_path IS NULL
        AND s.name = 'Chemistry'
    ''')
    
    papers = cursor.fetchall()
    print(f"Found {len(papers)} papers missing SQA marking schemes")
    
    fixed = 0
    for paper_id, year, pp_path, subject_slug, level_slug in papers:
        # Try to find the marking scheme file
        if pp_path:
            # Replace PP with Msch in the path
            marking_path = pp_path.replace('SQApp', 'SQAmsch').replace('SQAPP', 'SQAmsch')
            
            # Check if file exists
            file_path = marking_path.lstrip('/')
            if os.path.exists(file_path):
                cursor.execute('UPDATE papers SET sqa_marking_path = ? WHERE id = ?', 
                             (marking_path, paper_id))
                fixed += 1
                print(f"  ✓ Fixed {year}: {marking_path}")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Fixed {fixed} SQA marking schemes")
    return fixed

def update_additional_materials(db_path, backup_dir):
    """Update missing additional materials from backup"""
    print("\n" + "="*70)
    print("Fixing Additional Materials")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find papers with NULL additional_files
    cursor.execute('''
        SELECT p.id, p.year, c.slug, s.slug, l.slug
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE p.additional_files IS NULL
        AND c.slug IN ('ahselfevaluation', 'higherselfevaluation', 'nat5selfevaluation',
                       'ahcoursenotesandexercises', 'higherexercises', 'nat5exercises',
                       'int1coursematerials', 'additionalmaterials')
        AND s.name = 'Chemistry'
    ''')
    
    papers = cursor.fetchall()
    print(f"Found {len(papers)} papers missing additional materials data")
    
    fixed = 0
    for paper_id, year, category_slug, subject_slug, level_slug in papers:
        # Try to find backup file
        backup_path = os.path.join(backup_dir, '_downloads', subject_slug, level_slug)
        
        if not os.path.exists(backup_path):
            continue
        
        # Look for matching file
        for filename in os.listdir(backup_path):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(backup_path, filename)
            frontmatter = parse_markdown_frontmatter(filepath)
            
            if not frontmatter:
                continue
            
            # Check if this matches our paper
            fm_category = frontmatter.get('category', '')
            fm_year = str(frontmatter.get('Year') or frontmatter.get('year') or frontmatter.get('title', ''))
            
            if fm_category == category_slug and fm_year == year:
                # Build additional_files JSON
                additional_data = {}
                
                for key, value in frontmatter.items():
                    if key in ['title', 'level', 'category', 'subject']:
                        continue
                    
                    # Fix paths in the data
                    if isinstance(value, list):
                        fixed_list = []
                        for item in value:
                            if isinstance(item, dict) and 'url' in item:
                                item['url'] = fix_path(item['url'])
                            fixed_list.append(item)
                        additional_data[key] = fixed_list
                    elif isinstance(value, dict) and 'url' in value:
                        value['url'] = fix_path(value['url'])
                        additional_data[key] = value
                    else:
                        additional_data[key] = value
                
                # Update database
                cursor.execute('UPDATE papers SET additional_files = ? WHERE id = ?',
                             (json.dumps(additional_data), paper_id))
                fixed += 1
                print(f"  ✓ Fixed {year} ({category_slug})")
                break
    
    conn.commit()
    conn.close()
    print(f"\n✓ Fixed {fixed} additional materials")
    return fixed

def main():
    print("="*70)
    print("Fix Missing Data Script")
    print("="*70)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '..', 'server', 'db', 'jabchem.db')
    backup_dir = os.path.join(script_dir, '..', '..', 'backup_old_md', '20251126_212710')
    
    if not os.path.exists(backup_dir):
        print(f"Error: Backup not found at {backup_dir}")
        return 1
    
    print(f"\nDatabase: {db_path}")
    print(f"Backup: {backup_dir}")
    
    response = input("\nProceed with fixes? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return 0
    
    # Fix SQA marking schemes
    fixed_sqa = update_sqa_marking_schemes(db_path, backup_dir)
    
    # Fix additional materials
    fixed_additional = update_additional_materials(db_path, backup_dir)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"SQA marking schemes fixed:    {fixed_sqa}")
    print(f"Additional materials fixed:   {fixed_additional}")
    print(f"Total fixes:                  {fixed_sqa + fixed_additional}")
    print()
    print("Next steps:")
    print("  1. Regenerate markdown: curl -X POST http://localhost:3001/api/publish/test")
    print("  2. Rebuild Jekyll site")
    print("  3. Check preview")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
