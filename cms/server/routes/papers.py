from flask import Blueprint, jsonify, request
import os
from datetime import datetime
from utils.file_handler import generate_markdown_file_for_paper

def create_papers_blueprint(db):
    bp = Blueprint('papers', __name__, url_prefix='/api/papers')
    
    @bp.route('/category/<int:category_id>', methods=['GET'])
    def get_papers_by_category(category_id):
        """Get all papers in a category"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM papers 
                WHERE category_id = ? 
                ORDER BY year DESC
            ''', (category_id,))
            papers = [dict(row) for row in cursor.fetchall()]
            return jsonify(papers)
    
    @bp.route('/<int:paper_id>', methods=['GET'])
    def get_paper(paper_id):
        """Get single paper"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            paper = cursor.fetchone()
            
            if not paper:
                return jsonify({'error': 'Paper not found'}), 404
            
            return jsonify(dict(paper))
    
    @bp.route('', methods=['POST'])
    def create_paper():
        """Create new paper"""
        data = request.get_json()
        
        required_fields = ['year', 'category_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert paper
            cursor.execute('''
                INSERT INTO papers (
                    year, category_id, past_paper_path, 
                    jabchem_marking_path, sqa_marking_path, additional_files
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['year'],
                data['category_id'],
                data.get('past_paper_path'),
                data.get('jabchem_marking_path'),
                data.get('sqa_marking_path'),
                data.get('additional_files')
            ))
            
            paper_id = cursor.lastrowid
            
            # Get paper with relationships for markdown generation
            cursor.execute('''
                SELECT 
                    p.*,
                    c.slug as category_slug,
                    l.name as level_name,
                    l.slug as level_slug,
                    s.name as subject_name,
                    s.slug as subject_slug
                FROM papers p
                JOIN categories c ON p.category_id = c.id
                JOIN levels l ON c.level_id = l.id
                JOIN subjects s ON l.subject_id = s.id
                WHERE p.id = ?
            ''', (paper_id,))
            
            paper_with_relations = dict(cursor.fetchone())
            
            # Generate markdown file immediately
            try:
                generate_markdown_file_for_paper(
                    paper_with_relations,
                    paper_with_relations['subject_slug'],
                    paper_with_relations['level_slug'],
                    paper_with_relations['category_slug'],
                    paper_with_relations['subject_name'],
                    paper_with_relations['level_name']
                )
            except Exception as e:
                print(f"Error generating markdown: {e}")
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            paper = dict(cursor.fetchone())
            
            return jsonify(paper), 201
    
    @bp.route('/<int:paper_id>', methods=['PUT'])
    def update_paper(paper_id):
        """Update paper"""
        data = request.get_json()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Paper not found'}), 404
            
            cursor.execute('''
                UPDATE papers SET
                    year = ?,
                    category_id = ?,
                    past_paper_path = ?,
                    jabchem_marking_path = ?,
                    sqa_marking_path = ?,
                    additional_files = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('year'),
                data.get('category_id'),
                data.get('past_paper_path'),
                data.get('jabchem_marking_path'),
                data.get('sqa_marking_path'),
                data.get('additional_files'),
                paper_id
            ))
            
            # Get paper with relationships for markdown generation
            cursor.execute('''
                SELECT 
                    p.*,
                    c.slug as category_slug,
                    l.name as level_name,
                    l.slug as level_slug,
                    s.name as subject_name,
                    s.slug as subject_slug
                FROM papers p
                JOIN categories c ON p.category_id = c.id
                JOIN levels l ON c.level_id = l.id
                JOIN subjects s ON l.subject_id = s.id
                WHERE p.id = ?
            ''', (paper_id,))
            
            paper_with_relations = dict(cursor.fetchone())
            
            # Regenerate markdown file
            try:
                generate_markdown_file_for_paper(
                    paper_with_relations,
                    paper_with_relations['subject_slug'],
                    paper_with_relations['level_slug'],
                    paper_with_relations['category_slug'],
                    paper_with_relations['subject_name'],
                    paper_with_relations['level_name']
                )
            except Exception as e:
                print(f"Error generating markdown: {e}")
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            paper = dict(cursor.fetchone())
            
            return jsonify(paper)
    
    @bp.route('/<int:paper_id>', methods=['DELETE'])
    def delete_paper(paper_id):
        """Delete paper"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            paper = cursor.fetchone()
            
            if not paper:
                return jsonify({'error': 'Paper not found'}), 404
            
            cursor.execute('DELETE FROM papers WHERE id = ?', (paper_id,))
            
            return jsonify({'success': True, 'message': 'Paper deleted'})
    
    @bp.route('/<int:paper_id>/file/<file_type>', methods=['DELETE'])
    def delete_paper_file(paper_id, file_type):
        """Delete specific file from paper"""
        file_field_map = {
            'past_paper': 'past_paper_path',
            'jabchem_marking': 'jabchem_marking_path',
            'sqa_marking': 'sqa_marking_path'
        }
        
        if file_type not in file_field_map:
            return jsonify({'error': 'Invalid file type'}), 400
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            paper = cursor.fetchone()
            
            if not paper:
                return jsonify({'error': 'Paper not found'}), 404
            
            field_name = file_field_map[file_type]
            file_path = paper[field_name]
            
            if file_path:
                full_path = os.path.join('..', file_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            cursor.execute(f'UPDATE papers SET {field_name} = NULL WHERE id = ?', (paper_id,))
            
            return jsonify({'success': True, 'message': 'File deleted'})
    
    return bp
