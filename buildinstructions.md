# Prompt to Rebuild JABchem CMS in Python/Flask

## Context

I have a Node.js/Express CMS for managing exam papers on a Jekyll static site. I need you to rebuild this EXACTLY in Python using Flask, maintaining all functionality, file structure, and user experience.

## Current System Overview

### Tech Stack (Node.js)
- **Backend**: Node.js + Express + SQLite3
- **Frontend**: React 18 + React Router + TanStack Query + react-dropzone
- **Database**: SQLite with 5 tables
- **Git Integration**: simple-git for GitHub automation
- **File Upload**: express-fileupload

### Target Tech Stack (Python)
- **Backend**: Python 3.8+ + Flask + SQLAlchemy (or raw SQLite3)
- **Frontend**: Keep React (same as current)
- **Database**: SQLite (same schema)
- **Git Integration**: GitPython
- **File Upload**: Flask file upload handling

## System Architecture

### Database Schema (MUST BE IDENTICAL)

```sql
-- Subjects table
CREATE TABLE subjects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  icon TEXT,
  color TEXT,
  description TEXT
);

-- Levels table
CREATE TABLE levels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  subject_id INTEGER NOT NULL,
  description TEXT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id),
  UNIQUE(subject_id, slug)
);

-- Categories table
CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  level_id INTEGER NOT NULL,
  display_order INTEGER DEFAULT 0,
  table_config TEXT,
  FOREIGN KEY (level_id) REFERENCES levels(id)
);

-- Papers table
CREATE TABLE papers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year TEXT NOT NULL,
  category_id INTEGER NOT NULL,
  past_paper_path TEXT,
  jabchem_marking_path TEXT,
  sqa_marking_path TEXT,
  additional_files TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Publish history table
CREATE TABLE publish_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  commit_hash TEXT,
  message TEXT,
  published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT
);
```

### Initial Data Seeding (MUST BE IDENTICAL)

```python
subjects = [
    {'name': 'Chemistry', 'slug': 'chemistry', 'icon': 'flask', 'color': 'c3e8ff'},
    {'name': 'Maths', 'slug': 'maths', 'icon': 'calculator', 'color': 'edc672'},
    {'name': 'Physics', 'slug': 'physics', 'icon': 'atom', 'color': 'd7b5e8'},
    {'name': 'Biology', 'slug': 'biology', 'icon': 'dna', 'color': 'C2D8B2'}
]

levels = [
    {'name': 'National 5', 'slug': 'national5'},
    {'name': 'Higher', 'slug': 'higher'},
    {'name': 'Advanced Higher', 'slug': 'advancedhigher'},
    {'name': 'Archive', 'slug': 'archive'}
]
```

## Required API Endpoints

### 1. Subjects Routes (`/api/subjects`)
```
GET    /api/subjects           - List all subjects
GET    /api/subjects/:id       - Get subject with levels
```

### 2. Levels Routes (`/api/levels`)
```
GET    /api/levels/subject/:subjectId  - Get levels for subject
GET    /api/levels/:id                 - Get level with categories
```

### 3. Papers Routes (`/api/papers`)
```
GET    /api/papers/category/:categoryId  - List papers in category
GET    /api/papers/:id                   - Get single paper
POST   /api/papers                       - Create new paper
PUT    /api/papers/:id                   - Update paper
DELETE /api/papers/:id                   - Delete paper
DELETE /api/papers/:id/file/:fileType    - Delete specific file from paper
```

### 4. Upload Routes (`/api/upload`)
```
POST   /api/upload       - Upload single PDF file
POST   /api/upload/bulk  - Upload multiple PDFs
```

**Upload Logic**:
- Accept only PDF files (max 50MB)
- Normalize subject to lowercase
- Normalize level to lowercase, remove spaces
- Create directory: `/{subject}/{level}/`
- Generate filename: `{year}_{type}.pdf` where type is:
  - `past_paper`
  - `jabchem_marking`
  - `sqa_marking`
- Handle duplicate filenames (add _1, _2, etc.)
- Sanitize year (remove special characters)
- Return relative path: `/{subject}/{level}/{filename}`

### 5. Publish Routes (`/api/publish`)
```
POST   /api/publish         - Generate markdown and push to GitHub
GET    /api/publish/history - Get publish history
```

**Publish Logic**:
1. Query all papers from database with joins
2. Generate Jekyll markdown files with YAML frontmatter
3. Save to `_downloads/{subject}/{level}/{year}.md`
4. Git add, commit, push to GitHub
5. Log to publish_history table

**Markdown Format**:
```yaml
---
title: 2025
level: Higher
category: sqapastpapershigher
subject: Chemistry
Year: 2025
Past Paper:
  - url: /chemistry/higher/2025_past_paper.pdf
    link_text: 2025 Past Paper
JABchem Marking Scheme:
  - url: /chemistry/higher/2025_jabchem_marking.pdf
    link_text: JABchem Solutions
SQA Marking Scheme:
  - url: /chemistry/higher/2025_sqa_marking.pdf
    link_text: SQA Solutions
---
```

### 6. Structure Routes (`/api/structure`)
```
GET    /api/structure          - Get complete site structure
POST   /api/structure/category - Add new category
```

**Structure Response Format**:
```json
[
  {
    "id": 1,
    "name": "Chemistry",
    "slug": "chemistry",
    "color": "c3e8ff",
    "levels": [
      {
        "id": 7,
        "name": "Higher",
        "slug": "higher",
        "categories": [
          {
            "id": 15,
            "name": "SQA Past Papers - Higher",
            "slug": "sqapastpapershigher",
            "paper_count": 42
          }
        ]
      }
    ]
  }
]
```

## Flask Application Structure

```
cms/
├── server/
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration
│   ├── database.py               # Database initialization
│   ├── models.py                 # SQLAlchemy models (optional)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── subjects.py
│   │   ├── levels.py
│   │   ├── papers.py
│   │   ├── upload.py
│   │   ├── publish.py
│   │   └── structure.py
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py       # File upload utilities
│       └── git_handler.py        # Git operations
├── scripts/
│   ├── migrate_existing_data.py  # Import existing papers
│   └── backup_database.py        # Database backup
├── client/                        # Keep existing React app
│   └── (same as current)
├── requirements.txt
├── .env.example
└── README.md
```

## Key Requirements

### 1. Database Initialization
- Create database on first run
- Seed subjects and levels automatically
- Handle migrations gracefully

### 2. File Upload Handling
- Use Flask's request.files
- Validate PDF files only
- Create directories recursively
- Handle file moves/copies
- Return JSON responses

### 3. Git Integration
- Use GitPython library
- Configure git user from environment
- Handle git add, commit, push
- Catch and log errors
- Store commit hash in database

### 4. CORS Configuration
- Enable CORS for React frontend
- Allow localhost:3000 in development
- Configure for production

### 5. Error Handling
- Return proper HTTP status codes
- JSON error responses
- Log errors to console
- Graceful failure handling

### 6. Environment Variables
```
FLASK_ENV=development
FLASK_PORT=3001
DATABASE_PATH=server/db/jabchem.db
GITHUB_TOKEN=your_token
GITHUB_REPO=username/repo
GITHUB_BRANCH=main
```

## Migration Script Requirements

**File**: `scripts/migrate_existing_data.py`

Must:
1. Read all markdown files from `_downloads/` directory
2. Parse YAML frontmatter
3. Extract year, category, file paths
4. Skip files without year field
5. Skip "additional" folders
6. Create categories if they don't exist
7. Insert papers into database
8. Show progress and summary
9. Handle errors gracefully

## Frontend (Keep Existing React)

The React frontend should remain UNCHANGED. It communicates via REST API, so as long as Flask endpoints match the Express endpoints exactly, it will work.

## Testing Requirements

Create a simple test to verify:
1. Database initialization works
2. All API endpoints respond
3. File upload works
4. Git operations work (mock in tests)
5. Migration script runs successfully

## Documentation to Create

1. **README.md** - Flask-specific setup instructions
2. **QUICKSTART.md** - Getting started with Python/Flask
3. **requirements.txt** - All Python dependencies

## Dependencies (requirements.txt)

```
Flask==3.0.0
Flask-CORS==4.0.0
GitPython==3.1.40
PyYAML==6.0.1
python-dotenv==1.0.0
Werkzeug==3.0.1
```

## Critical Implementation Details

### File Upload Route
```python
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    subject = request.form.get('subject', '').lower()
    level = request.form.get('level', '').lower().replace(' ', '')
    year = request.form.get('year', '')
    file_type = request.form.get('type', '')
    
    # Validate PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
    
    # Create directory
    upload_dir = os.path.join('..', subject, level)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename
    sanitized_year = re.sub(r'[^a-zA-Z0-9]', '', year)
    filename = f"{sanitized_year}_{file_type}.pdf"
    
    # Handle duplicates
    filepath = os.path.join(upload_dir, filename)
    counter = 1
    while os.path.exists(filepath):
        base, ext = os.path.splitext(filename)
        filepath = os.path.join(upload_dir, f"{base}_{counter}{ext}")
        counter += 1
    
    # Save file
    file.save(filepath)
    
    # Return relative path
    relative_path = f"/{subject}/{level}/{os.path.basename(filepath)}"
    
    return jsonify({
        'success': True,
        'path': relative_path,
        'message': 'File uploaded successfully'
    })
```

### Publish Route
```python
@app.route('/api/publish', methods=['POST'])
def publish_changes():
    try:
        data = request.get_json()
        message = data.get('message', 'Update from CMS')
        
        # Generate markdown files
        generate_markdown_files()
        
        # Git operations
        repo = git.Repo('..')
        repo.git.add('.')
        
        status = repo.git.status()
        if 'nothing to commit' in status:
            return jsonify({'message': 'No changes to publish'})
        
        commit = repo.index.commit(message)
        origin = repo.remote('origin')
        origin.push()
        
        # Log to database
        cursor.execute(
            "INSERT INTO publish_history (commit_hash, message, status) VALUES (?, ?, ?)",
            (commit.hexsha, message, 'success')
        )
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Changes published successfully',
            'commit': commit.hexsha
        })
    except Exception as e:
        # Log error
        cursor.execute(
            "INSERT INTO publish_history (message, status) VALUES (?, ?)",
            (message, 'failed')
        )
        conn.commit()
        return jsonify({'error': str(e)}), 500
```

## Success Criteria

The Flask version is complete when:
1. ✅ All API endpoints return identical responses to Node.js version
2. ✅ React frontend works without any changes
3. ✅ File uploads work and files are stored correctly
4. ✅ Database schema matches exactly
5. ✅ Migration script imports existing data
6. ✅ Publish functionality generates correct markdown and pushes to GitHub
7. ✅ All documentation is updated for Python/Flask
8. ✅ Can run with `python server/app.py` or `flask run`

## Additional Notes

- Use Python 3.8+ features (f-strings, type hints optional)
- Follow PEP 8 style guide
- Use context managers for database connections
- Handle file paths cross-platform (use `os.path.join`)
- Log important operations to console
- Keep code simple and readable (like the Node.js version)

## What NOT to Change

- React frontend (keep as-is)
- Database schema (must be identical)
- API endpoint URLs (must match exactly)
- File storage structure (must match exactly)
- Markdown generation format (must match exactly)
- User experience (must be identical)

## Deliverables

1. Complete Flask backend in `cms/server/`
2. Migration script in `cms/scripts/`
3. requirements.txt with all dependencies
4. Updated README.md for Flask
5. .env.example with Flask-specific variables
6. All routes tested and working
7. Database initialization working
8. File upload working
9. Git integration working

---

**Start by creating the Flask app structure, then implement routes one by one, testing each against the React frontend to ensure compatibility.**
