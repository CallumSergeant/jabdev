#!/usr/bin/env python3
"""
Audit script to compare database vs markdown files
Ensures no data loss before cleanup operations
"""

import os
import sys
import sqlite3
import yaml
import json
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def parse_markdown_frontmatter(filepath):
    """Extract frontmatter from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return None
        
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def scan_markdown_files():
    """Scan all markdown files in _downloads"""
    print("Scanning markdown files...")
    
    md_files = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(script_dir, '..', '..', '_downloads')
    
    for root, dirs, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, os.path.join(script_dir, '..', '..'))
                
                frontmatter = parse_markdown_frontmatter(filepath)
                if frontmatter:
                    md_files.append({
                        'path': rel_path,
                        'filename': file,
                        'data': frontmatter
                    })
    
    print(f"  Found {len(md_files)} markdown files")
    return md_files

def get_database_papers():
    """Get all papers from database"""
    print("Loading database papers...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.*,
            c.name as category_name,
            c.slug as category_slug,
            l.name as level_name,
            l.slug as level_slug,
            s.name as subject_name,
            s.slug as subject_slug
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        ORDER BY s.slug, l.slug, p.year
    ''')
    
    papers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print(f"  Found {len(papers)} papers in database")
    return papers

def compare_data():
    """Compare markdown files vs database"""
    print("\n" + "="*70)
    print("DATA AUDIT")
    print("="*70 + "\n")
    
    md_files = scan_markdown_files()
    db_papers = get_database_papers()
    
    # Create lookup structures
    db_lookup = {}
    for paper in db_papers:
        key = (paper['subject_slug'], paper['level_slug'], paper['year'])
        if key not in db_lookup:
            db_lookup[key] = []
        db_lookup[key].append(paper)
    
    md_lookup = {}
    for md in md_files:
        data = md['data']
        subject = data.get('subject', '').lower()
        level = data.get('level', '').lower().replace(' ', '')
        year = str(data.get('Year') or data.get('year') or data.get('title', ''))
        
        key = (subject, level, year)
        if key not in md_lookup:
            md_lookup[key] = []
        md_lookup[key].append(md)
    
    print(f"Database: {len(db_papers)} papers")
    print(f"Markdown: {len(md_files)} files")
    print()
    
    # Find markdown files not in database
    md_only = []
    for key, mds in md_lookup.items():
        if key not in db_lookup:
            md_only.extend(mds)
    
    # Find database entries not in markdown
    db_only = []
    for key, papers in db_lookup.items():
        if key not in md_lookup:
            db_only.extend(papers)
    
    # Check for relative paths (../)
    relative_paths = []
    for md in md_files:
        data = md['data']
        # Check all fields for relative paths
        for field, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'url' in item:
                        if item['url'] and '/../' in item['url']:
                            relative_paths.append({
                                'file': md['path'],
                                'field': field,
                                'url': item['url']
                            })
            elif isinstance(value, dict) and 'url' in value:
                if value['url'] and '/../' in value['url']:
                    relative_paths.append({
                        'file': md['path'],
                        'field': field,
                        'url': value['url']
                    })
    
    # Report findings
    print("="*70)
    print("FINDINGS")
    print("="*70 + "\n")
    
    if md_only:
        print(f"⚠️  {len(md_only)} markdown files NOT in database:")
        print("-"*70)
        for md in md_only[:20]:
            data = md['data']
            print(f"  {md['path']}")
            print(f"    Subject: {data.get('subject')}, Level: {data.get('level')}, Year: {data.get('Year') or data.get('year') or data.get('title')}")
        if len(md_only) > 20:
            print(f"  ... and {len(md_only) - 20} more")
        print()
    else:
        print("✓ All markdown files are in database")
        print()
    
    if db_only:
        print(f"⚠️  {len(db_only)} database entries NOT in markdown:")
        print("-"*70)
        for paper in db_only[:20]:
            print(f"  {paper['subject_name']} {paper['level_name']} {paper['year']}")
        if len(db_only) > 20:
            print(f"  ... and {len(db_only) - 20} more")
        print()
    else:
        print("✓ All database entries have markdown files")
        print()
    
    if relative_paths:
        print(f"⚠️  {len(relative_paths)} files with relative paths (../):")
        print("-"*70)
        for item in relative_paths[:20]:
            print(f"  {item['file']}")
            print(f"    {item['field']}: {item['url']}")
        if len(relative_paths) > 20:
            print(f"  ... and {len(relative_paths) - 20} more")
        print()
    else:
        print("✓ No relative paths found")
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total markdown files:           {len(md_files)}")
    print(f"Total database papers:          {len(db_papers)}")
    print(f"Markdown only (not in DB):      {len(md_only)}")
    print(f"Database only (not in MD):      {len(db_only)}")
    print(f"Files with relative paths:      {len(relative_paths)}")
    print()
    
    if md_only:
        print("⚠️  WARNING: Some markdown files are NOT in the database!")
        print("   Do NOT delete markdown files until these are migrated.")
        print()
        
        # Save list to file
        output_file = os.path.join(os.path.dirname(__file__), 'md_not_in_db.txt')
        with open(output_file, 'w') as f:
            for md in md_only:
                f.write(f"{md['path']}\n")
        print(f"   List saved to: {output_file}")
        print()
    
    if relative_paths:
        print("⚠️  WARNING: Some files have relative paths (../)!")
        print("   These need to be fixed in the database and regenerated.")
        print()
        
        # Save list to file
        output_file = os.path.join(os.path.dirname(__file__), 'relative_paths.txt')
        with open(output_file, 'w') as f:
            for item in relative_paths:
                f.write(f"{item['file']}: {item['url']}\n")
        print(f"   List saved to: {output_file}")
        print()
    
    # Return status
    return {
        'safe_to_delete': len(md_only) == 0,
        'md_only': md_only,
        'db_only': db_only,
        'relative_paths': relative_paths
    }

def main():
    print("="*70)
    print("JABchem Data Audit Script")
    print("="*70)
    print()
    
    result = compare_data()
    
    if result['safe_to_delete']:
        print("="*70)
        print("✓ SAFE TO REGENERATE")
        print("="*70)
        print("All markdown data is in the database.")
        print("It's safe to regenerate markdown files from database.")
        print()
        print("To regenerate:")
        print("  curl -X POST http://localhost:3001/api/publish/test")
        return 0
    else:
        print("="*70)
        print("⚠️  NOT SAFE TO DELETE")
        print("="*70)
        print("Some markdown files contain data not in the database.")
        print("Review the files listed above before proceeding.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
