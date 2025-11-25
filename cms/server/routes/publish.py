from flask import Blueprint, jsonify, request
from utils.git_handler import GitHandler
from utils.file_handler import generate_markdown_files

def create_publish_blueprint(db):
    bp = Blueprint('publish', __name__, url_prefix='/api/publish')
    
    @bp.route('', methods=['POST'])
    def publish_changes():
        """Generate markdown and push to GitHub"""
        try:
            data = request.get_json() or {}
            message = data.get('message', 'Update from CMS')
            
            # Generate markdown files
            paper_count = generate_markdown_files(db)
            print(f"Generated {paper_count} markdown files")
            
            # Git operations
            git_handler = GitHandler()
            
            if not git_handler.has_changes():
                return jsonify({
                    'success': True,
                    'message': 'No changes to publish'
                })
            
            git_handler.add_all()
            commit_hash = git_handler.commit(message)
            
            if not commit_hash:
                return jsonify({
                    'success': True,
                    'message': 'No changes to publish'
                })
            
            git_handler.push()
            
            # Log to database
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO publish_history (commit_hash, message, status)
                    VALUES (?, ?, ?)
                ''', (commit_hash, message, 'success'))
            
            return jsonify({
                'success': True,
                'message': 'Changes published successfully',
                'commit': commit_hash,
                'papers_generated': paper_count
            })
            
        except Exception as e:
            # Log error to database
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO publish_history (message, status)
                        VALUES (?, ?)
                    ''', (str(e), 'failed'))
            except:
                pass
            
            print(f"Publish error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/history', methods=['GET'])
    def get_publish_history():
        """Get publish history"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM publish_history 
                ORDER BY published_at DESC 
                LIMIT 50
            ''')
            history = [dict(row) for row in cursor.fetchall()]
            return jsonify(history)
    
    return bp
