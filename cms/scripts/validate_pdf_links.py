#!/usr/bin/env python3
"""
Comprehensive PDF Link Validation Script
Tests every PDF link in the database to ensure files exist and are accessible.
Flags broken links and attempts to fix them by searching for the files.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

class PDFValidator:
    def __init__(self, db_path, root_dir):
        self.db_path = db_path
        self.root_dir = root_dir
        self.issues = []
        self.stats = {
            'total_papers': 0,
            'total_links': 0,
            'valid_links': 0,
            'broken_links': 0,
            'fixed_links': 0,
            'unfixable_links': 0
        }
        
        # Build a cache of all PDF files
        self.pdf_cache = self._build_pdf_cache()
    
    def _build_pdf_cache(self):
        """Build a cache of all PDF files in the project"""
        print("Building PDF file cache...")
        cache = {}
        
        subjects = ['chemistry', 'maths', 'physics', 'biology']
        for subject in subjects:
            subject_path = os.path.join(self.root_dir, subject)
            if not os.path.exists(subject_path):
                continue
            
            for root, dirs, files in os.walk(subject_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.root_dir)
                        
                        # Store by filename (for fuzzy matching)
                        filename_lower = file.lower()
                        if filename_lower not in cache:
                            cache[filename_lower] = []
                        cache[filename_lower].append('/' + rel_path)
        
        print(f"  Found {len(cache)} unique PDF filenames")
        return cache
    
    def _check_file_exists(self, path):
        """Check if a file exists given a path starting with /"""
        if not path:
            return False
        
        # Remove leading slash
        rel_path = path.lstrip('/')
        full_path = os.path.join(self.root_dir, rel_path)
        return os.path.isfile(full_path)
    
    def _find_similar_file(self, path):
        """Try to find a similar file if the exact path doesn't exist"""
        if not path:
            return None
        
        # Extract filename
        filename = os.path.basename(path)
        filename_lower = filename.lower()
        
        # Try exact filename match
        if filename_lower in self.pdf_cache:
            matches = self.pdf_cache[filename_lower]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                # Multiple matches - try to find best match based on path similarity
                path_parts = path.lower().split('/')
                best_match = None
                best_score = 0
                
                for match in matches:
                    match_parts = match.lower().split('/')
                    score = sum(1 for p in path_parts if p in match_parts)
                    if score > best_score:
                        best_score = score
                        best_match = match
                
                return best_match
        
        # Try without spaces
        filename_no_spaces = filename.replace(' ', '').lower()
        if filename_no_spaces in self.pdf_cache:
            matches = self.pdf_cache[filename_no_spaces]
            if matches:
                return matches[0]
        
        # Try fuzzy matching (remove special characters, case insensitive)
        import re
        filename_clean = re.sub(r'[^a-z0-9]', '', filename_lower)
        
        for cached_name, paths in self.pdf_cache.items():
            cached_clean = re.sub(r'[^a-z0-9]', '', cached_name)
            if cached_clean == filename_clean:
                return paths[0]
        
        return None
    
    def validate_papers(self):
        """Validate all papers in the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all papers
        cursor.execute('''
            SELECT 
                p.*,
                c.name as category_name,
                l.name as level_name,
                s.name as subject_name
            FROM papers p
            JOIN categories c ON p.category_id = c.id
            JOIN levels l ON c.level_id = l.id
            JOIN subjects s ON l.subject_id = s.id
            ORDER BY s.name, l.name, p.year
        ''')
        
        papers = cursor.fetchall()
        self.stats['total_papers'] = len(papers)
        
        print(f"\nValidating {len(papers)} papers...")
        print("="*70)
        
        updates = []
        
        for paper in papers:
            paper_dict = dict(paper)
            paper_id = paper_dict['id']
            year = paper_dict['year']
            subject = paper_dict['subject_name']
            level = paper_dict['level_name']
            
            # Check each type of file
            paths_to_check = [
                ('past_paper_path', paper_dict.get('past_paper_path')),
                ('jabchem_marking_path', paper_dict.get('jabchem_marking_path')),
                ('sqa_marking_path', paper_dict.get('sqa_marking_path'))
            ]
            
            paper_updates = {}
            
            for field_name, path in paths_to_check:
                if not path:
                    continue
                
                self.stats['total_links'] += 1
                
                if self._check_file_exists(path):
                    self.stats['valid_links'] += 1
                else:
                    # Broken link found
                    self.stats['broken_links'] += 1
                    
                    issue = {
                        'paper_id': paper_id,
                        'year': year,
                        'subject': subject,
                        'level': level,
                        'field': field_name,
                        'broken_path': path,
                        'fixed_path': None
                    }
                    
                    # Try to find the file
                    fixed_path = self._find_similar_file(path)
                    
                    if fixed_path and self._check_file_exists(fixed_path):
                        issue['fixed_path'] = fixed_path
                        paper_updates[field_name] = fixed_path
                        self.stats['fixed_links'] += 1
                        print(f"✓ FIXED: {subject} {level} {year} - {field_name}")
                        print(f"    OLD: {path}")
                        print(f"    NEW: {fixed_path}")
                    else:
                        self.stats['unfixable_links'] += 1
                        print(f"✗ BROKEN: {subject} {level} {year} - {field_name}")
                        print(f"    PATH: {path}")
                        print(f"    File not found!")
                    
                    self.issues.append(issue)
            
            # Store updates for this paper
            if paper_updates:
                updates.append((paper_id, paper_updates))
        
        conn.close()
        
        return updates
    
    def apply_fixes(self, updates, clear_unfixable=False):
        """Apply fixes to the database"""
        if not updates and not clear_unfixable:
            print("\nNo fixes to apply.")
            return
        
        print(f"\n{'='*70}")
        print(f"Applying fixes to database...")
        print("="*70)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Apply fixes
        if updates:
            for paper_id, paper_updates in updates:
                # Build UPDATE query
                set_clauses = []
                values = []
                
                for field, new_path in paper_updates.items():
                    set_clauses.append(f"{field} = ?")
                    values.append(new_path)
                
                values.append(paper_id)
                
                query = f"UPDATE papers SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
            
            print(f"✓ Applied {len(updates)} fixes")
        
        # Clear unfixable links
        if clear_unfixable:
            unfixable = [issue for issue in self.issues if not issue['fixed_path']]
            for issue in unfixable:
                cursor.execute(
                    f"UPDATE papers SET {issue['field']} = NULL WHERE id = ?",
                    (issue['paper_id'],)
                )
            print(f"✓ Cleared {len(unfixable)} unfixable links (set to NULL)")
        
        conn.commit()
        conn.close()
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        print(f"Total Papers:        {self.stats['total_papers']}")
        print(f"Total PDF Links:     {self.stats['total_links']}")
        print(f"Valid Links:         {self.stats['valid_links']} ✓")
        print(f"Broken Links:        {self.stats['broken_links']} ✗")
        print(f"  - Fixed:           {self.stats['fixed_links']} ✓")
        print(f"  - Unfixable:       {self.stats['unfixable_links']} ✗")
        
        if self.stats['total_links'] > 0:
            success_rate = (self.stats['valid_links'] + self.stats['fixed_links']) / self.stats['total_links'] * 100
            print(f"\nSuccess Rate:        {success_rate:.1f}%")
        
        # List unfixable issues
        unfixable = [issue for issue in self.issues if not issue['fixed_path']]
        if unfixable:
            print("\n" + "="*70)
            print("UNFIXABLE ISSUES")
            print("="*70)
            for issue in unfixable:
                print(f"\n{issue['subject']} {issue['level']} {issue['year']}")
                print(f"  Field: {issue['field']}")
                print(f"  Path:  {issue['broken_path']}")
        
        print("\n" + "="*70)
    
    def save_report(self, filename='validation_report.json'):
        """Save detailed report to JSON file"""
        report = {
            'stats': self.stats,
            'issues': self.issues
        }
        
        report_path = os.path.join(os.path.dirname(__file__), filename)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate PDF links in JABchem database')
    parser.add_argument('--auto-fix', action='store_true', 
                       help='Automatically apply fixes without prompting')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output, only show errors')
    args = parser.parse_args()
    
    if not args.quiet:
        print("="*70)
        print("PDF Link Validation Script")
        print("="*70)
    
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '..', 'server', 'db', 'jabchem.db')
    root_dir = os.path.join(script_dir, '..', '..')
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return 1
    
    # Create validator
    validator = PDFValidator(db_path, root_dir)
    
    # Validate all papers
    updates = validator.validate_papers()
    
    # Print report
    if not args.quiet:
        validator.print_report()
    elif validator.stats['broken_links'] > 0:
        print(f"Found {validator.stats['broken_links']} broken links")
    
    # Apply fixes
    if args.auto_fix:
        if updates or validator.stats['unfixable_links'] > 0:
            validator.apply_fixes(updates, clear_unfixable=True)
            if not args.quiet:
                print("\n✓ Database updated automatically")
    else:
        # Ask to apply fixes
        if updates or validator.stats['unfixable_links'] > 0:
            print("\n" + "="*70)
            
            if updates:
                response = input(f"\nApply {len(updates)} automatic fixes to database? (yes/no): ")
                apply_fixes = response.lower() == 'yes'
            else:
                apply_fixes = False
            
            clear_unfixable = False
            if validator.stats['unfixable_links'] > 0:
                print("\nUnfixable links are likely files that don't exist.")
                response = input(f"Clear {validator.stats['unfixable_links']} unfixable links (set to NULL)? (yes/no): ")
                clear_unfixable = response.lower() == 'yes'
            
            if apply_fixes or clear_unfixable:
                validator.apply_fixes(updates, clear_unfixable)
                print("\n✓ Database updated! Run this script again to verify.")
                print("  Then regenerate markdown files and rebuild Jekyll site:")
                print("    curl -X POST http://localhost:3001/api/publish/test")
            else:
                print("\nNo changes applied.")
    
    # Save detailed report
    if not args.quiet:
        validator.save_report()
    
    # Return exit code based on remaining issues
    if validator.stats['unfixable_links'] > 0 and not args.auto_fix:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
