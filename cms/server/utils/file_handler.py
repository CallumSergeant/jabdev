import os
import yaml

def generate_markdown_file_for_paper(paper_dict, subject_slug, level_slug, category_slug, subject_name, level_name):
    """Generate a single Jekyll markdown file for a paper"""
    import json
    
    # Create directory structure
    output_dir = os.path.join('..', '_downloads', subject_slug, level_slug)
    os.makedirs(output_dir, exist_ok=True)
    
    # Build frontmatter
    frontmatter = {
        'title': paper_dict['year'],
        'level': level_name,
        'category': category_slug,
        'subject': subject_name
    }
    
    # Check if this is an additional materials paper (has additional_files)
    if paper_dict.get('additional_files'):
        try:
            additional_data = json.loads(paper_dict['additional_files'])
            # Add all additional fields to frontmatter
            frontmatter.update(additional_data)
        except (json.JSONDecodeError, TypeError):
            pass
    else:
        # Standard paper format
        frontmatter['Year'] = paper_dict['year']
        
        # Add file paths if they exist
        if paper_dict.get('past_paper_path'):
            frontmatter['Past Paper'] = [{
                'url': paper_dict['past_paper_path'],
                'link_text': f"{paper_dict['year']} Past Paper"
            }]
        
        if paper_dict.get('jabchem_marking_path'):
            frontmatter['JABchem Marking Scheme'] = [{
                'url': paper_dict['jabchem_marking_path'],
                'link_text': 'JABchem Solutions'
            }]
        
        if paper_dict.get('sqa_marking_path'):
            frontmatter['SQA Marking Scheme'] = [{
                'url': paper_dict['sqa_marking_path'],
                'link_text': 'SQA Solutions'
            }]
    
    # Generate markdown file
    filename = f"{paper_dict['year']}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write('---\n')
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
        f.write('---\n')
    
    return filepath

def generate_markdown_files(db):
    """Generate Jekyll markdown files from database for all papers"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get all papers with their relationships
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
        
        papers = cursor.fetchall()
        
        for paper in papers:
            paper_dict = dict(paper)
            generate_markdown_file_for_paper(
                paper_dict,
                paper_dict['subject_slug'],
                paper_dict['level_slug'],
                paper_dict['category_slug'],
                paper_dict['subject_name'],
                paper_dict['level_name']
            )
        
        return len(papers)
