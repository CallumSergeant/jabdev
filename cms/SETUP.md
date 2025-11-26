# JABchem CMS Setup Guide

## Prerequisites

### 1. Python Dependencies (Already Installed ✓)
The Python virtual environment is set up with all required packages:
- Flask 3.0.0
- Flask-CORS 4.0.0
- GitPython 3.1.40
- PyYAML 6.0.1
- python-dotenv 1.0.0
- Werkzeug 3.0.1

### 2. Jekyll/Ruby Dependencies (Required for Test Build)

To use the "Test Build" feature, you need to install Jekyll and Bundler:

#### Install Ruby Development Tools
```bash
# Install Ruby development headers and build tools
sudo apt update
sudo apt install ruby-dev build-essential zlib1g-dev

# Verify installation
ruby --version
gem --version
```

#### Install Bundler
```bash
# Install bundler for the user
gem install bundler -v 2.4.22 --user-install

# Add gem binaries to PATH (add to ~/.bashrc for permanent)
export PATH="$HOME/.gem/ruby/2.7.0/bin:$PATH"

# Verify
~/.gem/ruby/2.7.0/bin/bundle --version
```

#### Install Jekyll Dependencies
```bash
# From the project root directory (not cms/)
cd /home/callum/jabdev

# Configure bundle to install locally
~/.gem/ruby/2.7.0/bin/bundle config set --local path 'vendor/bundle'

# Install all gems
~/.gem/ruby/2.7.0/bin/bundle install
```

This will install:
- Jekyll
- GitHub Pages gem
- All required plugins

## Running the CMS

### Start the Flask Server
```bash
cd cms
./run.sh
```

Or manually:
```bash
cd cms
source venv/bin/activate
python server/app.py
```

The CMS will be available at: http://localhost:3001

## Using the Test Build Feature

Once Jekyll is installed:

1. Go to the Publish page in the CMS
2. Click "Test Build (Local)"
3. The system will:
   - Generate all markdown files
   - Run `~/.gem/ruby/2.7.0/bin/bundle exec jekyll build`
   - Show you the build output
   - NOT push anything to Git

**Note:** The CMS automatically uses the full path to bundle, so you don't need to add it to your PATH for the test build to work.

## Troubleshooting

### Jekyll Not Found
If you get "Jekyll not found" error:
```bash
cd /home/callum/jabdev
bundle install
```

### Bundle Not Found
```bash
sudo apt install ruby-bundler
```

### Permission Issues
If you get permission errors with gem:
```bash
# Add to ~/.bashrc
export GEM_HOME="$HOME/.gem"
export PATH="$HOME/.gem/bin:$PATH"

# Reload
source ~/.bashrc

# Then install
bundle install
```

## Optional: Preview Jekyll Site Locally

To preview the full Jekyll site:
```bash
cd /home/callum/jabdev
bundle exec jekyll serve
```

Then visit: http://localhost:4000
