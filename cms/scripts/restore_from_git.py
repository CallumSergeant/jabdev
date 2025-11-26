#!/usr/bin/env python3
"""
Restore missing data from git history
"""

import os
import sys
import sqlite3
import yaml
import json
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def get_file_from_git(filepath, commit='8d8a9b1'):
    """Get file content from git"""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit}:{filepath}'],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..', '..')
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        return None

def parse_frontmatter(content):
    """Parse YAML frontmatter"""
    if not content or not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    try:
        return yaml.safe_load(parts[1])
    except:
        return None

def fix_path(path):
    """Fix file paths"""
    if not path:
        return None
    # Remove spaces and fix structure
    path = path.replace(' ', '')
    # Flatten paths
    parts = path.split('/')
    if len(parts) > 3:
        # Keep only subject/level/filename
        return f'/{parts[1]}/{parts[2]}/{parts[-1]}'
    return path

def restore_chemistry_data(db_path):
    """Restore all missing Chemistry data from git"""
    print("\n" + "="*70)
    print("Restoring Chemistry Data from Git")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all Chemistry papers that need additional_files
    cursor.execute('''
        SELECT p.id, p.year, c.slug, s.slug, l.slug
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE s.name = 'Chemistry'
        AND c.slug IN ('ahcoursenotesandexercises', 'ahselfevaluation',
                       'higherselfevaluation', 'higherexercises',
                       'nat5selfevaluation', 'nat5exercises',
                       'int1coursematerials', 'additionalmaterials')
    ''')
    
    papers = cursor.fetchall()
    print(f"Found {len(papers)} papers to restore")
    
    fixed = 0
    for paper_id, year, category_slug, subject_slug, level_slug in papers:
        # Try different possible filenames
        possible_names = [
            f"{year}.md",
            f"{year.lower().replace(' ', '')}.md",
            f"{year.replace(' ', '').replace('.', '')}.md"
        ]
        
        git_path = f"_downloads/{subject_slug}/{level_slug}"
        
        for filename in possible_names:
            full_path = f"{git_path}/{filename}"
            content = get_file_from_git(full_path)
            
            if content:
                frontmatter = parse_frontmatter(content)
                if frontmatter and frontmatter.get('category') == category_slug:
                    # Build additional_files
                    additional_data = {}
                    
                    for key, value in frontmatter.items():
                        if key in ['title', 'level', 'category', 'subject', 'Year', 'year']:
                            continue
                        
                        # Fix paths
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
                    
                    if additional_data:
                        cursor.execute('UPDATE papers SET additional_files = ? WHERE id = ?',
                                     (json.dumps(additional_data), paper_id))
                        fixed += 1
                        print(f"  ✓ Restored {year} ({category_slug})")
                    break
    
    conn.commit()
    conn.close()
    print(f"\n✓ Restored {fixed} papers")
    return fixed

def main():
    print("="*70)
    print("Restore Data from Git History")
    print("="*70)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '..', 'server', 'db', 'jabchem.db')
    
    response = input("\nRestore missing data from git? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return 0
    
    fixed = restore_chemistry_data(db_path)
    
    print("\n" + "="*70)
    print(f"✓ Restored {fixed} papers")
    print("="*70)
    print("\nNext steps:")
    print("  1. Regenerate markdown: curl -X POST http://localhost:3001/api/publish/test")
    print("  2. Rebuild Jekyll")
    print("  3. Check preview")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
