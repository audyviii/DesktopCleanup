"""DesktopCleanup organizes files with a scan-first, confirm-before-moving workflow."""

import csv
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk


IGNORED_FILE_NAMES = {"desktop.ini", "downloads.ini", "thumbs.db", ".ds_store"}

FILE_CATEGORIES = {
    "Documents": {
        ".abw",
        ".doc",
        ".docm",
        ".docx",
        ".dot",
        ".dotm",
        ".dotx",
        ".log",
        ".odt",
        ".pages",
        ".pdf",
        ".rtf",
        ".tex",
        ".txt",
        ".wpd",
    },
    "Ebooks": {".azw", ".azw3", ".cbr", ".cbz", ".epub", ".fb2", ".ibooks", ".lit", ".mobi"},
    "Images": {
        ".ai",
        ".avif",
        ".bmp",
        ".cr2",
        ".dng",
        ".gif",
        ".heic",
        ".heif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".nef",
        ".png",
        ".psd",
        ".raw",
        ".svg",
        ".tif",
        ".tiff",
        ".webp",
    },
    "Design": {
        ".afdesign",
        ".afphoto",
        ".ase",
        ".fig",
        ".indd",
        ".sketch",
        ".xd",
    },
    "Spreadsheets": {
        ".csv",
        ".dif",
        ".numbers",
        ".ods",
        ".tsv",
        ".xls",
        ".xlsb",
        ".xlsm",
        ".xlsx",
    },
    "Presentations": {".key", ".odp", ".pot", ".potx", ".pps", ".ppsx", ".ppt", ".pptm", ".pptx"},
    "Data": {
        ".db",
        ".db3",
        ".jsonl",
        ".mdb",
        ".parquet",
        ".sav",
        ".sqlite",
        ".sqlite3",
        ".sql",
    },
    "Archives": {
        ".7z",
        ".bz2",
        ".cab",
        ".dmg",
        ".gz",
        ".iso",
        ".jar",
        ".rar",
        ".tar",
        ".tgz",
        ".xz",
        ".zip",
        ".zipx",
    },
    "Audio": {
        ".aac",
        ".aif",
        ".aiff",
        ".flac",
        ".m4a",
        ".mid",
        ".midi",
        ".mp3",
        ".ogg",
        ".opus",
        ".wav",
        ".wma",
    },
    "Video": {
        ".3gp",
        ".avi",
        ".flv",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".webm",
        ".wmv",
    },
    "Code": {
        ".bat",
        ".c",
        ".cfg",
        ".cmd",
        ".conf",
        ".cpp",
        ".cs",
        ".css",
        ".env",
        ".go",
        ".h",
        ".hpp",
        ".html",
        ".ini",
        ".java",
        ".js",
        ".json",
        ".jsx",
        ".kt",
        ".lua",
        ".md",
        ".php",
        ".pl",
        ".ps1",
        ".py",
        ".rb",
        ".rs",
        ".scss",
        ".sh",
        ".swift",
        ".toml",
        ".ts",
        ".tsx",
        ".vb",
        ".xml",
        ".yaml",
        ".yml",
    },
    "Installers": {".apk", ".appinstaller", ".deb", ".exe", ".msi", ".pkg", ".rpm"},
    "Fonts": {".eot", ".fon", ".otf", ".ttc", ".ttf", ".woff", ".woff2"},
    "Certificates": {".cer", ".crt", ".csr", ".der", ".gpg", ".key", ".p12", ".p7b", ".pem", ".pfx"},
    "Shortcuts": {".lnk", ".url", ".webloc"},
    "Calendar Contacts": {".ics", ".vcf"},
}


@dataclass(frozen=True)
class FilePlan:
    """A planned file move shown to the user before anything changes."""

    source: Path
    destination: Path
    category: str


@dataclass(frozen=True)
class MoveResult:
    """A completed file move written to the activity log."""

    source: Path
    destination: Path
    category: str
    moved_at: str


def get_default_source() -> Path:
    """Return a practical starting folder for the source picker."""

    downloads = Path.home() / "Downloads"
    return downloads if downloads.exists() else Path.home()


def get_default_destination() -> Path:
    """Return the default folder where organized files are stored."""

    return Path.home() / "Documents" / "DesktopCleanup Organized"


def category_for_file(file_path: Path) -> str:
    """Map a file extension to one of the configured destination categories."""

    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"


def is_ignored_file(file_path: Path) -> bool:
    """Return True for system files that should not appear in cleanup results."""

    return file_path.name.lower() in IGNORED_FILE_NAMES


def make_unique_path(destination: Path) -> Path:
    """Return a destination path that will not overwrite an existing file."""

    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def build_file_plan(file_path: Path, destination_root: Path) -> FilePlan:
    """Create a move plan for one file without touching the filesystem."""

    category = category_for_file(file_path)
    destination = destination_root / category / file_path.name
    return FilePlan(source=file_path, destination=destination, category=category)


def scan_folder(source_folder: Path, destination_root: Path) -> list[FilePlan]:
    """Scan a folder and return planned moves for regular, non-system files."""

    source_folder = source_folder.expanduser().resolve()
    destination_root = destination_root.expanduser().resolve()

    if not source_folder.exists():
        raise FileNotFoundError(f"Source folder does not exist: {source_folder}")
    if not source_folder.is_dir():
        raise NotADirectoryError(f"Source path is not a folder: {source_folder}")

    plans = []
    for item in sorted(source_folder.iterdir(), key=lambda path: path.name.lower()):
        if not item.is_file() or is_ignored_file(item):
            continue
        plans.append(build_file_plan(item, destination_root))
    return plans


def move_files(file_plans: list[FilePlan]) -> list[MoveResult]:
    """Move files from approved plans and return results for logging."""

    results = []
    moved_at = datetime.now().isoformat(timespec="seconds")

    for plan in file_plans:
        if not plan.source.exists():
            continue

        plan.destination.parent.mkdir(parents=True, exist_ok=True)
        safe_destination = make_unique_path(plan.destination)
        shutil.move(str(plan.source), str(safe_destination))
        results.append(
            MoveResult(
                source=plan.source,
                destination=safe_destination,
                category=plan.category,
                moved_at=moved_at,
            )
        )

    return results


def write_move_log(destination_root: Path, results: list[MoveResult]) -> Path | None:
    """Append completed moves to a CSV log and return the log path."""

    if not results:
        return None

    destination_root.mkdir(parents=True, exist_ok=True)
    log_path = destination_root / "desktop_cleanup_log.csv"
    log_exists = log_path.exists()

    with log_path.open("a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        if not log_exists:
            writer.writerow(["moved_at", "category", "source", "destination"])
        for result in results:
            writer.writerow(
                [
                    result.moved_at,
                    result.category,
                    str(result.source),
                    str(result.destination),
                ]
            )

    return log_path


class DesktopCleanupApp:
    """Tkinter interface for scanning, previewing, and moving files."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Desktop Cleanup")
        self.root.resizable(True, True)

        self.source_var = tk.StringVar(value=str(get_default_source()))
        self.destination_var = tk.StringVar(value=str(get_default_destination()))
        self.status_var = tk.StringVar(value="Choose folders, scan, then move selected files.")
        self.file_plans: list[FilePlan] = []

        self._build_layout()

    def _build_layout(self) -> None:
        """Build the folder inputs, action buttons, preview table, and status bar."""

        frame = ttk.Frame(self.root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        ttk.Label(frame, text="Source").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(frame, textvariable=self.source_var).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse", command=self._choose_source).grid(
            row=0,
            column=2,
            padx=(8, 0),
            pady=4,
        )

        ttk.Label(frame, text="Destination").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(frame, textvariable=self.destination_var).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse", command=self._choose_destination).grid(
            row=1,
            column=2,
            padx=(8, 0),
            pady=4,
        )

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 8))
        ttk.Button(buttons, text="Scan", command=self.scan).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Move Selected", command=self.move_selected).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text="Move All", command=self.move_all).grid(row=0, column=2)

        columns = ("name", "category", "destination")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("name", text="File")
        self.tree.heading("category", text="Category")
        self.tree.heading("destination", text="Destination")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("destination", width=420, anchor="w")
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=3, column=3, sticky="ns")

        ttk.Label(frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _choose_source(self) -> None:
        """Open a folder picker for the source folder."""

        folder = filedialog.askdirectory(initialdir=self.source_var.get())
        if folder:
            self.source_var.set(folder)

    def _choose_destination(self) -> None:
        """Open a folder picker for the destination folder."""

        folder = filedialog.askdirectory(initialdir=self.destination_var.get())
        if folder:
            self.destination_var.set(folder)

    def scan(self) -> None:
        """Refresh the preview table with planned moves for the selected folder."""

        try:
            self.file_plans = scan_folder(Path(self.source_var.get()), Path(self.destination_var.get()))
        except (OSError, ValueError) as error:
            messagebox.showerror("Scan failed", str(error))
            return

        self.tree.delete(*self.tree.get_children())
        for index, plan in enumerate(self.file_plans):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(plan.source.name, plan.category, str(plan.destination)),
            )

        count = len(self.file_plans)
        suffix = "s" if count != 1 else ""
        self.status_var.set(f"Scan complete. {count} file{suffix} ready for review.")

    def move_selected(self) -> None:
        """Move only the rows currently selected in the preview table."""

        selected_ids = self.tree.selection()
        selected_plans = [self.file_plans[int(item_id)] for item_id in selected_ids]
        self._confirm_and_move(selected_plans)

    def move_all(self) -> None:
        """Move every file currently shown in the preview table."""

        self._confirm_and_move(self.file_plans)

    def _confirm_and_move(self, selected_plans: list[FilePlan]) -> None:
        """Confirm the requested move operation, execute it, and refresh the preview."""

        if not selected_plans:
            messagebox.showinfo("Nothing selected", "Scan files first, then select one or more files to move.")
            return

        suffix = "s" if len(selected_plans) != 1 else ""
        confirmed = messagebox.askyesno(
            "Confirm move",
            f"Move {len(selected_plans)} file{suffix} to the destination folders?",
        )
        if not confirmed:
            return

        try:
            results = move_files(selected_plans)
            log_path = write_move_log(Path(self.destination_var.get()), results)
        except OSError as error:
            messagebox.showerror("Move failed", str(error))
            return

        self.scan()
        detail = f" Log written to {log_path}." if log_path else ""
        moved_suffix = "s" if len(results) != 1 else ""
        self.status_var.set(f"Moved {len(results)} file{moved_suffix}.{detail}")


def configure_windows_dpi() -> None:
    """Ask Windows for DPI-aware rendering when the API is available."""

    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


def main() -> None:
    """Start the DesktopCleanup GUI."""

    configure_windows_dpi()
    root = tk.Tk()
    DesktopCleanupApp(root)
    root.minsize(850, 450)
    root.mainloop()


if __name__ == "__main__":
    main()
