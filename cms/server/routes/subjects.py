from flask import Blueprint, jsonify

def create_subjects_blueprint(db):
    bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')
    
    @bp.route('', methods=['GET'])
    def get_subjects():
        """Get all subjects"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM subjects ORDER BY name')
            subjects = [dict(row) for row in cursor.fetchall()]
            return jsonify(subjects)
    
    @bp.route('/<int:subject_id>', methods=['GET'])
    def get_subject(subject_id):
        """Get subject with its levels"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,))
            subject = cursor.fetchone()
            
            if not subject:
                return jsonify({'error': 'Subject not found'}), 404
            
            subject_dict = dict(subject)
            
            cursor.execute('SELECT * FROM levels WHERE subject_id = ? ORDER BY name', (subject_id,))
            levels = [dict(row) for row in cursor.fetchall()]
            subject_dict['levels'] = levels
            
            return jsonify(subject_dict)
    
    return bp
