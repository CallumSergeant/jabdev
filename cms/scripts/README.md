# JABchem CMS Scripts

This directory contains utility scripts for managing the JABchem CMS.

## Validation & Testing

### validate_pdf_links.py

Comprehensive PDF link validation script that checks every PDF link in the database.

**Features:**
- Scans all 589 papers and validates 1000+ PDF links
- Automatically fixes broken links by finding similar files
- Identifies truly missing files
- Provides detailed reports

**Usage:**

```bash
# Interactive mode (prompts for fixes)
cms/venv/bin/python cms/scripts/validate_pdf_links.py

# Auto-fix mode (applies all fixes automatically)
cms/venv/bin/python cms/scripts/validate_pdf_links.py --auto-fix

# Quiet mode (minimal output)
cms/venv/bin/python cms/scripts/validate_pdf_links.py --quiet
```

**Output:**
- Console report with statistics
- `validation_report.json` - Detailed JSON report with all issues

### test_build.sh

Complete test build pipeline that validates, regenerates, and builds the site.

**Usage:**

```bash
./cms/scripts/test_build.sh
```

**Steps:**
1. Validates all PDF links
2. Regenerates markdown files from database
3. Builds Jekyll site
4. Final validation check

## Database Management

### migrate_existing_data.py

Migrates existing markdown files into the database.

**Usage:**

```bash
cd cms
python3 scripts/migrate_existing_data.py
```

### fix_database_paths.py

Updates database paths to match flattened file structure (removes subdirectories and spaces).

**Usage:**

```bash
cms/venv/bin/python cms/scripts/fix_database_paths.py
```

### backup_database.py

Creates a timestamped backup of the database.

**Usage:**

```bash
cd cms
python3 scripts/backup_database.py
```

### restore_backup.py

Restores database from a backup.

**Usage:**

```bash
cd cms
python3 scripts/restore_backup.py <backup_filename>
```

## File Management

### restructure_files.py

Major restructuring script that:
- Flattens folder structure (moves PDFs to level folders)
- Removes spaces from filenames
- Updates markdown files and database
- Creates backup before changes

**Usage:**

```bash
cd cms
python3 scripts/restructure_files.py
```

**Warning:** This makes significant changes. Always creates a backup first.

## Testing

### test_api.py

Tests CMS API endpoints.

**Usage:**

```bash
cd cms
python3 scripts/test_api.py
```

## Workflow

### Typical Development Workflow

1. **Make changes in CMS** (add/edit papers via web interface)

2. **Test locally:**
   ```bash
   ./cms/scripts/test_build.sh
   ```

3. **Preview site:**
   - Open http://localhost:3001/preview/

4. **Publish changes:**
   - Use CMS publish interface
   - Or manually: `curl -X POST http://localhost:3001/api/publish`

### After File Restructuring

If you've moved or renamed PDF files:

```bash
# 1. Fix database paths
cms/venv/bin/python cms/scripts/fix_database_paths.py

# 2. Validate and fix any issues
cms/venv/bin/python cms/scripts/validate_pdf_links.py --auto-fix

# 3. Regenerate and build
./cms/scripts/test_build.sh
```

### Troubleshooting Broken Links

```bash
# Check for broken links
cms/venv/bin/python cms/scripts/validate_pdf_links.py

# View detailed report
cat cms/scripts/validation_report.json | python3 -m json.tool

# Auto-fix what can be fixed
cms/venv/bin/python cms/scripts/validate_pdf_links.py --auto-fix
```

## Notes

- All scripts should be run from the project root directory
- The Flask server must be running for test builds (port 3001)
- Backups are stored in `backup_before_restructure/` directory
- Validation reports are saved to `cms/scripts/validation_report.json`
