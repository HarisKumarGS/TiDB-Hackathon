import os
import tempfile
import shutil
from typing import List, Dict, Optional
from pathlib import Path
import logging

import git
from github import Github
from unidiff import PatchSet, PatchedFile
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.sqlalchemy_models import CrashRCA, Repository, Crash

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Synchronous GitHub service for creating pull requests from crash RCA diffs.
    Uses unidiff for patch parsing, GitPython for local operations, and PyGithub for GitHub API.
    """
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.github_client = Github(self.github_token)
        self.temp_dir = None
    
    async def create_pull_request_from_rca(self, crash_rca_id: str, db: Session) -> Dict:
        """
        Main method to create a pull request from a crash RCA.
        
        Args:
            crash_rca_id: The ID of the crash RCA record
            db: Database session
            
        Returns:
            Dict containing PR details and status
        """
        try:
            # Fetch RCA data
            rca_data = self._get_rca_data(crash_rca_id, db)
            if not rca_data:
                raise ValueError(f"Crash RCA with ID {crash_rca_id} not found")
            
            # Validate git diff
            if not rca_data["git_diff"]:
                raise ValueError("No git diff found in RCA data")
            
            # Parse diff with unidiff
            patch_set = self._parse_diff_with_unidiff(rca_data["git_diff"])
            
            # Setup temporary workspace
            self.temp_dir = tempfile.mkdtemp(prefix="github_service_")
            
            try:
                # Clone repository and create feature branch
                repo_path = self._clone_repository(rca_data["repository_url"])
                branch_name = f"fix/crash-rca-{crash_rca_id}"
                
                # Create and checkout feature branch
                repo = git.Repo(repo_path)
                self._create_feature_branch(repo, branch_name)
                
                # Apply patches
                self._apply_patches_to_repo(repo_path, patch_set)
                
                # Commit changes
                commit_message = self._generate_commit_message(rca_data)
                repo.git.add(A=True)
                repo.git.commit(m=commit_message)
                
                # Push to remote
                origin = repo.remote("origin")
                origin.push(branch_name)
                
                # Create pull request
                pr_result = self._create_github_pr(
                    rca_data["repository_url"],
                    branch_name,
                    rca_data,
                    crash_rca_id
                )
                
                return {
                    "status": "success",
                    "pr_url": pr_result["html_url"],
                    "pr_number": pr_result["number"],
                    "branch_name": branch_name,
                    "commit_sha": str(repo.head.commit)
                }
                
            finally:
                # Cleanup temporary directory
                if self.temp_dir and os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                    
        except Exception as e:
            logger.error(f"Error creating PR for RCA {crash_rca_id}: {str(e)}")
            # Cleanup on error
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise
    
    def _get_rca_data(self, crash_rca_id: str, db: Session) -> Optional[Dict]:
        """Fetch RCA data with related crash and repository information."""
        rca = db.query(CrashRCA).filter(CrashRCA.id == crash_rca_id).first()
        if not rca:
            return None
        
        crash = db.query(Crash).filter(Crash.id == rca.crash_id).first()
        repository = db.query(Repository).filter(Repository.id == crash.repository_id).first()
        
        return {
            "rca_id": rca.id,
            "git_diff": rca.git_diff,
            "description": rca.description,
            "solution": rca.solution,
            "root_cause_identification": rca.root_cause_identification,
            "crash_component": crash.component,
            "crash_error_type": crash.error_type,
            "crash_severity": crash.severity,
            "repository_url": repository.url,
            "repository_name": repository.name
        }
    
    def _parse_diff_with_unidiff(self, git_diff: str) -> PatchSet:
        """
        Parse git diff using unidiff library.
        
        Args:
            git_diff: Raw git diff string
            
        Returns:
            PatchSet object containing parsed patches
        """
        try:
            patch_set = PatchSet.from_string(git_diff)
            if not patch_set:
                raise ValueError("Empty or invalid patch set")
            
            logger.info(f"Parsed {len(patch_set)} files from diff")
            return patch_set
            
        except Exception as e:
            logger.error(f"Error parsing diff: {str(e)}")
            raise ValueError(f"Invalid git diff format: {str(e)}")
    
    def _clone_repository(self, repo_url: str) -> str:
        """
        Clone repository to temporary directory.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            Path to cloned repository
        """
        repo_path = os.path.join(self.temp_dir, "repo")
        
        # Handle GitHub authentication for private repos
        if "github.com" in repo_url and not repo_url.startswith("https://"):
            # Convert SSH URL to HTTPS with token
            if repo_url.startswith("git@github.com:"):
                repo_name = repo_url.replace("git@github.com:", "").replace(".git", "")
                repo_url = f"https://{self.github_token}@github.com/{repo_name}.git"
        elif repo_url.startswith("https://github.com/"):
            # Add token to HTTPS URL
            repo_url = repo_url.replace("https://github.com/", f"https://{self.github_token}@github.com/")
        
        try:
            git.Repo.clone_from(repo_url, repo_path)
            logger.info(f"Successfully cloned repository to {repo_path}")
            return repo_path
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            raise
    
    def _create_feature_branch(self, repo: git.Repo, branch_name: str):
        """
        Create and checkout a new feature branch.
        
        Args:
            repo: GitPython repository object
            branch_name: Name of the branch to create
        """
        try:
            # Ensure we're on the main branch
            repo.git.checkout("main")
        except:
            try:
                repo.git.checkout("master")
            except:
                # Use current branch if neither main nor master exists
                pass
        
        # Create and checkout new branch
        repo.git.checkout("-b", branch_name)
        logger.info(f"Created and checked out branch: {branch_name}")
    
    def _apply_patches_to_repo(self, repo_path: str, patch_set: PatchSet):
        """
        Apply patches to the repository using unidiff.
        
        Args:
            repo_path: Path to the repository
            patch_set: PatchSet containing the patches to apply
        """
        for patched_file in patch_set:
            file_path = os.path.join(repo_path, patched_file.path)
            
            # Handle new files
            if patched_file.is_added_file:
                self._create_new_file(file_path, patched_file)
            
            # Handle deleted files
            elif patched_file.is_removed_file:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {patched_file.path}")
            
            # Handle modified files
            elif patched_file.is_modified_file:
                self._modify_existing_file(file_path, patched_file)
            
            logger.info(f"Applied patch for: {patched_file.path}")
    
    def _create_new_file(self, file_path: str, patched_file: PatchedFile):
        """Create a new file with content from patch."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Build file content from added lines
        content_lines = []
        for hunk in patched_file:
            for line in hunk:
                if line.is_added:
                    content_lines.append(line.value.rstrip('\n\r'))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        logger.info(f"Created new file: {patched_file.path}")
    
    def _modify_existing_file(self, file_path: str, patched_file: PatchedFile):
        """Modify an existing file using patch hunks."""
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist, creating new file")
            self._create_new_file(file_path, patched_file)
            return
        
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        # Apply hunks in reverse order to maintain line numbers
        for hunk in reversed(patched_file):
            original_lines = self._apply_hunk(original_lines, hunk)
        
        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(original_lines)
        
        logger.info(f"Modified file: {patched_file.path}")
    
    def _apply_hunk(self, lines: List[str], hunk) -> List[str]:
        """Apply a single hunk to file lines."""
        # Convert to 0-based indexing
        start_line = hunk.target_start - 1
        new_lines = []
        old_line_idx = start_line

        for line in hunk:
            if line.is_context:
                # Context lines must match existing lines
                if old_line_idx >= len(lines) or lines[old_line_idx].rstrip('\n') != line.value.rstrip('\n'):
                    raise ValueError(f"Context line mismatch at {old_line_idx + 1}: expected '{line.value.strip()}', got '{lines[old_line_idx].strip()}'")
                new_lines.append(lines[old_line_idx])
                old_line_idx += 1
            elif line.is_removed:
                # Skip the line in the original file (i.e., delete it)
                if old_line_idx >= len(lines) or lines[old_line_idx].rstrip('\n') != line.value.rstrip('\n'):
                    raise ValueError(f"Removed line mismatch at {old_line_idx + 1}: expected '{line.value.strip()}', got '{lines[old_line_idx].strip()}'")
                old_line_idx += 1
            elif line.is_added:
                # Add new line to the result
                new_lines.append(line.value)

        # Replace the relevant section in the original file
        end_line = old_line_idx
        return lines[:start_line] + new_lines + lines[end_line:]

    
    def _generate_commit_message(self, rca_data: Dict) -> str:
        """Generate a meaningful commit message from RCA data."""
        component = rca_data.get("crash_component", "Unknown")
        error_type = rca_data.get("crash_error_type", "Unknown")
        
        title = f"Fix {error_type} in {component}"
        
        body_parts = []
        if rca_data.get("description"):
            body_parts.append(f"Description: {rca_data['description']}")
        
        if rca_data.get("root_cause_identification"):
            body_parts.append(f"Root Cause: {rca_data['root_cause_identification']}")
        
        if rca_data.get("solution"):
            body_parts.append(f"Solution: {rca_data['solution']}")
        
        body_parts.append(f"RCA ID: {rca_data['rca_id']}")
        
        return f"{title}\n\n" + "\n\n".join(body_parts)
    
    def _create_github_pr(self, repo_url: str, branch_name: str, rca_data: Dict, crash_rca_id: str) -> Dict:
        """
        Create a pull request using PyGithub.
        
        Args:
            repo_url: Repository URL
            branch_name: Feature branch name
            rca_data: RCA data for PR content
            crash_rca_id: RCA ID for reference
            
        Returns:
            Dict containing PR information
        """
        # Extract repository name from URL
        repo_name = self._extract_repo_name(repo_url)
        
        try:
            repo = self.github_client.get_repo(repo_name)
            
            # Generate PR title and body
            pr_title = f"Fix: {rca_data.get('crash_error_type', 'Unknown Error')} in {rca_data.get('crash_component', 'Unknown Component')}"
            pr_body = self._generate_pr_body(rca_data, crash_rca_id)
            
            # Create pull request
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base="main"  # Try main first
            )
            
            logger.info(f"Created PR #{pr.number}: {pr.html_url}")
            
            return {
                "number": pr.number,
                "html_url": pr.html_url,
                "title": pr.title
            }
            
        except Exception as e:
            # Try with master branch if main fails
            if "main" in str(e):
                try:
                    pr = repo.create_pull(
                        title=pr_title,
                        body=pr_body,
                        head=branch_name,
                        base="master"
                    )
                    
                    return {
                        "number": pr.number,
                        "html_url": pr.html_url,
                        "title": pr.title
                    }
                except Exception as master_e:
                    logger.error(f"Failed to create PR with both main and master: {master_e}")
                    raise
            else:
                logger.error(f"Error creating PR: {str(e)}")
                raise
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        # Handle various URL formats
        if repo_url.startswith("git@github.com:"):
            return repo_url.replace("git@github.com:", "").replace(".git", "")
        elif "github.com/" in repo_url:
            parts = repo_url.split("github.com/")[1]
            return parts.replace(".git", "")
        else:
            raise ValueError(f"Unsupported repository URL format: {repo_url}")
    
    def _generate_pr_body(self, rca_data: Dict, crash_rca_id: str) -> str:
        """Generate PR body from RCA data."""
        body_parts = [
            "## 🐛 Bug Fix - Automated PR from Crash RCA",
            "",
            f"**RCA ID:** `{crash_rca_id}`",
            f"**Component:** {rca_data.get('crash_component', 'Unknown')}",
            f"**Error Type:** {rca_data.get('crash_error_type', 'Unknown')}",
            f"**Severity:** {rca_data.get('crash_severity', 'Unknown')}",
            ""
        ]
        
        if rca_data.get("description"):
            body_parts.extend([
                "## 📝 Description",
                rca_data["description"],
                ""
            ])
        
        if rca_data.get("root_cause_identification"):
            body_parts.extend([
                "## 🔍 Root Cause Analysis",
                rca_data["root_cause_identification"],
                ""
            ])
        
        if rca_data.get("solution"):
            body_parts.extend([
                "## 💡 Solution",
                rca_data["solution"],
                ""
            ])
        
        body_parts.extend([
            "## ⚠️ Important Notes",
            "- This PR was automatically generated from a crash RCA analysis",
            "- Please review the changes carefully before merging",
            "- Ensure all tests pass before deployment",
            "",
            "---",
            "*Generated by CrashLens RCA System*"
        ])
        
        return "\n".join(body_parts)


# Singleton instance
github_service = GitHubService()
