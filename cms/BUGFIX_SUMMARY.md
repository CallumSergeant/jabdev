# Bug Fix Summary - Markdown File Generation

## Issue
Multiple papers with the same year in the same subject/level but different categories were overwriting each other because markdown files were named only by year (e.g., `2000.md`).

### Example
Biology Higher 2015 had 3 papers:
- Old Higher (sqapastpapersoldhigher)
- Revised Higher (sqapastpapersrevisedhigher)  
- New Higher (sqapastpapershigher)

Only the last one processed would be saved, losing the other two.

## Root Cause
In `cms/server/utils/file_handler.py`, the filename was generated as:
```python
filename = f"{paper_dict['year']}.md"
```

This caused collisions when multiple papers shared the same year.

## Solution
Changed filename generation to include the paper ID:
```python
filename = f"{paper_dict['year']}-{paper_dict['id']}.md"
```

This ensures each paper gets a unique filename.

## Results

### Before Fix
- 589 papers in database
- 444 markdown files generated (145 papers lost due to overwrites)
- Multiple papers with same year were missing

### After Fix
- 589 papers in database
- 589 markdown files generated (100% coverage)
- All papers now have unique files

### Example Files
Biology Higher 2015 now has 3 separate files:
- `2015-16.md` - Old Higher
- `2015-17.md` - Revised Higher
- `2015-19.md` - New Higher

## Validation
✅ All 589 papers have markdown files
✅ All 1,059 PDF links validated (100% success rate)
✅ No relative paths (../) in any files
✅ All PDFs accessible through preview
✅ Jekyll site builds successfully

## Files Modified
- `cms/server/utils/file_handler.py` - Fixed filename generation

## Testing
Run validation:
```bash
cms/venv/bin/python cms/scripts/validate_pdf_links.py --quiet
cms/venv/bin/python cms/scripts/audit_data.py
```

Both should show 100% success with no issues.
