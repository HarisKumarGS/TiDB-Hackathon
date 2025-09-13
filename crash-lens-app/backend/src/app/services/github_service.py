import os
import tempfile
import re
import time
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse
import git
from github import Github, Auth, GithubException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models.model import Repository, CrashRCA


class GitHubService:
    """Service for GitHub operations using PyGithub and GitPython with PAT authentication"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.github_token = None
        self.github_client = None
        self._authenticated_user = None
        self._rate_limit_remaining = None
        
        # Initialize GitHub authentication
        self._initialize_github_client()

    def _initialize_github_client(self):
        """Initialize GitHub client with PAT authentication"""
        try:
            # Prioritize GITHUB_TOKEN environment variable
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                self.github_token = token.strip()
                print("✅ Found GitHub token in GITHUB_TOKEN environment variable")
            else:
                # Fallback to other common names for backward compatibility
                fallback_vars = ["GITHUB_PAT", "GITHUB_PERSONAL_ACCESS_TOKEN", "GH_TOKEN"]
                for env_var in fallback_vars:
                    token = os.environ.get(env_var)
                    if token:
                        self.github_token = token.strip()
                        print(f"✅ Found GitHub token in {env_var} environment variable")
                        break
            
            if not self.github_token:
                print("⚠️  No GitHub token found. Please set GITHUB_TOKEN environment variable.")
                print("💡 Create a PAT at: https://github.com/settings/tokens")
                return
            
            # Validate token format
            if not self._validate_token_format(self.github_token):
                return
            
            # Create PyGithub client with authentication
            auth = Auth.Token(self.github_token)
            self.github_client = Github(auth=auth)
            
            # Test authentication and get user info
            try:
                user = self.github_client.get_user()
                self._authenticated_user = user.login
                
                # Get rate limit info
                try:
                    rate_limit = self.github_client.get_rate_limit()
                    # Handle different PyGithub versions
                    if hasattr(rate_limit, 'core'):
                        self._rate_limit_remaining = rate_limit.core.remaining
                        rate_limit_info = f"{self._rate_limit_remaining}/{rate_limit.core.limit}"
                    else:
                        # Fallback for different API structure
                        self._rate_limit_remaining = getattr(rate_limit, 'remaining', 'unknown')
                        rate_limit_info = f"{self._rate_limit_remaining}/unknown"
                except Exception as e:
                    print(f"⚠️  Could not get rate limit info: {e}")
                    self._rate_limit_remaining = None
                    rate_limit_info = "unknown"
                
                print("✅ GitHub authentication successful")
                print(f"👤 Authenticated as: {self._authenticated_user}")
                print(f"📊 Rate limit remaining: {rate_limit_info}")
                
                # Check token scopes/permissions
                self._check_token_permissions()
                
            except GithubException as e:
                if e.status == 401:
                    print("❌ GitHub token is invalid or expired")
                elif e.status == 403:
                    print("❌ GitHub token doesn't have sufficient permissions")
                else:
                    print(f"❌ GitHub API error: {e}")
                self.github_client = None
            except Exception as e:
                print(f"❌ Error testing GitHub authentication: {e}")
                self.github_client = None
                
        except Exception as e:
            print(f"❌ Error initializing GitHub client: {e}")
            self.github_client = None

    def _validate_token_format(self, token: str) -> bool:
        """Validate GitHub PAT format"""
        if not token or len(token.strip()) < 20:
            print("❌ Invalid token: too short")
            return False
        
        # Classic PAT: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        if token.startswith('ghp_') and len(token) == 44:
            print("✅ Classic PAT format detected")
            return True
        
        # Fine-grained PAT: github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        elif token.startswith('github_pat_'):
            if len(token) < 70:  # Fine-grained PATs are typically 70+ characters
                print(f"❌ Fine-grained PAT appears truncated (length: {len(token)}, expected: 70+)")
                print("💡 Please check your GITHUB_TOKEN environment variable - it may be incomplete")
                return False
            print("✅ Fine-grained PAT format detected")
            return True
        
        # Legacy 40-character hex token (deprecated but may still work)
        elif len(token) == 40 and re.match(r'^[a-f0-9]{40}$', token):
            print("⚠️  Legacy token format detected (deprecated)")
            return True
        
        else:
            print("❌ Unrecognized token format")
            print(f"💡 Token length: {len(token)}, starts with: {token[:10]}...")
            print("💡 Token should start with 'ghp_' (classic) or 'github_pat_' (fine-grained)")
            return False

    def _check_token_permissions(self):
        """Check if token has required permissions for repository operations"""
        try:
            # Test basic repository access using PyGithub
            user = self.github_client.get_user()
            # Get repositories with pagination limit for efficiency
            repos_paginated = user.get_repos()
            repos = []
            count = 0
            for repo in repos_paginated:
                repos.append(repo)
                count += 1
                if count >= 10:  # Limit to 10 for efficiency
                    break
            print(f"✅ Token can access {len(repos)} repositories")
            
            # Test if we can access both public and private repos
            public_repos = [repo for repo in repos if not repo.private]
            private_repos = [repo for repo in repos if repo.private]
            
            if public_repos:
                print(f"✅ Can access {len(public_repos)} public repositories")
            if private_repos:
                print(f"✅ Can access {len(private_repos)} private repositories")
            
            # For classic tokens, try to get additional permission info
            if self.github_token.startswith('ghp_'):
                try:
                    # Test repository creation permission (indicates 'repo' scope)
                    try:
                        # This will fail if we don't have repo creation permissions
                        # but won't actually create a repo due to the test name
                        user.get_repo("__test_permissions_check__")
                    except GithubException as e:
                        if e.status == 404:
                            print("✅ Token has repository access permissions")
                        elif e.status == 403:
                            print("⚠️  Token may have limited repository permissions")
                    
                    # Check if we can access user's organizations (indicates broader permissions)
                    try:
                        orgs = list(user.get_orgs())
                        if orgs:
                            print(f"✅ Can access {len(orgs)} organizations")
                    except GithubException:
                        pass  # Organization access is optional
                        
                except Exception as e:
                    print(f"⚠️  Could not fully verify token permissions: {e}")
            
            # For fine-grained tokens, permissions are repository-specific
            elif self.github_token.startswith('github_pat_'):
                print("✅ Fine-grained token detected - permissions are repository-specific")
            
        except Exception as e:
            print(f"⚠️  Could not verify token permissions: {e}")

    def _get_authenticated_clone_url(self, repo_url: str) -> str:
        """Get clone URL with embedded PAT authentication"""
        if not self.github_token:
            return repo_url
        
        # Convert HTTPS URLs to include authentication
        if repo_url.startswith("https://github.com"):
            return repo_url.replace("https://github.com", f"https://{self.github_token}@github.com")
        
        # SSH URLs don't need token authentication (uses SSH keys)
        return repo_url

    def _setup_git_credentials(self, repo: git.Repo):
        """Configure git credentials for GitPython operations"""
        try:
            if self.github_token and self._authenticated_user:
                # Configure git credentials for HTTPS operations
                with repo.config_writer() as git_config:
                    git_config.set_value("user", "name", "Crash RCA Bot")
                    git_config.set_value("user", "email", "noreply@github.com")
                    
                # Set up credential helper for token authentication
                repo.git.config("credential.helper", "store")
                
        except Exception as e:
            print(f"⚠️  Could not setup git credentials: {e}")

    def _parse_github_url(self, repo_url: str) -> Optional[Tuple[str, str]]:
        """Parse GitHub repository URL to extract owner and repo name"""
        try:
            if repo_url.startswith("git@github.com:"):
                # SSH format: git@github.com:owner/repo.git
                path = repo_url.replace("git@github.com:", "").replace(".git", "")
                owner, repo_name = path.split("/", 1)
                return owner, repo_name
            elif "github.com" in repo_url:
                # HTTPS format: https://github.com/owner/repo
                parsed = urlparse(repo_url)
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    owner, repo_name = path_parts[0], path_parts[1].replace(".git", "")
                    return owner, repo_name
            return None
        except Exception as e:
            print(f"❌ Error parsing GitHub URL {repo_url}: {e}")
            return None

    def _get_repository_details(self, repository_id: str) -> Optional[Repository]:
        """Get repository details from the database"""
        try:
            query = text("""
                SELECT id, name, url, document_url, created_at, updated_at
                FROM repository
                WHERE id = :id
            """)
            
            result = self.db.execute(query, {"id": repository_id})
            row = result.fetchone()
            
            if not row:
                return None
                
            return Repository(
                id=row.id,
                name=row.name,
                url=row.url,
                document_url=row.document_url,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
        except Exception as e:
            print(f"❌ Error getting repository details: {e}")
            return None

    def _get_crash_rca_with_crash(self, crash_rca_id: str) -> Optional[Dict[str, Any]]:
        """Get crash RCA data along with associated crash and repository information"""
        try:
            query = text("""
                SELECT 
                    cr.id as rca_id,
                    cr.crash_id,
                    cr.description,
                    cr.problem_identification,
                    cr.data_collection,
                    cr.root_cause_identification,
                    cr.solution,
                    cr.author,
                    cr.supporting_documents,
                    cr.git_diff,
                    cr.created_at as rca_created_at,
                    cr.updated_at as rca_updated_at,
                    c.id as crash_id,
                    c.component,
                    c.error_type,
                    c.severity,
                    c.status,
                    c.impacted_users,
                    c.comment,
                    c.error_log,
                    c.repository_id,
                    c.created_at as crash_created_at,
                    c.updated_at as crash_updated_at,
                    r.id as repo_id,
                    r.name as repo_name,
                    r.url as repo_url,
                    r.document_url as repo_document_url
                FROM crash_rca cr
                JOIN crash c ON cr.crash_id = c.id
                JOIN repository r ON c.repository_id = r.id
                WHERE cr.id = :rca_id
            """)
            
            result = self.db.execute(query, {"rca_id": crash_rca_id})
            row = result.fetchone()
            
            if not row:
                return None
                
            return {
                "crash_rca": {
                    "id": row.rca_id,
                    "crash_id": row.crash_id,
                    "description": row.description,
                    "problem_identification": row.problem_identification,
                    "data_collection": row.data_collection,
                    "root_cause_identification": row.root_cause_identification,
                    "solution": row.solution,
                    "author": row.author,
                    "supporting_documents": row.supporting_documents,
                    "git_diff": row.git_diff,
                    "created_at": row.rca_created_at,
                    "updated_at": row.rca_updated_at,
                },
                "crash": {
                    "id": row.crash_id,
                    "component": row.component,
                    "error_type": row.error_type,
                    "severity": row.severity,
                    "status": row.status,
                    "impacted_users": row.impacted_users,
                    "comment": row.comment,
                    "error_log": row.error_log,
                    "repository_id": row.repository_id,
                    "created_at": row.crash_created_at,
                    "updated_at": row.crash_updated_at,
                },
                "repository": {
                    "id": row.repo_id,
                    "name": row.repo_name,
                    "url": row.repo_url,
                    "document_url": row.repo_document_url,
                }
            }
        except Exception as e:
            print(f"❌ Error getting crash RCA with crash data: {e}")
            return None

    def _get_default_branch(self, repo_url: str) -> str:
        """Get the default branch of the repository using PyGithub"""
        try:
            github_info = self._parse_github_url(repo_url)
            if github_info and self.github_client:
                owner, repo_name = github_info
                github_repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                return github_repo.default_branch
        except Exception as e:
            print(f"⚠️  Could not determine default branch: {e}")
        
        return "main"  # Fallback to main

    def _clone_repository(self, repo_url: str, temp_dir: str) -> Optional[git.Repo]:
        """Clone repository using GitPython with PAT authentication"""
        try:
            print(f"🔄 Cloning repository: {repo_url}")
            
            # Get authenticated clone URL
            auth_clone_url = self._get_authenticated_clone_url(repo_url)
            
            # Clone using GitPython
            repo = git.Repo.clone_from(auth_clone_url, temp_dir)
            
            # Setup git configuration
            self._setup_git_credentials(repo)
            
            print(f"✅ Successfully cloned repository to {temp_dir}")
            return repo
            
        except git.exc.GitCommandError as e:
            if "authentication failed" in str(e).lower() or "access denied" in str(e).lower():
                print("❌ Git authentication failed. Check your PAT permissions.")
            else:
                print(f"❌ Git command error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error cloning repository: {e}")
            return None

    def _validate_diff_content(self, diff_content: str) -> bool:
        """Validate that the diff content has basic diff structure (supports both git diff and plain diff)"""
        if not diff_content or not diff_content.strip():
            print("❌ Diff content is empty")
            return False
            
        lines = diff_content.strip().split('\n')
        
        # Check for any diff format indicators
        has_diff_indicators = False
        
        for line in lines:
            # Check for git diff format
            if line.startswith('diff --git'):
                has_diff_indicators = True
                break
            # Check for unified diff format
            elif line.startswith('--- ') and any(l.startswith('+++ ') for l in lines):
                has_diff_indicators = True
                break
            # Check for hunk headers (@@)
            elif line.startswith('@@') and '-' in line and '+' in line:
                has_diff_indicators = True
                break
            # Check for simple diff lines (+ or -)
            elif line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
                has_diff_indicators = True
                break
        
        if not has_diff_indicators:
            print("❌ No diff format indicators found (expected git diff, unified diff, or +/- lines)")
            return False
            
        print("✅ Diff content validation passed")
        return True

    def _preprocess_diff_content(self, diff_content: str) -> str:
        """Preprocess diff content to ensure proper format and convert plain diff to git diff if needed"""
        lines = diff_content.strip().split('\n')
        processed_lines = []
        
        # Check if this is already a git diff
        is_git_diff = any(line.startswith('diff --git') for line in lines)
        
        if is_git_diff:
            # Already git diff format, just clean up
            for line in lines:
                line = line.rstrip()
                if not processed_lines and not line:
                    continue
                processed_lines.append(line)
        else:
            # Convert plain diff to git diff format
            print("🔄 Converting plain diff to git diff format")
            
            # Try to detect file names from --- and +++ lines
            old_file = None
            new_file = None
            
            for line in lines:
                if line.startswith('--- '):
                    old_file = line[4:].strip()
                    if old_file.startswith('a/'):
                        old_file = old_file[2:]
                elif line.startswith('+++ '):
                    new_file = line[4:].strip()
                    if new_file.startswith('b/'):
                        new_file = new_file[2:]
                    break
            
            # If we couldn't detect file names, use generic names
            if not old_file or not new_file:
                old_file = new_file = "file.txt"
                print(f"⚠️  Could not detect file names, using generic: {old_file}")
            
            # Add git diff header
            processed_lines.append(f"diff --git a/{old_file} b/{new_file}")
            processed_lines.append("index 0000000..1111111 100644")
            
            # Process the rest of the lines
            for line in lines:
                line = line.rstrip()
                if not line and not processed_lines:
                    continue
                processed_lines.append(line)
        
        # Ensure the diff ends with a newline
        processed_content = '\n'.join(processed_lines)
        if not processed_content.endswith('\n'):
            processed_content += '\n'
            
        return processed_content

    def _apply_diff_to_repo(self, repo: git.Repo, diff_content: str) -> bool:
        """Apply diff content to the cloned repository using GitPython (supports both git diff and plain diff)"""
        try:
            # Validate diff content first
            if not self._validate_diff_content(diff_content):
                return False
            
            # Preprocess the diff content (converts plain diff to git diff if needed)
            processed_diff = self._preprocess_diff_content(diff_content)
            
            # Write diff to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False, encoding='utf-8') as f:
                f.write(processed_diff)
                patch_file = f.name
            
            try:
                print(f"📁 Applying patch file: {patch_file}")
                
                # Strategy 1: Try standard git apply
                try:
                    # First check if patch can be applied cleanly
                    repo.git.apply('--check', patch_file)
                    print("✅ Patch validation passed")
                    
                    # Apply the patch
                    repo.git.apply(patch_file)
                    print("✅ Diff applied successfully")
                    return True
                    
                except git.exc.GitCommandError as e:
                    print(f"⚠️  Standard apply failed: {e}")
                    
                    # Strategy 2: Try with --3way for better merge resolution
                    try:
                        repo.git.apply('--3way', patch_file)
                        print("✅ Diff applied successfully with 3-way merge")
                        return True
                    except git.exc.GitCommandError as e2:
                        print(f"⚠️  3-way apply failed: {e2}")
                        
                        # Strategy 3: Try with whitespace options
                        try:
                            repo.git.apply('--ignore-space-change', '--ignore-whitespace', patch_file)
                            print("✅ Diff applied successfully (ignoring whitespace)")
                            return True
                        except git.exc.GitCommandError as e3:
                            print(f"⚠️  Whitespace-tolerant apply failed: {e3}")
                            
                            # Strategy 4: Try applying without index information
                            try:
                                repo.git.apply('--reject', '--ignore-whitespace', patch_file)
                                print("✅ Diff applied with some rejections (check .rej files)")
                                return True
                            except git.exc.GitCommandError as e4:
                                print(f"❌ All git apply strategies failed: {e4}")
                                
                                # Strategy 5: Manual application for simple diffs
                                return self._apply_diff_manually(repo, diff_content)
                            
            finally:
                # Clean up patch file
                if os.path.exists(patch_file):
                    os.unlink(patch_file)
                
        except Exception as e:
            print(f"❌ Error in apply_diff_to_repo: {e}")
            return False

    def _apply_diff_manually(self, repo: git.Repo, diff_content: str) -> bool:
        """Manually apply simple diff content when git apply fails"""
        try:
            print("🔧 Attempting manual diff application...")
            
            lines = diff_content.strip().split('\n')
            current_file = None
            changes_applied = False
            
            # Parse the diff and apply changes
            for line in lines:
                # Detect file being modified
                if line.startswith('--- '):
                    old_file = line[4:].strip()
                    if old_file.startswith('a/'):
                        current_file = old_file[2:]
                    elif old_file != '/dev/null':
                        current_file = old_file
                elif line.startswith('+++ '):
                    new_file = line[4:].strip()
                    if new_file.startswith('b/'):
                        current_file = new_file[2:]
                    elif new_file != '/dev/null' and not current_file:
                        current_file = new_file
                
                # Apply simple line additions (this is a basic implementation)
                elif line.startswith('+') and not line.startswith('+++') and current_file:
                    try:
                        file_path = os.path.join(repo.working_dir, current_file)
                        
                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        # For simple additions, append to file (basic implementation)
                        content_to_add = line[1:]  # Remove the '+' prefix
                        
                        if os.path.exists(file_path):
                            with open(file_path, 'a', encoding='utf-8') as f:
                                f.write('\n' + content_to_add)
                        else:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content_to_add)
                        
                        changes_applied = True
                        print(f"✅ Applied addition to {current_file}")
                        
                    except Exception as e:
                        print(f"⚠️  Could not apply change to {current_file}: {e}")
            
            if changes_applied:
                print("✅ Manual diff application completed")
                return True
            else:
                print("❌ No changes could be applied manually")
                return False
                
        except Exception as e:
            print(f"❌ Error in manual diff application: {e}")
            return False

    def _generate_unique_branch_name(self, base_name: str, repo: git.Repo) -> str:
        """Generate a unique branch name to avoid conflicts"""
        try:
            # Get list of existing remote branches
            try:
                repo.git.fetch('origin')
                remote_branches = [ref.name.split('/')[-1] for ref in repo.remotes.origin.refs]
            except:
                remote_branches = []
            
            # Get local branches
            local_branches = [ref.name for ref in repo.heads]
            existing_branches = set(remote_branches + local_branches)
            
            # If base name is not taken, use it
            if base_name not in existing_branches:
                return base_name
            
            # Try with timestamp
            timestamp = int(time.time())
            candidate = f"{base_name}-{timestamp}"
            if candidate not in existing_branches:
                return candidate
            
            # Try with incremental numbers
            counter = 1
            while True:
                candidate = f"{base_name}-{counter}"
                if candidate not in existing_branches:
                    return candidate
                counter += 1
                
        except Exception:
            # Fallback to timestamp-based name
            return f"{base_name}-{int(time.time())}"

    def _create_branch_and_commit(self, repo: git.Repo, branch_name: str, commit_message: str) -> Tuple[bool, str]:
        """Create a new branch and commit changes"""
        try:
            # Generate unique branch name
            unique_branch_name = self._generate_unique_branch_name(branch_name, repo)
            
            # Create and checkout new branch
            current_branch = repo.active_branch
            new_branch = repo.create_head(unique_branch_name)
            new_branch.checkout()
            
            print(f"✅ Created and checked out branch: {unique_branch_name}")
            
            # Check if there are any changes to commit
            if not repo.is_dirty() and not repo.untracked_files:
                print("⚠️  No changes to commit")
                # Switch back to original branch
                current_branch.checkout()
                return False, unique_branch_name
            
            # Add all changes
            repo.git.add(A=True)  # -A flag adds all changes
            
            # Verify changes are staged
            try:
                # Check if there are staged changes
                staged_changes = repo.index.diff("HEAD")
                if not staged_changes:
                    print("⚠️  No changes were staged for commit")
                    current_branch.checkout()
                    return False, unique_branch_name
            except:
                # If HEAD doesn't exist (first commit), just proceed
                pass
            
            # Commit changes
            actor = git.Actor("Crash RCA Bot", "noreply@github.com")
            repo.index.commit(
                message=commit_message,
                author=actor,
                committer=actor
            )
            
            print(f"✅ Committed changes to branch '{unique_branch_name}'")
            return True, unique_branch_name
                
        except Exception as e:
            print(f"❌ Error creating branch and commit: {e}")
            return False, branch_name

    def _push_branch(self, repo: git.Repo, branch_name: str) -> bool:
        """Push branch to remote repository using GitPython"""
        try:
            # Get the remote origin
            origin = repo.remote('origin')
            
            # Push the branch with upstream tracking
            print(f"🚀 Pushing branch '{branch_name}' to remote...")
            push_info = origin.push(f"{branch_name}:{branch_name}")
            
            # Check push result
            if push_info:
                for info in push_info:
                    if info.flags & git.remote.PushInfo.ERROR:
                        print(f"❌ Push error: {info.summary}")
                        return False
                    elif info.flags & git.remote.PushInfo.REJECTED:
                        print(f"❌ Push rejected: {info.summary}")
                        return False
                    elif info.flags & git.remote.PushInfo.UP_TO_DATE:
                        print("✅ Branch is up to date")
                    else:
                        print(f"✅ Push successful: {info.summary}")
            
            print(f"✅ Successfully pushed branch '{branch_name}' to remote")
            return True
            
        except git.exc.GitCommandError as e:
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "403" in error_msg:
                print("❌ Git push authentication failed (403 Forbidden)")
                print("💡 This usually means:")
                print("   - GitHub token is invalid, expired, or truncated")
                print("   - Token doesn't have 'repo' or 'contents:write' permissions")
                print("   - For fine-grained PATs, check repository access permissions")
                print(f"   - Current token length: {len(self.github_token) if self.github_token else 0}")
            elif "404" in error_msg:
                print("❌ Repository not found or no access permissions")
            else:
                print(f"❌ Git push error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error pushing branch: {e}")
            return False

    def _format_commit_message(self, crash_rca: dict, crash: dict) -> str:
        """Format a proper commit message following conventional commits"""
        # Subject line (max 50 chars recommended)
        component = crash['component'].lower().replace(' ', '-').replace('_', '-')
        error_type = crash['error_type'].replace(' ', '-').lower()
        
        subject = f"fix({component}): resolve {error_type}"
        if len(subject) > 50:
            subject = f"fix: resolve {error_type}"
        
        # Body with details
        body_parts = []
        
        if crash_rca.get("description"):
            body_parts.append(f"Description: {crash_rca['description']}")
        
        if crash_rca.get("solution"):
            body_parts.append(f"Solution: {crash_rca['solution']}")
        
        # Add crash details
        body_parts.append(f"Severity: {crash['severity']}")
        body_parts.append(f"Impacted Users: {crash['impacted_users']}")
        
        if crash.get("comment"):
            body_parts.append(f"Notes: {crash['comment']}")
        
        # Add footer with references
        footer_parts = [
            f"Crash-ID: {crash['id']}",
            f"RCA-ID: {crash_rca['id']}"
        ]
        
        # Combine all parts
        commit_message = subject
        if body_parts:
            commit_message += "\n\n" + "\n".join(body_parts)
        if footer_parts:
            commit_message += "\n\n" + "\n".join(footer_parts)
        
        return commit_message

    def _format_pull_request_body(self, crash_rca: dict, crash: dict) -> str:
        """Format pull request body with proper markdown"""
        body = "## 🐛 Bug Fix\n\n"
        
        # Summary table
        body += "| Field | Value |\n"
        body += "|-------|-------|\n"
        body += f"| **Component** | `{crash['component']}` |\n"
        body += f"| **Error Type** | `{crash['error_type']}` |\n"
        body += f"| **Severity** | {crash['severity']} |\n"
        body += f"| **Impacted Users** | {crash['impacted_users']} |\n"
        body += f"| **Status** | {crash['status']} |\n\n"
        
        # Detailed sections
        if crash_rca.get("description"):
            body += f"## 📝 Description\n\n{crash_rca['description']}\n\n"
        
        if crash_rca.get("problem_identification"):
            body += f"## 🔍 Problem Identification\n\n{crash_rca['problem_identification']}\n\n"
        
        if crash_rca.get("root_cause_identification"):
            body += f"## 🎯 Root Cause Analysis\n\n{crash_rca['root_cause_identification']}\n\n"
        
        if crash_rca.get("data_collection"):
            body += f"## 📊 Data Collection\n\n{crash_rca['data_collection']}\n\n"
        
        if crash_rca.get("solution"):
            body += f"## 💡 Solution\n\n{crash_rca['solution']}\n\n"
        
        # Supporting documents
        if crash_rca.get("supporting_documents"):
            body += f"## 📎 Supporting Documents\n\n{crash_rca['supporting_documents']}\n\n"
        
        # Additional information
        if crash.get("comment"):
            body += f"## 💬 Additional Notes\n\n{crash['comment']}\n\n"
        
        # Footer with metadata
        body += "---\n\n"
        body += "**Metadata:**\n"
        body += f"- 🆔 **Crash ID:** `{crash['id']}`\n"
        body += f"- 🔍 **RCA ID:** `{crash_rca['id']}`\n"
        body += f"- 👤 **Author:** {crash_rca.get('author', 'System')}\n"
        body += f"- 📅 **Created:** {crash_rca.get('created_at', 'N/A')}\n"
        
        return body

    def create_pull_request_from_crash_rca(self, crash_rca_id: str) -> Dict[str, Any]:
        """Create a GitHub pull request based on crash RCA data"""
        if not self.github_client:
            return {
                "success": False,
                "error": "GitHub client not initialized. Please check your PAT configuration.",
                "pull_request_url": None
            }
        
        try:
            # Get crash RCA data with associated crash and repository
            rca_data = self._get_crash_rca_with_crash(crash_rca_id)
            if not rca_data:
                return {
                    "success": False,
                    "error": "Crash RCA not found",
                    "pull_request_url": None
                }
            
            crash_rca = rca_data["crash_rca"]
            crash = rca_data["crash"]
            repository = rca_data["repository"]
            
            # Parse GitHub repository URL
            github_info = self._parse_github_url(repository["url"])
            if not github_info:
                return {
                    "success": False,
                    "error": f"Invalid GitHub URL: {repository['url']}",
                    "pull_request_url": None
                }
            
            owner, repo_name = github_info
            
            # Get diff content from git_diff field
            diff_content = crash_rca.get("git_diff")
            if not diff_content:
                return {
                    "success": False,
                    "error": "No diff content found in git_diff field",
                    "pull_request_url": None
                }
            
            # Get default branch using PyGithub
            default_branch = self._get_default_branch(repository["url"])
            
            # Create temporary directory for repository operations
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository using GitPython
                repo = self._clone_repository(repository["url"], temp_dir)
                if not repo:
                    return {
                        "success": False,
                        "error": "Failed to clone repository",
                        "pull_request_url": None
                    }
                
                # Ensure we're on the default branch
                try:
                    repo.git.checkout(default_branch)
                except git.exc.GitCommandError as e:
                    print(f"⚠️  Could not checkout {default_branch}: {e}")
                
                # Generate branch name
                base_branch_name = f"fix-crash-{crash['component'].lower().replace(' ', '-').replace('_', '-')}-{crash_rca_id[:8]}"
                
                # Apply diff to repository
                if not self._apply_diff_to_repo(repo, diff_content):
                    return {
                        "success": False,
                        "error": "Failed to apply diff to repository",
                        "pull_request_url": None
                    }
                
                # Format commit message
                commit_message = self._format_commit_message(crash_rca, crash)
                
                # Create branch and commit
                success, actual_branch_name = self._create_branch_and_commit(repo, base_branch_name, commit_message)
                if not success:
                    return {
                        "success": False,
                        "error": "Failed to create branch and commit changes",
                        "pull_request_url": None
                    }
                
                # Push branch to remote
                if not self._push_branch(repo, actual_branch_name):
                    return {
                        "success": False,
                        "error": "Failed to push branch to remote repository",
                        "pull_request_url": None
                    }
            
            # Create pull request using PyGithub
            try:
                github_repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                
                # Format PR title and body
                component = crash['component']
                error_type = crash['error_type']
                pr_title = f"fix({component}): resolve {error_type}"
                
                # GitHub PR title has a limit of ~256 characters
                if len(pr_title) > 100:
                    pr_title = f"fix: resolve {error_type}"
                
                pr_body = self._format_pull_request_body(crash_rca, crash)
                
                # Create the pull request
                pull_request = github_repo.create_pull(
                    title=pr_title,
                    body=pr_body,
                    head=actual_branch_name,
                    base=default_branch,
                    draft=False
                )
                
                print(f"✅ Pull request created: {pull_request.html_url}")
                
                # Add labels if possible
                try:
                    available_labels = [label.name for label in github_repo.get_labels()]
                    labels_to_add = []
                    
                    # Add common labels if they exist
                    if "bug" in available_labels:
                        labels_to_add.append("bug")
                    if "fix" in available_labels:
                        labels_to_add.append("fix")
                    
                    # Add priority labels based on severity
                    severity = crash['severity'].lower()
                    if severity in ['high', 'critical']:
                        if "high-priority" in available_labels:
                            labels_to_add.append("high-priority")
                        elif "priority: high" in available_labels:
                            labels_to_add.append("priority: high")
                    
                    if labels_to_add:
                        pull_request.add_to_labels(*labels_to_add)
                        print(f"✅ Added labels: {', '.join(labels_to_add)}")
                        
                except Exception as e:
                    print(f"⚠️  Could not add labels: {e}")
                
                # Update rate limit info
                try:
                    rate_limit = self.github_client.get_rate_limit()
                    if hasattr(rate_limit, 'core'):
                        self._rate_limit_remaining = rate_limit.core.remaining
                    else:
                        self._rate_limit_remaining = getattr(rate_limit, 'remaining', None)
                except:
                    pass
                
                return {
                    "success": True,
                    "error": None,
                    "pull_request_url": pull_request.html_url,
                    "pull_request_number": pull_request.number,
                    "branch_name": actual_branch_name,
                    "repository": f"{owner}/{repo_name}",
                    "default_branch": default_branch,
                    "rate_limit_remaining": self._rate_limit_remaining
                }
                
            except GithubException as e:
                error_message = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
                
                # Handle specific GitHub API errors
                if e.status == 422:
                    if "pull request already exists" in error_message.lower():
                        return {
                            "success": False,
                            "error": f"Pull request already exists for branch '{actual_branch_name}'",
                            "pull_request_url": None
                        }
                elif e.status == 403:
                    return {
                        "success": False,
                        "error": "Insufficient permissions to create pull request. Check PAT scopes.",
                        "pull_request_url": None
                    }
                elif e.status == 404:
                    return {
                        "success": False,
                        "error": "Repository not found or no access permissions.",
                        "pull_request_url": None
                    }
                
                return {
                    "success": False,
                    "error": f"GitHub API error: {error_message}",
                    "pull_request_url": None
                }
        
        except Exception as e:
            print(f"❌ Error creating pull request: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "pull_request_url": None
            }

    def get_pull_request_status(self, owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Get status of a pull request using PyGithub"""
        if not self.github_client:
            return {
                "success": False,
                "error": "GitHub client not initialized"
            }
        
        try:
            github_repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            pr = github_repo.get_pull(pr_number)
            
            return {
                "success": True,
                "status": pr.state,
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "title": pr.title,
                "url": pr.html_url,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "author": pr.user.login,
                "comments_count": pr.comments,
                "commits_count": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "head_branch": pr.head.ref,
                "base_branch": pr.base.ref,
                "labels": [label.name for label in pr.labels],
                "milestone": pr.milestone.title if pr.milestone else None,
                "assignees": [assignee.login for assignee in pr.assignees],
                "reviewers": [reviewer.login for reviewer in pr.requested_reviewers]
            }
            
        except GithubException as e:
            error_message = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
            return {
                "success": False,
                "error": f"GitHub API error: {error_message}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def is_available(self) -> bool:
        """Check if GitHub service is available and configured"""
        return self.github_client is not None

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the GitHub service configuration"""
        if not self.github_client:
            return {
                "available": False,
                "error": "GitHub PAT not configured",
                "setup_instructions": {
                    "1": "Create a PAT at https://github.com/settings/tokens",
                    "2": "Set environment variable GITHUB_TOKEN with your PAT",
                    "3": "Ensure PAT has 'repo' scope for private repos or 'public_repo' for public repos"
                }
            }
        
        try:
            rate_limit = self.github_client.get_rate_limit()
            
            # Handle different PyGithub versions for rate limit
            if hasattr(rate_limit, 'core'):
                rate_limit_data = {
                    "remaining": rate_limit.core.remaining,
                    "limit": rate_limit.core.limit,
                    "reset": rate_limit.core.reset.isoformat(),
                    "used": rate_limit.core.used
                }
            else:
                # Fallback for different API structure
                rate_limit_data = {
                    "remaining": getattr(rate_limit, 'remaining', 'unknown'),
                    "limit": getattr(rate_limit, 'limit', 'unknown'),
                    "reset": getattr(rate_limit, 'reset', 'unknown'),
                    "used": getattr(rate_limit, 'used', 'unknown')
                }
            
            return {
                "available": True,
                "authenticated_user": self._authenticated_user,
                "rate_limit": rate_limit_data,
                "token_info": {
                    "format": "Classic PAT" if self.github_token.startswith('ghp_') else 
                             "Fine-grained PAT" if self.github_token.startswith('github_pat_') else 
                             "Legacy token",
                    "length": len(self.github_token)
                }
            }
        except Exception as e:
            return {
                "available": False,
                "error": f"Error getting service info: {str(e)}"
            }
