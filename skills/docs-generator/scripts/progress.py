#!/usr/bin/env python3
"""
Progress management for documentation generation.
Tracks session state to enable pause/resume functionality.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

PROGRESS_FILE = ".progress.json"


def get_progress_path(project_root: str) -> Path:
    """Get path to progress file in docs directory."""
    return Path(project_root) / "docs" / PROGRESS_FILE


def load_progress(project_root: str) -> Optional[Dict[str, Any]]:
    """Load existing progress file if it exists."""
    path = get_progress_path(project_root)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_progress(project_root: str, progress: dict) -> None:
    """Save progress to file."""
    path = get_progress_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    progress["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with open(path, "w") as f:
        json.dump(progress, f, indent=2)
    print(f"Progress saved to {path}")


def init_progress(language: str = "en") -> dict:
    """Create new progress structure."""
    return {
        "version": "1.0",
        "language": language,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "phase": "init",
        "analysis": {},
        "scope": {
            "approved_docs": [],
            "skipped": []
        },
        "docs": {}
    }


def cmd_check(args) -> None:
    """Check for existing progress and display summary."""
    progress = load_progress(args.project_root)

    if not progress:
        print("No existing progress found.")
        print(f"Run with 'init' to start new documentation session.")
        sys.exit(0)

    print("=== Documentation Progress ===")
    print(f"Language: {progress.get('language', 'en')}")
    print(f"Phase: {progress.get('phase', 'unknown')}")
    print(f"Started: {progress.get('started_at', 'unknown')}")
    print(f"Last updated: {progress.get('last_updated', 'unknown')}")

    # Analysis summary
    analysis = progress.get("analysis", {})
    if analysis:
        print(f"\nProject type: {'Monorepo' if analysis.get('is_monorepo') else 'Single package'}")
        if analysis.get("packages"):
            print(f"Packages: {', '.join(analysis['packages'])}")
        if analysis.get("frameworks"):
            print(f"Frameworks: {analysis['frameworks']}")

    # Doc status summary
    docs = progress.get("docs", {})
    if docs:
        completed = sum(1 for d in docs.values() if d.get("status") == "completed")
        in_progress = sum(1 for d in docs.values() if d.get("status") == "in_progress")
        pending = sum(1 for d in docs.values() if d.get("status") == "pending")

        print(f"\n=== Document Status ===")
        print(f"Completed: {completed}")
        print(f"In progress: {in_progress}")
        print(f"Pending: {pending}")

        if in_progress > 0:
            print(f"\nIn progress docs:")
            for doc, info in docs.items():
                if info.get("status") == "in_progress":
                    print(f"  - {doc}")

        if pending > 0:
            print(f"\nPending docs:")
            for doc, info in docs.items():
                if info.get("status") == "pending":
                    print(f"  - {doc}")

    # Output as JSON for machine parsing
    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(progress, indent=2))


def cmd_init(args) -> None:
    """Initialize new progress file."""
    path = get_progress_path(args.project_root)

    if path.exists() and not args.force:
        print(f"Progress file already exists at {path}")
        print("Use --force to overwrite")
        sys.exit(1)

    progress = init_progress(args.language)
    save_progress(args.project_root, progress)
    print(f"Initialized new progress file for {args.project_root}")


def cmd_save(args) -> None:
    """Save/update progress state."""
    progress = load_progress(args.project_root)

    if not progress:
        progress = init_progress(args.language if hasattr(args, 'language') else "en")

    # Update phase if provided
    if args.phase:
        progress["phase"] = args.phase

    # Update analysis if provided
    if args.analysis:
        progress["analysis"] = json.loads(args.analysis)

    # Update doc status if provided
    if args.doc:
        if "docs" not in progress:
            progress["docs"] = {}

        status = args.status or "pending"
        progress["docs"][args.doc] = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

    # Update scope if provided
    if args.scope:
        progress["scope"] = json.loads(args.scope)

    save_progress(args.project_root, progress)


def cmd_complete(args) -> None:
    """Mark a document as completed."""
    progress = load_progress(args.project_root)

    if not progress:
        print("No progress file found. Run 'init' first.")
        sys.exit(1)

    if "docs" not in progress:
        progress["docs"] = {}

    progress["docs"][args.doc] = {
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat() + "Z"
    }

    save_progress(args.project_root, progress)
    print(f"Marked '{args.doc}' as completed")


def cmd_clear(args) -> None:
    """Clear/remove progress file."""
    path = get_progress_path(args.project_root)

    if not path.exists():
        print("No progress file to clear.")
        sys.exit(0)

    if not args.force:
        print(f"This will delete {path}")
        print("Use --force to confirm")
        sys.exit(1)

    path.unlink()
    print(f"Progress file deleted: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage documentation generation progress"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check existing progress")
    check_parser.add_argument("project_root", help="Project root directory")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")
    check_parser.set_defaults(func=cmd_check)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize new progress")
    init_parser.add_argument("project_root", help="Project root directory")
    init_parser.add_argument("--language", default="en", help="Documentation language")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    init_parser.set_defaults(func=cmd_init)

    # Save command
    save_parser = subparsers.add_parser("save", help="Save progress state")
    save_parser.add_argument("project_root", help="Project root directory")
    save_parser.add_argument("--phase", help="Current phase (init/analysis/scope/generation/complete)")
    save_parser.add_argument("--doc", help="Document path to update")
    save_parser.add_argument("--status", help="Document status (pending/in_progress/completed)")
    save_parser.add_argument("--analysis", help="Analysis data as JSON string")
    save_parser.add_argument("--scope", help="Scope data as JSON string")
    save_parser.add_argument("--language", default="en", help="Documentation language")
    save_parser.set_defaults(func=cmd_save)

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark document as completed")
    complete_parser.add_argument("project_root", help="Project root directory")
    complete_parser.add_argument("--doc", required=True, help="Document path")
    complete_parser.set_defaults(func=cmd_complete)

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear progress file")
    clear_parser.add_argument("project_root", help="Project root directory")
    clear_parser.add_argument("--force", action="store_true", help="Confirm deletion")
    clear_parser.set_defaults(func=cmd_clear)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
