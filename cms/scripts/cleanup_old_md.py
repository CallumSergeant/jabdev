#!/usr/bin/env python3
"""
Clean up old markdown files with rel/)
These are duplicates - the correct files are generated from the database
"""

import os
import sys
import shutil
from datetime import datetime

def find_files_with_relative_p
    """Find all markdown files with relative pa""
    files_to_remove = []
    
    )
    downloads_dir 
    
    for root, dirs, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.md'):
                filepatht, file)
                
                try:
                    with open(filepath, 'r', encodi
                        content = f.read()
                    
                    if '/../' in content:
                        files_to_remove.append(file
                except Exception as e:
    
    
e

def main():
    print("="*70)
    print("Clean Up Old Markdown Files")
    print("="*70)
    /).")
    print("These are duplicates - correct 
    nt()
    
    # Find files
    files = find_files_with_relative_paths()
    
    if not files:
    )
        return 0
    
    print(f/):")
    print("-"*70)
    
    # Show sample
    for fil:20]:
    
        print(f"  {rpath}")
    
    
        print(f"  ...
    
    print()
    ")
    print("  1. Backed up to backup_old_md/")
    print("  2. D
    
    
    response = ")
    if response.lower() != 'ye
        print("Aborted.")
        return 0
    
    # Create backup
    
    backup_dir = oamp)
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"\nBacking up to: {backup_dir}")
    
    # Backup and remove files
    removed_count = 0
    for filepath in files:
    try:
            path
            rel_p.'))
            backup_path = os.path.join(back
            
    ry
            oTrue)
            
            # Copy to backup
            shutil.copy2(ath)
            
    riginal
            os.remo
            removed_count += 1
            
        except Exception as e:
    ")
    
    print(f"\n✓ Removed {removed
    print(f"✓ B)
    print()
    print("N
    print("  1. Verify site stiw/")
    print("  2. If issue
    print("  3. Rebuild Jekyll")
    
    rn 0

if __name__:
    sys.exit(main())
