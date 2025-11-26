#!/usr/bin/env python3
"""
Add all missing items identified by comparison with live site
"""

import os
import sys
import sqlite3
import json
import subprocess

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

def fix_path(path):
    """Fix file paths - remove spaces and flatten"""
    if not path:
        return None
    path = path.replace(' ', '')
    parts = path.split('/')
    if len(parts) > 3:
        return f'/{parts[1]}/{parts[2]}/{parts[-1]}'
    return path

def main():
    print("="*70)
    print("ADD MISSING ITEMS TO DATABASE")
    print("="*70)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    added_count = 0
    
    # 1. Chemistry AH - Course Notes (1.1 and 3.2)
    print("\n1. Adding Chemistry AH Course Notes...")
    cat_id = get_category_id(cursor, 'Chemistry', 'Advanced Higher', 'ahcoursenotesandexercises')
    if cat_id:
        # 1.1
        data = {
            '#': '1.1',
            'Unit': 'Electromagnetic Radiation',
            'Notes': [{'url': fix_path('/chemistry/advancedhigher/AHCourseNotes/1.1AHCfEChemistryNotes.pdf'), 'link_text': 'Unit 1.1 Notes'}],
            'Exercises': [{'url': fix_path('/chemistry/advancedhigher/AHExercises/CfEAHExcercise1.1.pdf'), 'link_text': 'Unit 1.1 Exercise'}]
        }
        add_paper(cursor, '1.1', cat_id, data)
        added_count += 1
        print("  ✓ Added 1.1")
        
        # 3.2
        data = {
            '#': '3.2',
            'Unit': 'Calculations',
            'Notes': [{'url': fix_path('/chemistry/advancedhigher/AHCourseNotes/AHCfEUnit3Skills.pdf'), 'link_text': 'Unit 3.2 Notes'}],
            'Exercises': [
                {'url': fix_path('/chemistry/advancedhigher/AHExercises/CfEAHExercise3.1MC.pdf'), 'link_text': 'Unit 3.2 MC Exercises'},
                {'url': fix_path('/chemistry/advancedhigher/AHExercises/CfEAHExercise3.1Long.pdf'), 'link_text': 'Unit 3.2 Long Exercises'}
            ]
        }
        add_paper(cursor, '3.2', cat_id, data)
        added_count += 1
        print("  ✓ Added 3.2")
    
    # 2. Chemistry Higher - Self Evaluation (1 and 4)
    print("\n2. Adding Chemistry Higher Self Evaluation...")
    cat_id = get_category_id(cursor, 'Chemistry', 'Higher', 'higherselfevaluation')
    if cat_id:
        # Item 1
        data = {
            '#': 1,
            'File': 'Traffic Lights - Unit 1',
            'Link': [{'url': fix_path('/chemistry/higher/HChemSelfEvaluation/JABchemHTrafficLightsUnit1.pdf'), 'link_text': 'Unit 1 Traffic Lights'}]
        }
        add_paper(cursor, 'TL 1', cat_id, data)
        added_count += 1
        print("  ✓ Added TL 1")
        
        # Item 4
        data = {
            '#': 4,
            'File': 'Question Bank',
            'Link': [{'url': fix_path('/chemistry/higher/HChemSelfEvaluation/JABchemHigherQuestionBank.pdf'), 'link_text': 'Question Bank'}]
        }
        add_paper(cursor, 'QB', cat_id, data)
        added_count += 1
        print("  ✓ Added QB")
    
    # 3. Chemistry N5 - Self Evaluation (1 and 2)
    print("\n3. Adding Chemistry N5 Self Evaluation...")
    cat_id = get_category_id(cursor, 'Chemistry', 'National 5', 'n5selfevaluation')
    if cat_id:
        # Item 1
        data = {
            '#': 1,
            'File': 'Traffic Lights',
            'Link': [{'url': fix_path('/chemistry/national5/Nat5SelfEvaluation/Nat5ChemistryTrafficLights.pdf'), 'link_text': 'Traffic Lights'}]
        }
        add_paper(cursor, 'TL', cat_id, data)
        added_count += 1
        print("  ✓ Added TL")
        
        # Item 2
        data = {
            '#': 2,
            'File': 'Question Bank',
            'Link': [{'url': fix_path('/chemistry/national5/Nat5SelfEvaluation/JABchemNat5QuestionBanksAllExams.pdf'), 'link_text': 'Question Bank'}]
        }
        add_paper(cursor, 'QB', cat_id, data)
        added_count += 1
        print("  ✓ Added QB")
    
    # 4. Chemistry N5 - Exercises (19 items)
    print("\n4. Adding Chemistry N5 Exercises (19 items)...")
    cat_id = get_category_id(cursor, 'Chemistry', 'National 5', 'n5exercises')
    if cat_id:
        exercises = [
            ('1.1', 'Reaction Rates', 'Nat5PPSelfStudy1.1.pdf'),
            ('1.21', 'Periodic Table & Atomic Structure', 'Nat5PPSelfStudy1.2a.pdf'),
            ('1.22', 'Covalent & Ionic Bonding', 'Nat5PPSelfStudy1.2bc.pdf'),
            ('1.3', 'Chemical Formulae & Mole Calculations', 'Nat5PPSelfStudy1.3.pdf'),
            ('1.4', 'pH and Acids & Alkalis', 'Nat5PPSelfStudy1.4.pdf'),
            ('2.11', 'Naming & Drawing Hydrocarbons', 'Nat5PPSelfStudy2.1a.pdf'),
            ('2.12', 'Alkanes', 'Nat5PPSelfStudy2.1b.pdf'),
            ('2.13', 'Alkenes', 'Nat5PPSelfStudy2.1c.pdf'),
            ('2.14', 'Cycloalkanes', 'Nat5PPSelfStudy2.1d.pdf'),
            ('2.21', 'Alcohols', 'Nat5PPSelfStudy2.2a.pdf'),
            ('2.22', 'Carboxylic Acids', 'Nat5PPSelfStudy2.2b.pdf'),
            ('2.3', 'Energy From Fuels', 'Nat5PPSelfStudy2.3.pdf'),
            ('3.11', 'Metallic Bonding & Reaction of Metals', 'Nat5PPSelfStudy3.1ab.pdf'),
            ('3.12', 'Redox', 'Nat5PPSelfStudy3.1c.pdf'),
            ('3.13', 'Extraction of Metals', 'Nat5PPSelfStudy3.1d.pdf'),
            ('3.14', 'Electrochemical Cells', 'Nat5PPSelfStudy3.1e.pdf'),
            ('3.2', 'Plastics', 'Nat5PPSelfStudy3.2.pdf'),
            ('3.3', 'Fertilisers', 'Nat5PPSelfStudy3.3.pdf'),
            ('3.4', 'Nuclear Chemistry', 'Nat5PPSelfStudy3.4.pdf'),
        ]
        
        for num, unit, filename in exercises:
            data = {
                '#': num,
                'Unit': unit,
                'Exercises': [{'url': f'/chemistry/national5/{filename}', 'link_text': f'Unit {num} Exercises'}]
            }
            add_paper(cursor, num, cat_id, data)
            added_count += 1
        print(f"  ✓ Added {len(exercises)} exercises")
    
    # 5. Chemistry Archive - Int 1 Course Materials (12 items)
    print("\n5. Adding Chemistry Archive Int 1 Course Materials (12 items)...")
    cat_id = get_category_id(cursor, 'Chemistry', 'Archive', 'coursematerialsint1')
    if cat_id:
        materials = [
            ('1.1', 'Substances', ['Int1.1.pdf'], ['Int1.1summary.pdf'], ['Int1HW1.1.pdf', 'Int1HW1.2.pdf', 'Int1HW1.3.pdf']),
            ('1.2', 'Chemical Reactions', ['Int1.2.pdf'], ['Int1.2summary.pdf'], ['Int1HW2.1.pdf', 'Int1HW2.2.pdf']),
            ('1.3', 'Bonding', ['Int1.3.pdf'], ['Int1.3summary.pdf'], ['Int1HW3.1.pdf', 'Int1HW3.2.pdf']),
            ('1.4', 'Acids & Alkalis', ['Int1.4.pdf'], ['Int1.4summary.pdf'], ['Int1HW4.1.pdf', 'Int1HW4.2.pdf', 'Int1HW4.3.pdf']),
            ('2.5', 'Metals', ['Int1.5.pdf'], ['Int1.5summary.pdf'], ['Int1HW5.1.pdf', 'Int1HW5.2.pdf', 'Int1HW5.3.pdf']),
            ('2.6', 'Personal Needs', ['Int1.6.pdf'], ['Int1.6summary.pdf'], ['Int1HW6.1.pdf', 'Int1HW6.2.pdf']),
            ('2.7', 'Fuels', ['Int1.7.pdf'], ['Int1.7summary.pdf'], ['Int1HW7.1.pdf', 'Int1HW7.2.pdf', 'Int1HW7.3.pdf']),
            ('2.8', 'Plastics', ['Int1.8.pdf'], ['Int1.8summary.pdf'], ['Int1HW8.1.pdf', 'Int1HW8.2.pdf']),
            ('3.9', 'Photosynthesis & Respiration', ['Int1.9.pdf'], ['Int1.9summary.pdf'], ['Int1HW9.1.pdf', 'Int1HW9.2.pdf']),
            ('3.1', 'Plant Growth', ['Int1.10.pdf'], ['Int1.10summary.pdf'], ['Int1HW10.1.pdf', 'Int1HW10.2.pdf']),
            ('3.11', 'Food & Diet', ['Int1.11.pdf'], ['Int1.11summary.pdf'], ['Int1HW11.1.pdf', 'Int1HW11.2.pdf', 'Int1HW11.3.pdf', 'Int1HW11.4.pdf']),
            ('3.12', 'Drugs', ['Int1.12.pdf'], ['Int1.12summary.pdf'], ['Int1HW12.1.pdf', 'Int1HW12.2.pdf']),
        ]
        
        for num, unit, worksheets, summaries, homeworks in materials:
            data = {
                '#': num,
                'Unit': unit,
                'Worksheets': [{'url': f'/chemistry/archive/{w}', 'link_text': 'Worksheet'} for w in worksheets],
                'Summary': [{'url': f'/chemistry/archive/{s}', 'link_text': 'Summary'} for s in summaries],
                'Homework': [{'url': f'/chemistry/archive/{h}', 'link_text': f'{h.split("HW")[1].split(".")[0]} Homework'} for h in homeworks]
            }
            add_paper(cursor, num, cat_id, data)
            added_count += 1
        print(f"  ✓ Added {len(materials)} course materials")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print(f"✓ Added {added_count} items to database")
    print("="*70)
    print("\nNext steps:")
    print("  1. Regenerate markdown: curl -X POST http://localhost:3001/api/publish/test")
    print("  2. Rebuild Jekyll")
    print("  3. Run comparison again")

if __name__ == '__main__':
    main()
