# Smart File Organizer

A command-line tool that organizes messy folders (like Downloads) into
categorized subfolders — with content-aware classification for PDFs,
not just file extensions.

## Why

Most file organizers just sort by extension. This one goes a step further:
it peeks inside PDF files and classifies them as Resumes, Invoices, or
Academic documents based on their actual content, not just the ".pdf" extension.

Every real run is logged, so any organize session can be fully undone.

## Features

- Sorts files into categories: Images, Documents, Videos, Audio, Archives,
  Code, Spreadsheets, and more
- Smart PDF classification: reads PDF content to detect Resumes, Invoices,
  and Academic documents
- `--dry-run` mode to preview changes before touching any files
- Full undo support via session logs
- Handles filename collisions automatically
- Session history with `list-sessions`
- Real-time folder watching: automatically organizes new files as they arrive
## Installation

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/smart-organizer.git
cd smart-organizer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Usage

Preview what would happen, without moving anything:
\`\`\`bash
python3 organizer.py organize ~/Downloads --dry-run
\`\`\`

Actually organize a folder:
\`\`\`bash
python3 organizer.py organize ~/Downloads
\`\`\`

Undo the most recent organize session:
\`\`\`bash
python3 organizer.py undo
\`\`\`

List past organize sessions:
\`\`\`bash
python3 organizer.py list-sessions
\`\`\`
Watch a folder and auto-organize new files as they appear:
\`\`\`bash
python3 organizer.py watch ~/Downloads
\`\`\`
Press Ctrl+C to stop watching. Like `organize`, watch sessions are logged
and can be undone with `python3 organizer.py undo`.

## How PDF classification works

For each PDF, the tool extracts text from the first page and searches
for category-specific keywords (e.g. "invoice", "total due" for
Invoices; "professional summary", "work experience" for Resumes).
If no keywords match, or the PDF has no extractable text (like a
scanned document), it falls back to the generic Documents category.

## Notes

- Only scans the top level of a folder, not subfolders
- `.DS_Store` files are automatically ignored
- Session logs are stored in `~/.file_organizer/sessions/`