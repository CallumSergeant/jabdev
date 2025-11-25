from flask import Blueprint, jsonify

def create_levels_blueprint(db):
    bp = Blueprint('levels', __name__, url_prefix='/api/levels')
    
    @bp.route('/subject/<int:subject_id>', methods=['GET'])
    def get_levels_by_subject(subject_id):
        """Get all levels for a subject"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM levels WHERE subject_id = ? ORDER BY name', (subject_id,))
            levels = [dict(row) for row in cursor.fetchall()]
            return jsonify(levels)
    
    @bp.route('/<int:level_id>', methods=['GET'])
    def get_level(level_id):
        """Get level with its categories"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM levels WHERE id = ?', (level_id,))
            level = cursor.fetchone()
            
            if not level:
                return jsonify({'error': 'Level not found'}), 404
            
            level_dict = dict(level)
            
            cursor.execute('SELECT * FROM categories WHERE level_id = ? ORDER BY display_order, name', (level_id,))
            categories = [dict(row) for row in cursor.fetchall()]
            level_dict['categories'] = categories
            
            return jsonify(level_dict)
    
    return bp
