import argparse
from pathlib import Path
import shutil
import json
import uuid
from datetime import datetime

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".pages", ".rtf"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".numbers"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".dmg"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".ipynb"],
}

LOG_DIR = Path.home() / ".file_organizer" / "sessions"

def get_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR

def classify(filepath):
    ext = Path(filepath).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"
def main():
    parser = argparse.ArgumentParser(description="Smart file organizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize_parser = subparsers.add_parser("organize", help="Organize a folder")
    organize_parser.add_argument("folder", help="Path to folder to organize")
    organize_parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files")

    undo_parser = subparsers.add_parser("undo", help="Undo the last organize run")

    list_parser = subparsers.add_parser("list-sessions", help="List past organize sessions")

    args = parser.parse_args()

    if args.command == "organize":
        target = Path(args.folder).expanduser()
        for item in target.iterdir():
            if item.is_file() and item.name != ".DS_Store":
                category = classify(item)
                dest_folder = target / category
                dest_path = dest_folder / item.name

                # Handle name collisions
                counter = 1
                stem = item.stem
                suffix = item.suffix
                while dest_path.exists():
                    dest_path = dest_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

                if args.dry_run:
                    print(f"[DRY RUN] {item.name} -> {dest_path}")
                else:
                    dest_folder.mkdir(exist_ok=True)
                    shutil.move(str(item), str(dest_path))
                    print(f"Moved: {item.name} -> {dest_path}")
    elif args.command == "undo":
        print("Would undo last session")
    elif args.command == "list-sessions":
        print("Would list past sessions")

if __name__ == "__main__":
    main()