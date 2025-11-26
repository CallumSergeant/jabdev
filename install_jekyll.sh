#!/bin/bash
# Quick install script for Jekyll dependencies

echo "Installing Jekyll dependencies for JABchem CMS..."
echo "=================================================="

# Install ruby-dev if not present
if ! dpkg -l | grep -q ruby-dev; then
    echo "Installing ruby-dev..."
    sudo apt update
    sudo apt install -y ruby-dev build-essential zlib1g-dev
fi

# Install bundler
echo "Installing bundler..."
gem install bundler -v 2.4.22 --user-install

# Add to PATH
export PATH="$HOME/.gem/ruby/2.7.0/bin:$PATH"

# Configure bundle
echo "Configuring bundle..."
cd "$(dirname "$0")"
~/.gem/ruby/2.7.0/bin/bundle config set --local path 'vendor/bundle'

# Install gems
echo "Installing Jekyll and dependencies (this may take a few minutes)..."
~/.gem/ruby/2.7.0/bin/bundle install

echo ""
echo "=================================================="
echo "Installation complete!"
echo ""
echo "To use Jekyll commands, add this to your ~/.bashrc:"
echo "  export PATH=\"\$HOME/.gem/ruby/2.7.0/bin:\$PATH\""
echo ""
echo "The CMS Test Build feature will work automatically."
echo "=================================================="
