#!/usr/bin/env python3
"""
Compare local Jekyll build with live jabchem.org.uk site
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

def get_page_content(url):
    """Fetch and parse a page"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_table_data(soup):
    """Extract table data from page"""
    tables = []
    
    # Find all tables
    for table_elem in soup.find_all('table'):
        table_data = {
            'title': '',
            'rows': []
        }
        
        # Try to find table title (usually in h3 before table)
        prev_elem = table_elem.find_previous('h3')
        if prev_elem:
            table_data['title'] = prev_elem.get_text(strip=True)
        
        # Extract headers
        headers = []
        thead = table_elem.find('thead')
        if thead:
            for th in thead.find_all('th'):
                headers.append(th.get_text(strip=True))
        
        # Extract rows
        tbody = table_elem.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    # Get text and count links
                    text = td.get_text(strip=True)
                    links = len(td.find_all('a'))
                    row.append({
                        'text': text,
                        'links': links
                    })
                if row:
                    table_data['rows'].append(row)
        
        if table_data['rows']:
            tables.append(table_data)
    
    return tables

def compare_pages(live_url, local_url):
    """Compare live and local pages"""
    print(f"\nComparing: {live_url}")
    print("="*70)
    
    # Fetch both pages
    live_soup = get_page_content(live_url)
    local_soup = get_page_content(local_url)
    
    if not live_soup or not local_soup:
        print("  ✗ Could not fetch one or both pages")
        return False
    
    # Extract table data
    live_tables = extract_table_data(live_soup)
    local_tables = extract_table_data(local_soup)
    
    print(f"  Live tables: {len(live_tables)}")
    print(f"  Local tables: {len(local_tables)}")
    
    if len(live_tables) != len(local_tables):
        print(f"  ⚠️  Table count mismatch!")
        return False
    
    # Compare each table
    all_match = True
    for i, (live_table, local_table) in enumerate(zip(live_tables, local_tables)):
        live_rows = len(live_table['rows'])
        local_rows = len(local_table['rows'])
        
        title = live_table['title'] or f"Table {i+1}"
        
        if live_rows == local_rows:
            print(f"  ✓ {title}: {live_rows} rows")
        else:
            print(f"  ✗ {title}: {live_rows} live vs {local_rows} local")
            all_match = False
            
            # Show difference
            if live_rows > local_rows:
                print(f"    Missing {live_rows - local_rows} rows locally")
            else:
                print(f"    Extra {local_rows - live_rows} rows locally")
    
    return all_match

def main():
    print("="*70)
    print("JABCHEM LIVE vs LOCAL COMPARISON")
    print("="*70)
    print("\nComparing live site (jabchem.org.uk) with local build")
    print("This will check table counts and row counts for each page.\n")
    
    # Define pages to check
    pages = [
        # Chemistry
        ('chemistry/advancedhigher', 'Chemistry Advanced Higher'),
        ('chemistry/higher', 'Chemistry Higher'),
        ('chemistry/national5', 'Chemistry National 5'),
        ('chemistry/archive', 'Chemistry Archive'),
        ('chemistry/additional', 'Chemistry Additional'),
        
        # Biology
        ('biology/advancedhigher', 'Biology Advanced Higher'),
        ('biology/higher', 'Biology Higher'),
        ('biology/national5', 'Biology National 5'),
        ('biology/archive', 'Biology Archive'),
        
        # Physics
        ('physics/advancedhigher', 'Physics Advanced Higher'),
        ('physics/higher', 'Physics Higher'),
        ('physics/national5', 'Physics National 5'),
        ('physics/archive', 'Physics Archive'),
        ('physics/additional', 'Physics Additional'),
        
        # Maths
        ('maths/advancedhigher', 'Maths Advanced Higher'),
        ('maths/higher', 'Maths Higher'),
        ('maths/national5', 'Maths National 5'),
        ('maths/archive', 'Maths Archive'),
    ]
    
    results = {
        'match': [],
        'mismatch': [],
        'error': []
    }
    
    for path, name in pages:
        live_url = f"https://jabchem.org.uk/{path}"
        local_url = f"http://localhost:3001/preview/{path}"
        
        try:
            if compare_pages(live_url, local_url):
                results['match'].append(name)
            else:
                results['mismatch'].append(name)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['error'].append(name)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✓ Matching pages:    {len(results['match'])}")
    print(f"✗ Mismatched pages:  {len(results['mismatch'])}")
    print(f"⚠️  Error pages:      {len(results['error'])}")
    
    if results['mismatch']:
        print("\nMismatched pages:")
        for page in results['mismatch']:
            print(f"  - {page}")
    
    if results['error']:
        print("\nError pages:")
        for page in results['error']:
            print(f"  - {page}")
    
    print("\n" + "="*70)
    
    if len(results['match']) == len(pages):
        print("✓ All pages match!")
        return 0
    else:
        print("⚠️  Some pages have differences")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
