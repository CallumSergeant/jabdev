#!/usr/bin/env python3
"""
Add remaining missing items (Chemistry Additional, Physics N5, Maths Higher)
"""

import os
import sys
import sqlite3
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def get_category_id(cursor, subject, level, category_slug):
    """Get category ID"""
    cursor.execute('''
        SELECT c.id FROM categories c
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE s.name = ? AND l.name = ? AND c.slug = ?
    ''', (subject, level, category_slug))
    result = cursor.fetchone()
    return result[0] if result else None

def add_paper(cursor, year, category_id, additional_data=None):
    """Add a paper to database"""
    cursor.execute('''
        INSERT INTO papers (year, category_id, additional_files)
        VALUES (?, ?, ?)
    ''', (year, category_id, json.dumps(additional_data) if additional_data else None))
    return cursor.lastrowid

def main():
    print("="*70)
    print("ADD REMAINING MISSING ITEMS")
    print("="*70)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    added_count = 0
    
    # 1. Chemistry Additional - Multiple Choice Data (7 items)
    print("\n1. Adding Chemistry Additional - Multiple Choice Data...")
    cat_id = get_category_id(cursor, 'Chemistry', 'Additional', 'multiplechoicedata')
    if cat_id:
        mc_data = [
            (1, 'Advanced Higher', '2016-2017', 'SQAnewAdvancedHigherMCdata.pdf'),
            (2, 'Revised Advanced Higher', '2013-2015', 'SQArevisedAdvancedHigherMCdata.pdf'),
            (5, 'Revised Higher', '2012-2015', 'SQArevisedHigherMCdata.pdf'),
            (6, 'Old Higher', '2000-2015', 'SQAoldHigherMCdata.pdf'),
            (7, 'Pre-2000 Higher', '1991-1999', 'SQApre2000HigherMCdata.pdf'),
            (8, 'National 5', '2014-2017', 'SQANat5MCdata.pdf'),
            (10, 'Intermediate 1', '2002-2015', 'SQAInt1MCdata.pdf'),
        ]
        
        for num, age, years, filename in mc_data:
            data = {
                '#': num,
                'Age': age,
                'Years Covered': years,
                'File': [{'url': f'/chemistry/additional/{filename}', 'link_text': 'MC Data'}]
            }
            add_paper(cursor, str(num), cat_id, data)
            added_count += 1
        print(f"  ✓ Added {len(mc_data)} MC data items")
    
    # 2. Chemistry Additional - Comparison (1 item)
    print("\n2. Adding Chemistry Additional - Comparison...")
    cat_id = get_category_id(cursor, 'Chemistry', 'Additional', 'comparisonofquestions')
    if cat_id:
        data = {
            '#': 2,
            'Comparison Table': [{'url': '/chemistry/additional/RevAHtoAHcomparison.pdf', 'link_text': 'AH v revAH Question Comparison'}]
        }
        add_paper(cursor, '2', cat_id, data)
        added_count += 1
        print("  ✓ Added comparison item")
    
    # 3. Physics N5 - Self Evaluation (2 items)
    print("\n3. Adding Physics N5 Self Evaluation...")
    cat_id = get_category_id(cursor, 'Physics', 'National 5', 'n5selfevaluation')
    if cat_id:
        # Item 1
        data = {
            '#': 1,
            'File': 'Traffic Lights',
            'Link': [{'url': '/physics/national5/Nat5PhysicsTrafficLights.pdf', 'link_text': 'Traffic Lights'}]
        }
        add_paper(cursor, 'TL', cat_id, data)
        added_count += 1
        print("  ✓ Added TL")
        
        # Item 2
        data = {
            '#': 2,
            'File': 'Question Bank',
            'Link': [{'url': '/physics/national5/Nat5PhysicsQuestionBank.pdf', 'link_text': 'Question Bank'}]
        }
        add_paper(cursor, 'QB', cat_id, data)
        added_count += 1
        print("  ✓ Added QB")
    
    # 4. Maths Higher - Missing paper
    # Need to find which year is missing
    print("\n4. Checking Maths Higher for missing paper...")
    cursor.execute('''
        SELECT p.year FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        WHERE s.name = 'Maths' AND l.name = 'Higher' AND c.slug = 'sqapastpapersoldhigher'
        ORDER BY p.year
    ''')
    existing_years = [row[0] for row in cursor.fetchall()]
    print(f"  Existing years: {existing_years}")
    print("  (Need to check live site to identify missing year)")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print(f"✓ Added {added_count} items to database")
    print("="*70)
    print("\nNext steps:")
    print("  1. Regenerate markdown: curl -X POST http://localhost:3001/api/publish/test")
    print("  2. Rebuild Jekyll")
    print("  3. Run comparison again to verify")

if __name__ == '__main__':
    main()
