#!/usr/bin/env python3
"""
Comprehensive content audit script
Compares database content with what's expected to be on the site
"""

import os
import sys
import sqlite3
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

def audit_database():
    """Audit database content"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("="*70)
    print("DATABASE CONTENT AUDIT")
    print("="*70)
    
    # Get counts by subject and level
    cursor.execute('''
        SELECT s.name as subject, l.name as level, c.name as category, COUNT(p.id) as count
        FROM papers p
        JOIN categories c ON p.category_id = c.id
        JOIN levels l ON c.level_id = l.id
        JOIN subjects s ON l.subject_id = s.id
        GROUP BY s.name, l.name, c.name
        ORDER BY s.name, l.name, c.name
    ''')
    
    results = cursor.fetchall()
    
    by_subject = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for row in results:
        subject = row['subject']
        level = row['level']
        category = row['category']
        count = row['count']
        by_subject[subject][level][category] = count
    
    # Print summary
    total_papers = 0
    for subject in sorted(by_subject.keys()):
        print(f"\n{subject}:")
        print("-"*70)
        for level in sorted(by_subject[subject].keys()):
            print(f"  {level}:")
            for category, count in sorted(by_subject[subject][level].items()):
                print(f"    {category}: {count} papers")
                total_papers += count
    
    print("\n" + "="*70)
    print(f"TOTAL PAPERS: {total_papers}")
    print("="*70)
    
    # Check for papers with files
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN past_paper_path IS NOT NULL THEN 1 ELSE 0 END) as with_pp,
            SUM(CASE WHEN jabchem_marking_path IS NOT NULL THEN 1 ELSE 0 END) as with_jab,
            SUM(CASE WHEN sqa_marking_path IS NOT NULL THEN 1 ELSE 0 END) as with_sqa,
            SUM(CASE WHEN additional_files IS NOT NULL THEN 1 ELSE 0 END) as with_additional
        FROM papers
    ''')
    
    stats = cursor.fetchone()
    print(f"\nFile Statistics:")
    print(f"  Total papers:              {stats['total']}")
    print(f"  With past papers:          {stats['with_pp']}")
    print(f"  With JABchem marking:      {stats['with_jab']}")
    print(f"  With SQA marking:          {stats['with_sqa']}")
    print(f"  With additional files:     {stats['with_additional']}")
    
    conn.close()
    return total_papers

def audit_markdown_files():
    """Audit generated markdown files"""
    print("\n" + "="*70)
    print("MARKDOWN FILES AUDIT")
    print("="*70)
    
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', '..', '_downloads')
    
    by_subject = defaultdict(lambda: defaultdict(int))
    total_files = 0
    
    for subject in os.listdir(downloads_dir):
        subject_path = os.path.join(downloads_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        
        for level in os.listdir(subject_path):
            level_path = os.path.join(subject_path, level)
            if not os.path.isdir(level_path):
                continue
            
            md_files = [f for f in os.listdir(level_path) if f.endswith('.md')]
            count = len(md_files)
            by_subject[subject][level] = count
            total_files += count
    
    for subject in sorted(by_subject.keys()):
        print(f"\n{subject}:")
        print("-"*70)
        for level in sorted(by_subject[subject].keys()):
            count = by_subject[subject][level]
            print(f"  {level}: {count} files")
    
    print("\n" + "="*70)
    print(f"TOTAL MARKDOWN FILES: {total_files}")
    print("="*70)
    
    return total_files

def audit_pdf_files():
    """Audit PDF files on filesystem"""
    print("\n" + "="*70)
    print("PDF FILES AUDIT")
    print("="*70)
    
    subjects = ['chemistry', 'biology', 'physics', 'maths']
    by_subject = defaultdict(lambda: defaultdict(int))
    total_pdfs = 0
    
    for subject in subjects:
        subject_path = os.path.join(os.path.dirname(__file__), '..', '..', subject)
        if not os.path.exists(subject_path):
            continue
        
        for root, dirs, files in os.walk(subject_path):
            level = os.path.basename(root)
            pdf_count = len([f for f in files if f.lower().endswith('.pdf')])
            if pdf_count > 0:
                by_subject[subject][level] += pdf_count
                total_pdfs += pdf_count
    
    for subject in sorted(by_subject.keys()):
        print(f"\n{subject}:")
        print("-"*70)
        total_subject = 0
        for level in sorted(by_subject[subject].keys()):
            count = by_subject[subject][level]
            print(f"  {level}: {count} PDFs")
            total_subject += count
        print(f"  TOTAL: {total_subject} PDFs")
    
    print("\n" + "="*70)
    print(f"TOTAL PDF FILES: {total_pdfs}")
    print("="*70)
    
    return total_pdfs

def check_specific_content():
    """Check for specific content that was reported missing"""
    print("\n" + "="*70)
    print("SPECIFIC CONTENT CHECKS")
    print("="*70)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'db', 'jabchem.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    checks = [
        ("Chemistry AH - SQA Marking Schemes", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Advanced Higher' AND c.slug='sqapastpapersah' AND p.sqa_marking_path IS NOT NULL"),
        
        ("Chemistry AH - Self Evaluation", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Advanced Higher' AND c.slug='ahselfevaluation'"),
        
        ("Chemistry AH - Course Notes", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Advanced Higher' AND c.slug='ahcoursenotesandexercises'"),
        
        ("Chemistry Higher - Self Evaluation", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Higher' AND c.slug='higherselfevaluation'"),
        
        ("Chemistry N5 - Self Evaluation", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='National 5' AND c.slug='n5selfevaluation'"),
        
        ("Chemistry N5 - Exercises", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='National 5' AND c.slug='n5exercises'"),
        
        ("Chemistry Archive - Int 1 Materials", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Archive' AND c.slug='coursematerialsint1'"),
        
        ("Chemistry Additional Materials", 
         "SELECT COUNT(*) FROM papers p JOIN categories c ON p.category_id = c.id JOIN levels l ON c.level_id = l.id JOIN subjects s ON l.subject_id = s.id WHERE s.name='Chemistry' AND l.name='Additional'"),
    ]
    
    print()
    for name, query in checks:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        status = "✓" if count > 0 else "✗"
        print(f"{status} {name}: {count} items")
    
    conn.close()

def main():
    print("="*70)
    print("JABCHEM CONTENT AUDIT")
    print("="*70)
    print("\nThis script audits all content in the database, markdown files,")
    print("and PDF files to ensure everything is present.\n")
    
    # Run audits
    db_papers = audit_database()
    md_files = audit_markdown_files()
    pdf_files = audit_pdf_files()
    check_specific_content()
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Database papers:     {db_papers}")
    print(f"Markdown files:      {md_files}")
    print(f"PDF files:           {pdf_files}")
    print()
    
    if db_papers == md_files:
        print("✓ Database and markdown files match!")
    else:
        print(f"✗ Mismatch: {db_papers} papers vs {md_files} markdown files")
    
    print("\n" + "="*70)
    print("\nTo compare with live site:")
    print("  1. Visit https://jabchem.org.uk")
    print("  2. Check each subject/level page")
    print("  3. Compare paper counts and content")
    print("  4. Verify all links work")
    print()
    print("Local preview: http://localhost:3001/preview/")
    print("="*70)

if __name__ == '__main__':
    main()
