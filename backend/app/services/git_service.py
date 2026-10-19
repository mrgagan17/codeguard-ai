import os
from typing import List, Tuple, Optional
import git
from app.core.logging import logger
from app.core.security import is_safe_path

class GitService:
    @staticmethod
    def get_changed_files(repo_path: str, base_ref: str = "HEAD~1") -> List[Tuple[str, str]]:
        """
        Extract changed files (relative_path, current_content) from a local git repository.
        Only reads repository files, never commits or modifies anything.
        """
        if not os.path.isdir(repo_path):
            raise ValueError(f"Path does not exist: {repo_path}")

        try:
            repo = git.Repo(repo_path)
            if repo.bare:
                raise ValueError("Bare git repositories are not supported.")

            changed_files: List[Tuple[str, str]] = []

            # 1. Check working tree unstaged & staged diffs
            diff_index = repo.head.commit.diff(None)  # uncommitted changes
            changed_paths = set()
            for diff in diff_index:
                if diff.b_path:
                    changed_paths.add(diff.b_path)
                elif diff.a_path:
                    changed_paths.add(diff.a_path)

            # Untracked files
            for untracked in repo.untracked_files:
                changed_paths.add(untracked)

            # If no uncommitted changes, check diff against base_ref if available
            if not changed_paths:
                try:
                    commit_diff = repo.commit(base_ref).diff("HEAD")
                    for diff in commit_diff:
                        if diff.b_path:
                            changed_paths.add(diff.b_path)
                except Exception:
                    # Fallback to all tracked Python files in repository
                    for item in repo.tree().traverse():
                        if item.type == 'blob' and item.path.endswith((".py", ".pyw")):
                            changed_paths.add(item.path)

            # Read content of changed Python files
            for rel_path in changed_paths:
                if not rel_path.endswith((".py", ".pyw")):
                    continue
                # Exclude virtual environments, git internals, node_modules
                parts = rel_path.replace("\\", "/").split("/")
                if any(p in parts for p in (".git", "venv", ".venv", "env", "node_modules", "__pycache__")):
                    continue

                full_path = os.path.join(repo_path, rel_path)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                        changed_files.append((rel_path.replace("\\", "/"), content))
                    except Exception as fe:
                        logger.warning(f"Could not read repository file {full_path}: {fe}")

            return changed_files
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Directory is not a valid Git repository: {repo_path}")
        except Exception as e:
            logger.error(f"Git analysis error: {e}")
            raise ValueError(f"Failed to analyze Git repository: {str(e)}")
