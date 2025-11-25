from flask import Blueprint, jsonify, request
import os
import re
from werkzeug.utils import secure_filename
from utils.file_handler import generate_markdown_file_for_paper

def create_upload_blueprint(db):
    bp = Blueprint('upload', __name__, url_prefix='/api/upload')
    
    def sanitize_year(year):
        """Remove special characters from year"""
        return re.sub(r'[^a-zA-Z0-9]', '', year)
    
    def handle_file_upload(file, subject, level, year, file_type):
        """Handle single file upload"""
        # Validate PDF
        if not file.filename.lower().endswith('.pdf'):
            return None, 'Only PDF files allowed'
        
        # Normalize inputs
        subject = subject.lower()
        level = level.lower().replace(' ', '')
        
        # Create directory
        upload_dir = os.path.join('..', subject, level)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Use original filename (sanitized)
        original_filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, original_filename)
        
        # Handle duplicates by adding counter
        counter = 1
        while os.path.exists(filepath):
            base, ext = os.path.splitext(original_filename)
            new_filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(upload_dir, new_filename)
            counter += 1
        
        # Save file
        file.save(filepath)
        
        # Return relative path
        relative_path = f"/{subject}/{level}/{os.path.basename(filepath)}"
        return relative_path, None
    
    @bp.route('', methods=['POST'])
    def upload_file():
        """Upload single PDF file and create/update paper in database"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        subject = request.form.get('subject', '')
        level = request.form.get('level', '')
        year = request.form.get('year', '')
        file_type = request.form.get('type', '')
        category_id = request.form.get('category_id')
        
        if not all([subject, level, year, file_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Upload the file
        path, error = handle_file_upload(file, subject, level, year, file_type)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Create or update paper in database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # If category_id provided, use it; otherwise try to find default category
            if not category_id:
                # Get subject and level IDs
                cursor.execute('SELECT id FROM subjects WHERE slug = ?', (subject,))
                subject_row = cursor.fetchone()
                if not subject_row:
                    return jsonify({'error': 'Subject not found'}), 404
                subject_id = subject_row['id']
                
                cursor.execute('SELECT id FROM levels WHERE subject_id = ? AND slug = ?', (subject_id, level))
                level_row = cursor.fetchone()
                if not level_row:
                    return jsonify({'error': 'Level not found'}), 404
                level_id = level_row['id']
                
                # Try to find a default category or create one
                cursor.execute('SELECT id FROM categories WHERE level_id = ? LIMIT 1', (level_id,))
                category_row = cursor.fetchone()
                if category_row:
                    category_id = category_row['id']
                else:
                    # Create default category
                    cursor.execute('''
                        INSERT INTO categories (name, slug, level_id)
                        VALUES (?, ?, ?)
                    ''', (f'Papers', 'papers', level_id))
                    category_id = cursor.lastrowid
            
            # Check if paper already exists for this year and category
            cursor.execute('''
                SELECT id FROM papers WHERE year = ? AND category_id = ?
            ''', (year, category_id))
            existing_paper = cursor.fetchone()
            
            # Map file type to database field
            field_map = {
                'past_paper': 'past_paper_path',
                'jabchem_marking': 'jabchem_marking_path',
                'sqa_marking': 'sqa_marking_path'
            }
            field_name = field_map.get(file_type)
            
            if existing_paper:
                # Update existing paper
                paper_id = existing_paper['id']
                cursor.execute(f'''
                    UPDATE papers SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (path, paper_id))
            else:
                # Create new paper
                cursor.execute(f'''
                    INSERT INTO papers (year, category_id, {field_name})
                    VALUES (?, ?, ?)
                ''', (year, category_id, path))
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
                md_path = generate_markdown_file_for_paper(
                    paper_with_relations,
                    paper_with_relations['subject_slug'],
                    paper_with_relations['level_slug'],
                    paper_with_relations['category_slug'],
                    paper_with_relations['subject_name'],
                    paper_with_relations['level_name']
                )
                print(f"Generated markdown: {md_path}")
            except Exception as e:
                print(f"Error generating markdown: {e}")
        
        return jsonify({
            'success': True,
            'path': path,
            'paper_id': paper_id,
            'message': 'File uploaded and paper created successfully'
        })
    
    @bp.route('/bulk', methods=['POST'])
    def upload_bulk():
        """Upload multiple PDF files"""
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        subject = request.form.get('subject', '')
        level = request.form.get('level', '')
        year = request.form.get('year', '')
        
        if not all([subject, level, year]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        results = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
            
            # Determine file type from filename
            filename_lower = file.filename.lower()
            if 'past' in filename_lower or 'paper' in filename_lower:
                file_type = 'past_paper'
            elif 'jabchem' in filename_lower or 'jab' in filename_lower:
                file_type = 'jabchem_marking'
            elif 'sqa' in filename_lower or 'marking' in filename_lower:
                file_type = 'sqa_marking'
            else:
                file_type = 'additional'
            
            path, error = handle_file_upload(file, subject, level, year, file_type)
            
            if error:
                errors.append({'filename': file.filename, 'error': error})
            else:
                results.append({'filename': file.filename, 'path': path, 'type': file_type})
        
        return jsonify({
            'success': len(errors) == 0,
            'uploaded': results,
            'errors': errors,
            'message': f'Uploaded {len(results)} files'
        })
    
    return bp
