from flask import Flask, jsonify, render_template, redirect, url_for, send_from_directory, abort
from flask_cors import CORS
from config import Config
from database import Database
from routes import register_routes
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize database
db = Database(Config.DATABASE_PATH)

# Register API routes
register_routes(app, db)

# Frontend routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subjects')
def subjects_page():
    return render_template('subjects.html')

@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    return render_template('subject_detail.html', subject_id=subject_id)

@app.route('/papers/<int:category_id>')
def papers_page(category_id):
    return render_template('papers.html', category_id=category_id)

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/publish')
def publish_page():
    return render_template('publish.html')

# Preview route - serve the built Jekyll site
@app.route('/preview')
@app.route('/preview/')
def preview_root():
    """Serve the root index.html for preview"""
    from flask import Response
    site_dir = os.path.abspath(os.path.join('..', '_site'))
    
    if not os.path.exists(site_dir):
        return render_template('preview_error.html', 
                             error='Site not built yet. Click "Test Build" first.'), 404
    
    try:
        with open(os.path.join(site_dir, 'index.html'), 'r') as f:
            content = f.read()
        
        # Rewrite absolute URLs to include /preview prefix
        content = content.replace('href="/', 'href="/preview/')
        content = content.replace('src="/', 'src="/preview/')
        content = content.replace('action="/', 'action="/preview/')
        content = content.replace('/preview/preview/', '/preview/')
        
        return Response(content, mimetype='text/html')
    except Exception as e:
        print(f"Preview error: {e}")
        abort(404)

@app.route('/preview/<path:path>')
def preview_site(path):
    """Serve the built Jekyll site from _site directory"""
    from flask import Response
    import mimetypes
    
    site_dir = os.path.abspath(os.path.join('..', '_site'))
    
    if not os.path.exists(site_dir):
        return render_template('preview_error.html', 
                             error='Site not built yet. Click "Test Build" first.'), 404
    
    # If path ends with /, serve index.html from that directory
    if path.endswith('/'):
        path = os.path.join(path, 'index.html')
    
    # Try to serve the file
    try:
        file_path = os.path.join(site_dir, path)
        
        # If it's a directory, serve index.html from it
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, 'index.html')
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try adding .html
            if not path.endswith('.html'):
                file_path = os.path.join(site_dir, path + '.html')
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    abort(404)
        
        # Read and serve the file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # If it's an HTML file, rewrite URLs
        if file_path.endswith('.html'):
            content = content.decode('utf-8')
            content = content.replace('href="/', 'href="/preview/')
            content = content.replace('src="/', 'src="/preview/')
            content = content.replace('action="/', 'action="/preview/')
            content = content.replace('/preview/preview/', '/preview/')
            return Response(content, mimetype='text/html')
        
        # For non-HTML files, determine mimetype and serve
        mimetype, _ = mimetypes.guess_type(file_path)
        return Response(content, mimetype=mimetype or 'application/octet-stream')
        
    except Exception as e:
        print(f"Preview error for {path}: {e}")
        abort(404)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'JABchem CMS API is running'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"Starting Flask server on port {Config.FLASK_PORT}")
    print(f"Database: {Config.DATABASE_PATH}")
    print(f"Environment: {Config.FLASK_ENV}")
    
    app.run(
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=(Config.FLASK_ENV == 'development')
    )
