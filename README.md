# DesktopCleanup
A small Tkinter app for reviewing and organizing files from a folder such as Downloads or Desktop.

DesktopCleanup scans a folder, previews where each file will go, and moves only after confirmation. It is designed to be safer than a one-click cleanup script because it avoids hidden deletes and keeps a CSV move log.

## Features

- Choose a source folder and destination folder.
- Preview planned file moves before anything changes.
- Move selected files or all scanned files.
- Sort a broad set of common file types into category folders.
- Place unrecognized file types in an `Other` folder.
- Preserve existing destination files by adding a counter such as `notes (1).txt`.
- Skip common system files such as `desktop.ini`.
- Write `desktop_cleanup_log.csv` in the destination folder.

## Categories

DesktopCleanup recognizes common formats for documents, ebooks, images, design files, spreadsheets, presentations, data files, archives, audio, video, code/config files, installers, fonts, certificates, shortcuts, calendar files, and contacts.

## Usage

Run the app:

```bash
python DeskC.py
```

Recommended workflow:

1. Choose the source folder.
2. Choose the destination folder.
3. Click `Scan`.
4. Review the preview table.
5. Select files and click `Move Selected`, or click `Move All`.

## Development

Run syntax checks:

```bash
python -m py_compile DeskC.py
```

Run tests:

```powershell
$env:PYTHONPATH='.'; python -m unittest discover -s tests
```

## Safety Notes

The app moves files but does not delete them. Still, test with a small sample folder first before using it on an important Desktop or Downloads folder.
