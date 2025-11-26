#!/bin/bash
# Comprehensive test build script
# Validates all PDF links, regenerates markdown, and builds Jekyll site

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CMS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================================================"
echo "JABchem Test Build Script"
echo "========================================================================"
echo ""

# Step 1: Validate PDF links
echo "Step 1: Validating PDF links..."
echo "------------------------------------------------------------------------"
cd "$PROJECT_ROOT"
"$CMS_DIR/venv/bin/python" "$SCRIPT_DIR/validate_pdf_links.py" --auto-fix

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ PDF validation failed! Please fix the issues above."
    exit 1
fi

echo ""
echo "✓ All PDF links validated successfully"
echo ""

# Step 2: Regenerate markdown files
echo "Step 2: Regenerating markdown files..."
echo "------------------------------------------------------------------------"
RESPONSE=$(curl -s -X POST http://localhost:3001/api/publish/test)
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

if [ "$SUCCESS" != "True" ]; then
    echo "❌ Failed to regenerate markdown files"
    echo "$RESPONSE"
    exit 1
fi

PAPERS_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('papers_generated', 0))")
echo "✓ Generated $PAPERS_COUNT markdown files"
echo ""

# Step 3: Build Jekyll site
echo "Step 3: Building Jekyll site..."
echo "------------------------------------------------------------------------"
cd "$PROJECT_ROOT"
~/.gem/ruby/2.7.0/bin/bundle exec jekyll build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Jekyll build failed!"
    exit 1
fi

echo ""
echo "✓ Jekyll site built successfully"
echo ""

# Step 4: Final validation
echo "Step 4: Final validation..."
echo "------------------------------------------------------------------------"
"$CMS_DIR/venv/bin/python" "$SCRIPT_DIR/validate_pdf_links.py" --quiet

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Warning: Some validation issues remain"
fi

echo ""
echo "========================================================================"
echo "✓ TEST BUILD COMPLETE"
echo "========================================================================"
echo ""
echo "Preview available at: http://localhost:3001/preview/"
echo ""
