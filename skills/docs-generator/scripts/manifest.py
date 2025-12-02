#!/usr/bin/env python3
"""
Manifest management for tracking documented source files.
Enables incremental documentation updates by detecting changes.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

MANIFEST_FILE = ".docs-manifest.json"


def get_manifest_path(project_root: str) -> Path:
    """Get path to manifest file in docs directory."""
    return Path(project_root) / "docs" / MANIFEST_FILE


def load_manifest(project_root: str) -> Optional[Dict[str, Any]]:
    """Load existing manifest file if it exists."""
    path = get_manifest_path(project_root)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_manifest(project_root: str, manifest: dict) -> None:
    """Save manifest to file."""
    path = get_manifest_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest saved to {path}")


def init_manifest() -> dict:
    """Create new manifest structure."""
    return {
        "version": "1.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "source_files": {},
        "doc_files": {}
    }


def file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def file_mtime(filepath: Path) -> str:
    """Get file modification time as ISO string."""
    mtime = os.path.getmtime(filepath)
    return datetime.utcfromtimestamp(mtime).isoformat() + "Z"


def git_available(project_root: str) -> bool:
    """Check if git is available and project is a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def git_changed_files(project_root: str, since_hash: str = None) -> List[str]:
    """Get list of changed files using git."""
    try:
        if since_hash:
            result = subprocess.run(
                ["git", "diff", "--name-only", since_hash],
                cwd=project_root,
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            # Parse porcelain output
            files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # Format is "XY filename" where XY is status
                    files.append(line[3:])
            return files

        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def cmd_check(args) -> None:
    """Check for changes since last documentation generation."""
    manifest = load_manifest(args.project_root)

    if not manifest:
        print("No manifest found. Documentation has not been generated yet.")
        print(json.dumps({
            "status": "no_manifest",
            "message": "Run documentation generation first"
        }, indent=2))
        sys.exit(0)

    project_root = Path(args.project_root)
    source_files = manifest.get("source_files", {})

    changes = {
        "status": "changes_detected",
        "added": [],
        "modified": [],
        "removed": [],
        "unchanged": [],
        "doc_mapping": {}
    }

    # Check if git is available for smarter detection
    use_git = git_available(args.project_root) and not args.no_git

    if use_git:
        print("Using git for change detection...")
        git_changes = git_changed_files(args.project_root)

    # Check each tracked file
    for filepath, info in source_files.items():
        full_path = project_root / filepath

        if not full_path.exists():
            changes["removed"].append(filepath)
            if info.get("docs"):
                for doc in info["docs"]:
                    if doc not in changes["doc_mapping"]:
                        changes["doc_mapping"][doc] = []
                    changes["doc_mapping"][doc].append(filepath)
        else:
            current_hash = file_hash(full_path)
            if current_hash != info.get("hash"):
                changes["modified"].append(filepath)
                if info.get("docs"):
                    for doc in info["docs"]:
                        if doc not in changes["doc_mapping"]:
                            changes["doc_mapping"][doc] = []
                        changes["doc_mapping"][doc].append(filepath)
            else:
                changes["unchanged"].append(filepath)

    # Check for new files (if using git)
    if use_git:
        for changed_file in git_changes:
            if changed_file not in source_files and not changed_file.startswith("docs/"):
                changes["added"].append(changed_file)

    # Determine overall status
    if not changes["added"] and not changes["modified"] and not changes["removed"]:
        changes["status"] = "no_changes"

    print(json.dumps(changes, indent=2))

    # Summary
    print(f"\n=== Summary ===")
    print(f"Added: {len(changes['added'])}")
    print(f"Modified: {len(changes['modified'])}")
    print(f"Removed: {len(changes['removed'])}")
    print(f"Unchanged: {len(changes['unchanged'])}")

    if changes["doc_mapping"]:
        print(f"\nDocumentation affected:")
        for doc, sources in changes["doc_mapping"].items():
            print(f"  {doc}:")
            for src in sources:
                print(f"    - {src}")


def cmd_update(args) -> None:
    """Update manifest after documentation generation."""
    manifest = load_manifest(args.project_root)

    if not manifest:
        manifest = init_manifest()

    project_root = Path(args.project_root)

    # Parse files list
    if args.files:
        files = [f.strip() for f in args.files.split(",")]
    else:
        files = []

    # Parse docs list
    if args.docs:
        docs = [d.strip() for d in args.docs.split(",")]
    else:
        docs = []

    # Update source files
    for filepath in files:
        full_path = project_root / filepath
        if full_path.exists():
            manifest["source_files"][filepath] = {
                "hash": file_hash(full_path),
                "mtime": file_mtime(full_path),
                "docs": docs
            }
            print(f"Tracked: {filepath}")

    # Update doc files
    for doc in docs:
        doc_path = project_root / doc
        manifest["doc_files"][doc] = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "sources": files,
            "exists": doc_path.exists()
        }
        print(f"Documented: {doc}")

    save_manifest(args.project_root, manifest)


def cmd_init(args) -> None:
    """Initialize new manifest file."""
    path = get_manifest_path(args.project_root)

    if path.exists() and not args.force:
        print(f"Manifest file already exists at {path}")
        print("Use --force to overwrite")
        sys.exit(1)

    manifest = init_manifest()
    save_manifest(args.project_root, manifest)
    print(f"Initialized new manifest file")


def cmd_show(args) -> None:
    """Show current manifest contents."""
    manifest = load_manifest(args.project_root)

    if not manifest:
        print("No manifest found.")
        sys.exit(1)

    print(json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Manage documentation manifest for change tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check for changes")
    check_parser.add_argument("project_root", help="Project root directory")
    check_parser.add_argument("--no-git", action="store_true", help="Don't use git for detection")
    check_parser.set_defaults(func=cmd_check)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update manifest")
    update_parser.add_argument("project_root", help="Project root directory")
    update_parser.add_argument("--files", help="Comma-separated source files")
    update_parser.add_argument("--docs", help="Comma-separated doc files")
    update_parser.set_defaults(func=cmd_update)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize manifest")
    init_parser.add_argument("project_root", help="Project root directory")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    init_parser.set_defaults(func=cmd_init)

    # Show command
    show_parser = subparsers.add_parser("show", help="Show manifest contents")
    show_parser.add_argument("project_root", help="Project root directory")
    show_parser.set_defaults(func=cmd_show)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
