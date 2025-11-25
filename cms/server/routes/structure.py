from flask import Blueprint, jsonify, request

def create_structure_blueprint(db):
    bp = Blueprint('structure', __name__, url_prefix='/api/structure')
    
    @bp.route('', methods=['GET'])
    def get_structure():
        """Get complete site structure"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all subjects
            cursor.execute('SELECT * FROM subjects ORDER BY name')
            subjects = []
            
            for subject_row in cursor.fetchall():
                subject = dict(subject_row)
                
                # Get levels for this subject
                cursor.execute('SELECT * FROM levels WHERE subject_id = ? ORDER BY name', (subject['id'],))
                levels = []
                
                for level_row in cursor.fetchall():
                    level = dict(level_row)
                    
                    # Get categories for this level with paper count
                    cursor.execute('''
                        SELECT c.*, COUNT(p.id) as paper_count
                        FROM categories c
                        LEFT JOIN papers p ON c.id = p.category_id
                        WHERE c.level_id = ?
                        GROUP BY c.id
                        ORDER BY c.display_order, c.name
                    ''', (level['id'],))
                    
                    categories = [dict(row) for row in cursor.fetchall()]
                    level['categories'] = categories
                    levels.append(level)
                
                subject['levels'] = levels
                subjects.append(subject)
            
            return jsonify(subjects)
    
    @bp.route('/category', methods=['POST'])
    def add_category():
        """Add new category"""
        data = request.get_json()
        
        required_fields = ['name', 'slug', 'level_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if level exists
            cursor.execute('SELECT * FROM levels WHERE id = ?', (data['level_id'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Level not found'}), 404
            
            # Insert category
            cursor.execute('''
                INSERT INTO categories (name, slug, level_id, display_order, table_config)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['name'],
                data['slug'],
                data['level_id'],
                data.get('display_order', 0),
                data.get('table_config')
            ))
            
            category_id = cursor.lastrowid
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            category = dict(cursor.fetchone())
            
            return jsonify(category), 201
    
    return bp
