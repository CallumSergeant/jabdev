from flask import Flask, jsonify, render_template, redirect, url_for
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
