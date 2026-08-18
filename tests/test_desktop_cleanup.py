import tempfile
import unittest
from pathlib import Path

from DeskC import category_for_file, make_unique_path, move_files, scan_folder, write_move_log


class DesktopCleanupTests(unittest.TestCase):
    def test_category_for_known_file_type(self):
        self.assertEqual(category_for_file(Path("report.pdf")), "Documents")
        self.assertEqual(category_for_file(Path("photo.PNG")), "Images")

    def test_category_for_expanded_file_types(self):
        expected_categories = {
            "book.epub": "Ebooks",
            "mockup.fig": "Design",
            "event.ics": "Calendar Contacts",
            "certificate.pfx": "Certificates",
            "installer.exe": "Installers",
            "font.woff2": "Fonts",
            "dataset.parquet": "Data",
            "shortcut.lnk": "Shortcuts",
        }

        for file_name, category in expected_categories.items():
            with self.subTest(file_name=file_name):
                self.assertEqual(category_for_file(Path(file_name)), category)

    def test_category_for_unknown_file_type(self):
        self.assertEqual(category_for_file(Path("backup.custom")), "Other")

    def test_scan_folder_skips_directories_and_system_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            destination = Path(temp_dir) / "organized"
            source.mkdir()
            (source / "notes.txt").write_text("hello", encoding="utf-8")
            (source / "desktop.ini").write_text("system", encoding="utf-8")
            (source / "folder").mkdir()

            plans = scan_folder(source, destination)

            self.assertEqual(len(plans), 1)
            self.assertEqual(plans[0].source.name, "notes.txt")
            self.assertEqual(plans[0].category, "Documents")

    def test_make_unique_path_appends_counter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            existing = folder / "notes.txt"
            existing.write_text("one", encoding="utf-8")

            unique = make_unique_path(existing)

            self.assertEqual(unique.name, "notes (1).txt")

    def test_move_files_uses_collision_safe_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            destination = Path(temp_dir) / "organized"
            source.mkdir()
            (source / "notes.txt").write_text("new", encoding="utf-8")
            existing_folder = destination / "Documents"
            existing_folder.mkdir(parents=True)
            (existing_folder / "notes.txt").write_text("old", encoding="utf-8")

            plans = scan_folder(source, destination)
            results = move_files(plans)

            self.assertEqual(len(results), 1)
            self.assertFalse((source / "notes.txt").exists())
            self.assertTrue((existing_folder / "notes.txt").exists())
            self.assertTrue((existing_folder / "notes (1).txt").exists())

    def test_write_move_log_returns_none_without_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertIsNone(write_move_log(Path(temp_dir), []))


if __name__ == "__main__":
    unittest.main()
