#!/usr/bin/env python3
"""
Fix Biology Higher to include both Biology and Human Biology papers
"""

import os
import sys
import sqlite3
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def get_file_from_git(filepath, commit='b7233e9'):
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
    except:
        return None

def parse_frontmatter(content):
    """Parse YAML frontmatter"""
    if not content or not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    try:
        import yaml
        return yaml.safe_load(parts[1])
    except:
        return None

def fix_path(path):
    """Fix file paths"""
    if not path:
        return None
    path = path.replace(' ', '')
    parts = path.split('/')
    if len(parts) > 3:
        return f'/{parts[1]}/{parts[2]}/{parts[-1]}'
    return path

def main():
    print("="*70)
    print("FIX BIOLOGY HIGHER - ADD HUMAN BIOLOGY PAPERS")
    print("="*70)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all Biology Higher papers
    cursor.execute('''
        SELECT p.id, p.year, p.past_paper_path, p.sqa_marking_path, c.slug
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE s.name = 'Biology' AND l.name = 'Higher'
        ORDER BY c.slug, p.year
    ''')
    
    papers = cursor.fetchall()
    print(f"\nFound {len(papers)} Biology Higher papers")
    
    updated = 0
    
    for paper_id, year, bio_pp, bio_sqa, category in papers:
        if not bio_pp:
            continue
        
        # Try to find human biology version
        # Pattern: revHbiologySQApp2014.pdf -> revHhumanbioSQApp2014.pdf
        # or: oldHbiologySQApp2014.pdf -> oldHhumanbioSQApp2014.pdf
        
        human_pp = None
        human_sqa = None
        
        if bio_pp:
            # Try different patterns
            human_pp = bio_pp.replace('biology', 'humanbio').replace('Biology', 'HumanBiology')
            if not os.path.exists(human_pp.lstrip('/')):
                human_pp = bio_pp.replace('Hbiology', 'Hhumanbio').replace('HBiology', 'HHumanBiology')
            if not os.path.exists(human_pp.lstrip('/')):
                human_pp = None
        
        if bio_sqa:
            human_sqa = bio_sqa.replace('biology', 'humanbio').replace('Biology', 'HumanBiology')
            if not os.path.exists(human_sqa.lstrip('/')):
                human_sqa = bio_sqa.replace('Hbiology', 'Hhumanbio').replace('HBiology', 'HHumanBiology')
            if not os.path.exists(human_sqa.lstrip('/')):
                human_sqa = None
        
        if human_pp or human_sqa:
            # Create additional_files structure with both versions
            additional_data = {
                'Year': year,
                'Past Paper': []
            }
            
            if bio_pp:
                additional_data['Past Paper'].append({
                    'url': bio_pp,
                    'link_text': 'Biology Paper'
                })
            
            if human_pp:
                additional_data['Past Paper'].append({
                    'url': human_pp,
                    'link_text': 'Human Biology Paper'
                })
            
            if bio_sqa or human_sqa:
                additional_data['SQA Marking Scheme'] = []
                
                if bio_sqa:
                    additional_data['SQA Marking Scheme'].append({
                        'url': bio_sqa,
                        'link_text': 'SQA Biology Solutions'
                    })
                
                if human_sqa:
                    additional_data['SQA Marking Scheme'].append({
                        'url': human_sqa,
                        'link_text': 'SQA Human Biology Solutions'
                    })
            
            # Update paper to use additional_files and clear standard paths
            cursor.execute('''
                UPDATE papers 
                SET additional_files = ?,
                    past_paper_path = NULL,
                    sqa_marking_path = NULL
                WHERE id = ?
            ''', (json.dumps(additional_data), paper_id))
            
            updated += 1
            print(f"✓ Updated {year} ({category}) - Added Human Biology version")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"✓ Updated {updated} Biology Higher papers")
    print("="*70)
    print("\nNext steps:")
    print("  1. Regenerate markdown")
    print("  2. Rebuild Jekyll")
    print("  3. Check preview")

if __name__ == '__main__':
    main()
