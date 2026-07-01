import argparse
from pathlib import Path
import shutil
import json
import uuid
from datetime import datetime
import pypdf
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
def extract_pdf_text(filepath, max_pages=1):
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page in reader.pages[:max_pages]:
            text += page.extract_text() or ""
        return text.lower()
    except Exception:
        return ""

PDF_KEYWORDS = {
    "Resumes": ["professional summary", "work experience", "curriculum vitae", "years of experience", "career objective"],
    "Invoices": ["invoice", "total due", "amount due", "bill to", "payment receipt", "subtotal", "receipt"],
    "Academic": ["assignment", "syllabus", "homework", "quiz", "lecture notes", "semester", "professor"],
}

def classify_pdf_content(filepath):
    text = extract_pdf_text(filepath)
    if not text:
        return None

    scores = {category: 0 for category in PDF_KEYWORDS}
    for category, keywords in PDF_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                scores[category] += 1

    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return None

    return best_category

def classify(filepath):
    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        content_category = classify_pdf_content(filepath)
        if content_category:
            return content_category

    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, target_folder):
        self.target_folder = target_folder

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        if filepath.name == ".DS_Store":
            return
        if filepath.suffix in (".crdownload", ".part", ".download"):
            return

        # Wait for the file to finish being written
        self.wait_until_stable(filepath)

        if not filepath.exists():
            return  # file disappeared (e.g. was a temp file that got renamed)

        self.organize_single_file(filepath)

    def wait_until_stable(self, filepath, checks=3, interval=1):
        last_size = -1
        stable_count = 0
        while stable_count < checks:
            if not filepath.exists():
                return
            current_size = filepath.stat().st_size
            if current_size == last_size:
                stable_count += 1
            else:
                stable_count = 0
            last_size = current_size
            time.sleep(interval)

    def organize_single_file(self, filepath):
        category = classify(filepath)
        dest_folder = self.target_folder / category
        dest_path = dest_folder / filepath.name

        counter = 1
        stem = filepath.stem
        suffix = filepath.suffix
        while dest_path.exists():
            dest_path = dest_folder / f"{stem}_{counter}{suffix}"
            counter += 1

        dest_folder.mkdir(exist_ok=True)
        shutil.move(str(filepath), str(dest_path))
        print(f"Auto-organized: {filepath.name} -> {dest_path}")


def main():
    parser = argparse.ArgumentParser(description="Smart file organizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize_parser = subparsers.add_parser("organize", help="Organize a folder")
    organize_parser.add_argument("folder", help="Path to folder to organize")
    organize_parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files")

    undo_parser = subparsers.add_parser("undo", help="Undo the last organize run")

    list_parser = subparsers.add_parser("list-sessions", help="List past organize sessions")
    watch_parser = subparsers.add_parser("watch", help="Watch a folder and auto-organize new files")
    watch_parser.add_argument("folder", help="Path to folder to watch")

    args = parser.parse_args()

    if args.command == "organize":
        target = Path(args.folder).expanduser()
        moves_log = []

        for item in target.iterdir():
            if item.is_file() and item.name != ".DS_Store":
                category = classify(item)
                dest_folder = target / category
                dest_path = dest_folder / item.name

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
                    moves_log.append({
                        "original_path": str(item),
                        "new_path": str(dest_path)
                    })

        if not args.dry_run and moves_log:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
            session_file = get_log_dir() / f"{session_id}.json"
            with open(session_file, "w") as f:
                json.dump({
                    "session_id": session_id,
                    "folder": str(target),
                    "timestamp": datetime.now().isoformat(),
                    "moves": moves_log
                }, f, indent=2)
            print(f"\nSession logged: {session_id}")
            print(f"Run 'python3 organizer.py undo' to reverse this.")
    elif args.command == "undo":
        session_files = sorted(get_log_dir().glob("*.json"))
        if not session_files:
            print("No sessions found to undo.")
            return

        latest_session = session_files[-1]
        with open(latest_session) as f:
            session_data = json.load(f)

        print(f"Undoing session: {session_data['session_id']}")
        for move in session_data["moves"]:
            original = Path(move["original_path"])
            new = Path(move["new_path"])
            if new.exists():
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(new), str(original))
                print(f"Restored: {new.name} -> {original}")
            else:
                print(f"Skipped (not found): {new}")

        latest_session.unlink()
        print(f"\nSession {session_data['session_id']} undone and removed.")
    elif args.command == "list-sessions":
        session_files = sorted(get_log_dir().glob("*.json"))
        if not session_files:
            print("No sessions found.")
            return

        for sf in session_files:
            with open(sf) as f:
                data = json.load(f)
            print(f"{data['session_id']}  |  {data['folder']}  |  {len(data['moves'])} files moved")
    elif args.command == "watch":
        target = Path(args.folder).expanduser()
        event_handler = DownloadHandler(target)
        observer = Observer()
        observer.schedule(event_handler, str(target), recursive=False)
        observer.start()
        print(f"Watching {target} for new files... (Ctrl+C to stop)")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nStopped watching.")
        observer.join()
if __name__ == "__main__":
    main()