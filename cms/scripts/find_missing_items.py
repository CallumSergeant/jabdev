#!/usr/bin/env python3
"""
Find specific missing items by comparing live site with local
"""

import requests
from bs4 import BeautifulSoup
import re

def get_table_details(url):
    """Get detailed table information from a page"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        tables = []
        for table_elem in soup.find_all('table'):
            # Get table title
            title = ''
            prev_elem = table_elem.find_previous('h3')
            if prev_elem:
                title = prev_elem.get_text(strip=True)
            
            # Get headers
            headers = []
            thead = table_elem.find('thead')
            if thead:
                for th in thead.find_all('th'):
                    headers.append(th.get_text(strip=True))
            
            # Get all rows with details
            rows = []
            tbody = table_elem.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    row_data = []
                    for td in tr.find_all('td'):
                        cell = {
                            'text': td.get_text(strip=True),
                            'links': []
                        }
                        # Get all links in cell
                        for a in td.find_all('a'):
                            href = a.get('href', '')
                            text = a.get_text(strip=True)
                            cell['links'].append({'href': href, 'text': text})
                        row_data.append(cell)
                    if row_data:
                        rows.append(row_data)
            
            tables.append({
                'title': title,
                'headers': headers,
                'rows': rows
            })
        
        return tables
    except Exception as e:
        print(f"Error: {e}")
        return []

def compare_and_show_missing(live_url, local_url, page_name):
    """Compare and show exactly what's missing"""
    print(f"\n{'='*70}")
    print(f"{page_name}")
    print('='*70)
    
    live_tables = get_table_details(live_url)
    local_tables = get_table_details(local_url)
    
    if len(live_tables) != len(local_tables):
        print(f"⚠️  Table count: {len(live_tables)} live vs {len(local_tables)} local")
        
        # Show which tables are missing
        live_titles = [t['title'] for t in live_tables]
        local_titles = [t['title'] for t in local_tables]
        
        for title in live_titles:
            if title not in local_titles:
                print(f"\n✗ MISSING TABLE: {title}")
                # Find the table
                for table in live_tables:
                    if table['title'] == title:
                        print(f"  Headers: {', '.join(table['headers'])}")
                        print(f"  Rows: {len(table['rows'])}")
                        print(f"\n  Sample rows:")
                        for i, row in enumerate(table['rows'][:3]):
                            print(f"    Row {i+1}: {[cell['text'] for cell in row]}")
        return
    
    # Compare each table
    for live_table, local_table in zip(live_tables, local_tables):
        title = live_table['title']
        live_count = len(live_table['rows'])
        local_count = len(local_table['rows'])
        
        if live_count != local_count:
            print(f"\n✗ {title}: {live_count} live vs {local_count} local")
            print(f"  Missing {live_count - local_count} rows")
            
            # Find missing rows by comparing first column (usually year or identifier)
            live_ids = set()
            local_ids = set()
            
            for row in live_table['rows']:
                if row:
                    live_ids.add(row[0]['text'])
            
            for row in local_table['rows']:
                if row:
                    local_ids.add(row[0]['text'])
            
            missing = live_ids - local_ids
            if missing:
                print(f"\n  Missing items: {sorted(missing)}")
                
                # Show details of missing items
                for item_id in sorted(missing):
                    for row in live_table['rows']:
                        if row and row[0]['text'] == item_id:
                            print(f"\n  Item: {item_id}")
                            for i, cell in enumerate(row):
                                if i < len(live_table['headers']):
                                    header = live_table['headers'][i]
                                    print(f"    {header}: {cell['text']}")
                                    if cell['links']:
                                        for link in cell['links']:
                                            print(f"      Link: {link['text']} -> {link['href']}")
        else:
            print(f"✓ {title}: {live_count} rows match")

def main():
    print("="*70)
    print("DETAILED MISSING ITEMS REPORT")
    print("="*70)
    
    # Pages with mismatches
    pages = [
        ('chemistry/advancedhigher', 'Chemistry Advanced Higher'),
        ('chemistry/higher', 'Chemistry Higher'),
        ('chemistry/national5', 'Chemistry National 5'),
        ('chemistry/archive', 'Chemistry Archive'),
        ('chemistry/additional', 'Chemistry Additional'),
        ('physics/national5', 'Physics National 5'),
        ('maths/higher', 'Maths Higher'),
    ]
    
    for path, name in pages:
        live_url = f"https://jabchem.org.uk/{path}"
        local_url = f"http://localhost:3001/preview/{path}"
        compare_and_show_missing(live_url, local_url, name)
    
    print("\n" + "="*70)
    print("END OF REPORT")
    print("="*70)

if __name__ == '__main__':
    main()
