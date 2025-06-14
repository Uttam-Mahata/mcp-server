import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import aiofiles
import httpx
from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
import base64

logger = logging.getLogger(__name__)

class GitHubClient:
    """
    Advanced GitHub client with comprehensive API integration
    """
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url
        self.github = Github(token, base_url=base_url)
        self.session = httpx.AsyncClient()
        self._rate_limit_remaining = 5000
        self._rate_limit_reset = datetime.now()
    
    async def _check_rate_limit(self):
        """Check and handle rate limiting"""
        if self._rate_limit_remaining < 100:
            logger.warning("Approaching rate limit, slowing down requests")
            await asyncio.sleep(1)
    
    async def analyze_repository(
        self, 
        owner: str, 
        repo: str, 
        include_content: bool = True,
        max_files: int = 50
    ) -> Dict[str, Any]:
        """Comprehensive repository analysis"""
        
        await self._check_rate_limit()
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            
            # Basic repository information
            repo_info = {
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "language": repository.language,
                "languages": await self._get_languages(repository),
                "stars": repository.stargazers_count,
                "forks": repository.forks_count,
                "open_issues": repository.open_issues_count,
                "default_branch": repository.default_branch,
                "created_at": repository.created_at.isoformat(),
                "updated_at": repository.updated_at.isoformat(),
                "size": repository.size,
                "topics": repository.get_topics(),
                "license": repository.license.name if repository.license else None,
                "homepage": repository.homepage,
                "has_wiki": repository.has_wiki,
                "has_pages": repository.has_pages,
                "archived": repository.archived,
                "disabled": repository.disabled,
                "private": repository.private
            }
            
            # Repository structure
            structure = await self._get_repository_structure(repository, max_depth=3)
            
            # Recent activity
            recent_commits = await self._get_recent_commits(repository, limit=10)
            recent_issues = await self._get_recent_issues(repository, limit=10)
            recent_prs = await self._get_recent_pull_requests(repository, limit=10)
            
            # Code analysis
            code_files = []
            if include_content:
                code_files = await self._get_important_files(repository, max_files)
            
            # Contributors
            contributors = await self._get_top_contributors(repository, limit=10)
            
            # README and documentation
            readme_content = await self._get_readme_content(repository)
            
            # Release information
            releases = await self._get_recent_releases(repository, limit=5)
            
            return {
                "repository_info": repo_info,
                "structure": structure,
                "recent_activity": {
                    "commits": recent_commits,
                    "issues": recent_issues,
                    "pull_requests": recent_prs
                },
                "code_files": code_files,
                "contributors": contributors,
                "readme": readme_content,
                "releases": releases,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            raise
    
    async def _get_languages(self, repository: Repository) -> Dict[str, int]:
        """Get repository languages"""
        try:
            return repository.get_languages()
        except Exception as e:
            logger.warning(f"Failed to get languages: {e}")
            return {}
    
    async def _get_repository_structure(self, repository: Repository, max_depth: int = 3) -> Dict[str, Any]:
        """Get repository file structure"""
        try:
            contents = repository.get_contents("", ref=repository.default_branch)
            return await self._build_tree_structure(repository, contents, max_depth, 0)
        except Exception as e:
            logger.warning(f"Failed to get repository structure: {e}")
            return {}
    
    async def _build_tree_structure(
        self, 
        repository: Repository, 
        contents: List, 
        max_depth: int, 
        current_depth: int
    ) -> Dict[str, Any]:
        """Recursively build tree structure"""
        structure = {"files": [], "directories": {}}
        
        if current_depth >= max_depth:
            return structure
        
        for content in contents:
            if content.type == "file":
                structure["files"].append({
                    "name": content.name,
                    "path": content.path,
                    "size": content.size,
                    "type": content.type
                })
            elif content.type == "dir":
                try:
                    subcontents = repository.get_contents(content.path, ref=repository.default_branch)
                    structure["directories"][content.name] = await self._build_tree_structure(
                        repository, subcontents, max_depth, current_depth + 1
                    )
                except Exception as e:
                    logger.warning(f"Failed to get directory contents for {content.path}: {e}")
                    structure["directories"][content.name] = {"files": [], "directories": {}}
        
        return structure
    
    async def _get_recent_commits(self, repository: Repository, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits"""
        try:
            commits = repository.get_commits()[:limit]
            return [
                {
                    "sha": commit.sha,
                    "message": commit.commit.message.split('\n')[0],  # First line only
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "url": commit.html_url
                }
                for commit in commits
            ]
        except Exception as e:
            logger.warning(f"Failed to get recent commits: {e}")
            return []
    
    async def _get_recent_issues(self, repository: Repository, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent issues"""
        try:
            issues = repository.get_issues(state="all", sort="updated")[:limit]
            return [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "url": issue.html_url
                }
                for issue in issues if not issue.pull_request  # Exclude PRs
            ]
        except Exception as e:
            logger.warning(f"Failed to get recent issues: {e}")
            return []
    
    async def _get_recent_pull_requests(self, repository: Repository, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pull requests"""
        try:
            prs = repository.get_pulls(state="all", sort="updated")[:limit]
            return [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "author": pr.user.login,
                    "url": pr.html_url,
                    "mergeable": pr.mergeable,
                    "merged": pr.merged
                }
                for pr in prs
            ]
        except Exception as e:
            logger.warning(f"Failed to get recent pull requests: {e}")
            return []
    
    async def _get_important_files(self, repository: Repository, max_files: int = 50) -> List[Dict[str, Any]]:
        """Get important code files with content"""
        important_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', 
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.mm'
        }
        
        important_files = [
            'README.md', 'README.rst', 'README.txt', 'package.json', 'requirements.txt',
            'Cargo.toml', 'pom.xml', 'build.gradle', 'Dockerfile', 'docker-compose.yml',
            'setup.py', 'setup.cfg', 'pyproject.toml', 'main.py', 'index.js', 'app.py'
        ]
        
        files = []
        file_count = 0
        
        try:
            # Get all files recursively
            contents = repository.get_git_tree(repository.default_branch, recursive=True)
            
            for item in contents.tree:
                if file_count >= max_files:
                    break
                
                if item.type == "blob":
                    # Check if it's an important file
                    is_important = (
                        item.path in important_files or
                        any(item.path.endswith(ext) for ext in important_extensions) or
                        'test' in item.path.lower() or
                        'spec' in item.path.lower()
                    )
                    
                    if is_important:
                        try:
                            file_content = await self._get_file_content_safe(repository, item.path)
                            if file_content:
                                files.append({
                                    "path": item.path,
                                    "content": file_content,
                                    "size": item.size if hasattr(item, 'size') else len(file_content),
                                    "type": "code" if any(item.path.endswith(ext) for ext in important_extensions) else "config"
                                })
                                file_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to get content for {item.path}: {e}")
                            continue
            
            return files
            
        except Exception as e:
            logger.warning(f"Failed to get important files: {e}")
            return []
    
    async def _get_file_content_safe(self, repository: Repository, path: str, max_size: int = 100000) -> Optional[str]:
        """Safely get file content with size limits"""
        try:
            file = repository.get_contents(path, ref=repository.default_branch)
            
            # Skip large files
            if file.size > max_size:
                return f"[File too large: {file.size} bytes]"
            
            # Decode content
            if file.encoding == "base64":
                content = base64.b64decode(file.content).decode('utf-8', errors='ignore')
            else:
                content = file.content
            
            return content
            
        except UnicodeDecodeError:
            return "[Binary file]"
        except Exception as e:
            logger.warning(f"Failed to get file content for {path}: {e}")
            return None
    
    async def _get_top_contributors(self, repository: Repository, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top contributors"""
        try:
            contributors = repository.get_contributors()[:limit]
            return [
                {
                    "login": contributor.login,
                    "contributions": contributor.contributions,
                    "avatar_url": contributor.avatar_url,
                    "html_url": contributor.html_url
                }
                for contributor in contributors
            ]
        except Exception as e:
            logger.warning(f"Failed to get contributors: {e}")
            return []
    
    async def _get_readme_content(self, repository: Repository) -> Optional[str]:
        """Get README content"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        
        for readme_file in readme_files:
            try:
                content = repository.get_contents(readme_file, ref=repository.default_branch)
                if content.encoding == "base64":
                    return base64.b64decode(content.content).decode('utf-8', errors='ignore')
                else:
                    return content.content
            except:
                continue
        
        return None
    
    async def _get_recent_releases(self, repository: Repository, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent releases"""
        try:
            releases = repository.get_releases()[:limit]
            return [
                {
                    "tag_name": release.tag_name,
                    "name": release.title,
                    "body": release.body,
                    "published_at": release.published_at.isoformat() if release.published_at else None,
                    "prerelease": release.prerelease,
                    "draft": release.draft,
                    "url": release.html_url
                }
                for release in releases
            ]
        except Exception as e:
            logger.warning(f"Failed to get releases: {e}")
            return []
    
    async def search_code(
        self, 
        query: str, 
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        limit: int = 30
    ) -> Dict[str, Any]:
        """Advanced code search"""
        
        # Build search query
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        if language:
            search_query += f" language:{language}"
        
        if filename:
            search_query += f" filename:{filename}"
        
        try:
            results = self.github.search_code(search_query)
            
            code_results = []
            for i, item in enumerate(results):
                if i >= limit:
                    break
                
                # Get file content
                try:
                    content = await self._get_file_content_safe(item.repository, item.path)
                    code_results.append({
                        "repository": item.repository.full_name,
                        "path": item.path,
                        "name": item.name,
                        "html_url": item.html_url,
                        "content": content,
                        "score": item.score
                    })
                except Exception as e:
                    logger.warning(f"Failed to get content for search result {item.path}: {e}")
            
            return {
                "query": search_query,
                "total_count": results.totalCount,
                "results": code_results
            }
            
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            raise
    
    async def get_issues(
        self, 
        owner: str, 
        repo: str, 
        state: str = "open",
        labels: List[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get repository issues"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issues = repository.get_issues(state=state, labels=labels or [])
            
            result = []
            for i, issue in enumerate(issues):
                if i >= limit:
                    break
                
                if not issue.pull_request:  # Exclude pull requests
                    result.append({
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body,
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                        "labels": [label.name for label in issue.labels],
                        "assignees": [assignee.login for assignee in issue.assignees],
                        "user": issue.user.login,
                        "comments": issue.comments,
                        "url": issue.html_url
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get issues: {e}")
            raise
    
    async def create_issue(
        self, 
        owner: str, 
        repo: str, 
        title: str,
        body: str = "",
        labels: List[str] = None,
        assignees: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new issue"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "url": issue.html_url
            }
            
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise
    
    async def get_pull_requests(
        self, 
        owner: str, 
        repo: str, 
        state: str = "open",
        base: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get repository pull requests"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            prs = repository.get_pulls(state=state, base=base)
            
            result = []
            for i, pr in enumerate(prs):
                if i >= limit:
                    break
                
                result.append({
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "head": {
                        "ref": pr.head.ref,
                        "sha": pr.head.sha
                    },
                    "base": {
                        "ref": pr.base.ref,
                        "sha": pr.base.sha
                    },
                    "user": pr.user.login,
                    "mergeable": pr.mergeable,
                    "merged": pr.merged,
                    "comments": pr.comments,
                    "review_comments": pr.review_comments,
                    "commits": pr.commits,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files,
                    "url": pr.html_url
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get pull requests: {e}")
            raise
    
    async def create_pull_request(
        self, 
        owner: str, 
        repo: str, 
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a new pull request"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            return {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "head": {
                    "ref": pr.head.ref,
                    "sha": pr.head.sha
                },
                "base": {
                    "ref": pr.base.ref,
                    "sha": pr.base.sha
                },
                "user": pr.user.login,
                "url": pr.html_url
            }
            
        except Exception as e:
            logger.error(f"Failed to create pull request: {e}")
            raise
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        path: str,
        ref: str = "main"
    ) -> str:
        """Get file content"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            file = repository.get_contents(path, ref=ref)
            
            if file.encoding == "base64":
                return base64.b64decode(file.content).decode('utf-8', errors='ignore')
            else:
                return file.content
                
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            raise
    
    async def update_file(
        self, 
        owner: str, 
        repo: str, 
        path: str,
        content: str,
        message: str,
        sha: Optional[str] = None,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Update file content"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            
            # Get current file SHA if not provided
            if not sha:
                try:
                    file = repository.get_contents(path, ref=branch)
                    sha = file.sha
                except:
                    # File doesn't exist, create new
                    sha = None
            
            if sha:
                # Update existing file
                result = repository.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=sha,
                    branch=branch
                )
            else:
                # Create new file
                result = repository.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=branch
                )
            
            return {
                "path": path,
                "sha": result['content'].sha,
                "commit": {
                    "sha": result['commit'].sha,
                    "message": result['commit'].message,
                    "url": result['commit'].html_url
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
            raise
    
    async def get_pull_request_details(
        self, 
        owner: str, 
        repo: str, 
        pr_number: int
    ) -> Dict[str, Any]:
        """Get detailed pull request information including diff"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            
            # Get files changed
            files = pr.get_files()
            
            # Get diff
            diff_content = []
            for file in files:
                diff_content.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch if hasattr(file, 'patch') else None
                })
            
            # Get reviews
            reviews = pr.get_reviews()
            review_data = [
                {
                    "id": review.id,
                    "user": review.user.login,
                    "state": review.state,
                    "body": review.body,
                    "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None
                }
                for review in reviews
            ]
            
            return {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "head": {
                    "ref": pr.head.ref,
                    "sha": pr.head.sha
                },
                "base": {
                    "ref": pr.base.ref,
                    "sha": pr.base.sha
                },
                "user": pr.user.login,
                "mergeable": pr.mergeable,
                "merged": pr.merged,
                "files": diff_content,
                "reviews": review_data,
                "url": pr.html_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get pull request details: {e}")
            raise
    
    async def get_repository_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get comprehensive repository metrics"""
        
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            
            # Basic metrics
            metrics = {
                "stars": repository.stargazers_count,
                "forks": repository.forks_count,
                "watchers": repository.watchers_count,
                "open_issues": repository.open_issues_count,
                "size": repository.size,
                "created_at": repository.created_at.isoformat(),
                "updated_at": repository.updated_at.isoformat(),
                "pushed_at": repository.pushed_at.isoformat() if repository.pushed_at else None
            }
            
            # Language statistics
            metrics["languages"] = repository.get_languages()
            
            # Contributors count
            try:
                contributors = list(repository.get_contributors())
                metrics["contributor_count"] = len(contributors)
            except:
                metrics["contributor_count"] = 0
            
            # Commit activity (last year)
            try:
                commit_activity = repository.get_stats_commit_activity()
                if commit_activity:
                    metrics["commit_activity"] = [
                        {
                            "week": week.week.isoformat(),
                            "total": week.total,
                            "days": week.days
                        }
                        for week in commit_activity
                    ]
                else:
                    metrics["commit_activity"] = []
            except:
                metrics["commit_activity"] = []
            
            # Release count
            try:
                releases = list(repository.get_releases())
                metrics["release_count"] = len(releases)
                if releases:
                    metrics["latest_release"] = {
                        "tag_name": releases[0].tag_name,
                        "published_at": releases[0].published_at.isoformat() if releases[0].published_at else None
                    }
            except:
                metrics["release_count"] = 0
                metrics["latest_release"] = None
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get repository metrics: {e}")
            raise
