from flask import Blueprint, jsonify, request
import os
from utils.git_handler import GitHandler
from utils.file_handler import generate_markdown_files

def create_publish_blueprint(db):
    bp = Blueprint('publish', __name__, url_prefix='/api/publish')
    
    @bp.route('/test', methods=['POST'])
    def test_deploy():
        """Generate markdown files and build Jekyll site locally without pushing"""
        import subprocess
        try:
            # Generate markdown files
            paper_count = generate_markdown_files(db)
            print(f"Generated {paper_count} markdown files")
            
            # Build Jekyll site
            build_dir = os.path.abspath('..')
            
            # Try to find bundle in common locations
            bundle_paths = [
                os.path.expanduser('~/.gem/ruby/2.7.0/bin/bundle'),
                '/usr/local/bin/bundle',
                '/usr/bin/bundle',
                'bundle'  # fallback to PATH
            ]
            
            bundle_cmd = None
            for path in bundle_paths:
                if os.path.exists(path) or path == 'bundle':
                    bundle_cmd = path
                    break
            
            if not bundle_cmd:
                return jsonify({'error': 'Bundle not found. Please install Jekyll dependencies.'}), 500
            
            result = subprocess.run(
                [bundle_cmd, 'exec', 'jekyll', 'build'],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': 'Test build completed successfully',
                    'papers_generated': paper_count,
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Jekyll build failed',
                    'output': result.stderr
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Build timed out after 60 seconds'}), 500
        except FileNotFoundError:
            return jsonify({'error': 'Jekyll not found. Make sure bundle and jekyll are installed.'}), 500
        except Exception as e:
            print(f"Test deploy error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
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
