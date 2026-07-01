import argparse
from pathlib import Path

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".pages", ".rtf"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".numbers"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".dmg"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".ipynb"],
}

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
                print(f"{item.name} -> {category}/")
    elif args.command == "undo":
        print("Would undo last session")
    elif args.command == "list-sessions":
        print("Would list past sessions")

if __name__ == "__main__":
    main()