import git
import os
from config import Config

class GitHandler:
    def __init__(self, repo_path='..'):
        self.repo_path = repo_path
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize git repository"""
        try:
            self.repo = git.Repo(self.repo_path)
            
            # Configure git user
            with self.repo.config_writer() as config:
                config.set_value('user', 'name', Config.GIT_USER_NAME)
                config.set_value('user', 'email', Config.GIT_USER_EMAIL)
            
        except git.InvalidGitRepositoryError:
            print(f"Warning: {self.repo_path} is not a git repository")
            self.repo = None
    
    def add_all(self):
        """Stage all changes"""
        if not self.repo:
            raise Exception("Git repository not initialized")
        self.repo.git.add('.')
    
    def commit(self, message):
        """Commit staged changes"""
        if not self.repo:
            raise Exception("Git repository not initialized")
        
        # Check if there are changes to commit
        if not self.repo.is_dirty() and not self.repo.untracked_files:
            return None
        
        commit = self.repo.index.commit(message)
        return commit.hexsha
    
    def push(self, branch=None):
        """Push commits to remote"""
        if not self.repo:
            raise Exception("Git repository not initialized")
        
        if branch is None:
            branch = Config.GITHUB_BRANCH
        
        origin = self.repo.remote('origin')
        origin.push(branch)
    
    def get_status(self):
        """Get git status"""
        if not self.repo:
            return "Git repository not initialized"
        return self.repo.git.status()
    
    def has_changes(self):
        """Check if there are uncommitted changes"""
        if not self.repo:
            return False
        return self.repo.is_dirty() or len(self.repo.untracked_files) > 0
