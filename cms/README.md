# JABchem CMS - Flask Edition

A Python/Flask-based Content Management System for managing exam papers on a Jekyll static site.

## Tech Stack

- **Backend**: Python 3.8+ with Flask
- **Frontend**: React 18 with React Router and TanStack Query
- **Database**: SQLite3
- **Git Integration**: GitPython

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for React frontend)
- Git

### Installation

1. **Clone the repository**
   ```bash
   cd cms
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the Flask server**
   ```bash
   cd server
   python app.py
   ```

   The API will be available at `http://localhost:3001`

6. **Set up React frontend** (in a new terminal)
   ```bash
   cd client
   npm install
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## Project Structure

```
cms/
├── server/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration
│   ├── database.py         # Database initialization
│   ├── routes/             # API route handlers
│   │   ├── subjects.py
│   │   ├── levels.py
│   │   ├── papers.py
│   │   ├── upload.py
│   │   ├── publish.py
│   │   └── structure.py
│   └── utils/              # Utility modules
│       ├── file_handler.py
│       └── git_handler.py
├── scripts/
│   ├── migrate_existing_data.py  # Import existing papers
│   └── backup_database.py        # Database backup
├── client/                 # React frontend
└── requirements.txt        # Python dependencies
```

## API Endpoints

### Subjects
- `GET /api/subjects` - List all subjects
- `GET /api/subjects/:id` - Get subject with levels

### Levels
- `GET /api/levels/subject/:subjectId` - Get levels for subject
- `GET /api/levels/:id` - Get level with categories

### Papers
- `GET /api/papers/category/:categoryId` - List papers in category
- `GET /api/papers/:id` - Get single paper
- `POST /api/papers` - Create new paper
- `PUT /api/papers/:id` - Update paper
- `DELETE /api/papers/:id` - Delete paper
- `DELETE /api/papers/:id/file/:fileType` - Delete specific file

### Upload
- `POST /api/upload` - Upload single PDF file
- `POST /api/upload/bulk` - Upload multiple PDFs

### Publish
- `POST /api/publish` - Generate markdown and push to GitHub
- `GET /api/publish/history` - Get publish history

### Structure
- `GET /api/structure` - Get complete site structure
- `POST /api/structure/category` - Add new category

## Database

The application uses SQLite with the following tables:
- `subjects` - Subject definitions (Chemistry, Maths, Physics, Biology)
- `levels` - Level definitions (National 5, Higher, Advanced Higher, Archive)
- `categories` - Paper categories within levels
- `papers` - Individual exam papers with file paths
- `publish_history` - Git publish history

The database is automatically initialized with seed data on first run.

## Migration

To import existing markdown files from `_downloads/` directory:

```bash
cd scripts
python migrate_existing_data.py
```

This will:
- Parse all markdown files in `_downloads/`
- Extract paper information from YAML frontmatter
- Create categories as needed
- Import papers into the database

## Backup

To create a database backup:

```bash
cd scripts
python backup_database.py
```

Backups are stored in `server/db/backups/` with timestamps.

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
cd server
python app.py
```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:3001/api/health

# Get all subjects
curl http://localhost:3001/api/subjects

# Get site structure
curl http://localhost:3001/api/structure
```

## Publishing Workflow

1. Upload PDF files via the frontend
2. Create/update paper entries
3. Click "Publish" to:
   - Generate Jekyll markdown files
   - Commit changes to Git
   - Push to GitHub

## Environment Variables

Create a `.env` file with:

```
FLASK_ENV=development
FLASK_PORT=3001
DATABASE_PATH=server/db/jabchem.db
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo
GITHUB_BRANCH=main
GIT_USER_NAME=Your Name
GIT_USER_EMAIL=your.email@example.com
```

## Troubleshooting

### Database Issues
- Delete `server/db/jabchem.db` to reset the database
- Run the app again to reinitialize with seed data

### Git Issues
- Ensure you're in a Git repository
- Check that `GITHUB_TOKEN` has push permissions
- Verify `GIT_USER_NAME` and `GIT_USER_EMAIL` are set

### CORS Issues
- Ensure the React app is running on `http://localhost:3000`
- Check CORS configuration in `app.py`

## License

MIT
