import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from database import BibleDatabase
from parser import BibleReferenceParser
from settings import SettingsManager, DEFAULT_SETTINGS

class TestBibleShow(unittest.TestCase):
    def setUp(self):
        db_file = SCRIPT_DIR / "sample_bible.sqlite"
        if not db_file.exists():
            from setup_bible_db import build_database
            build_database(str(db_file))
        self.db = BibleDatabase(str(db_file))
        self.parser = BibleReferenceParser(self.db)
        self.settings = SettingsManager("/tmp/test_bibleshow_settings.json")

    def tearDown(self):
        self.db.close()
        test_file = Path("/tmp/test_bibleshow_settings.json")
        if test_file.exists():
            test_file.unlink()

    def test_database_translations(self):
        translations = self.db.get_translations()
        self.assertGreaterEqual(len(translations), 5)
        ids = [t['id'] for t in translations]
        self.assertIn("KJV", ids)
        self.assertIn("WEB", ids)
        self.assertIn("LSG", ids)
        self.assertIn("RV1909", ids)
        self.assertIn("SUV", ids)

    def test_database_books(self):
        books = self.db.get_books()
        self.assertEqual(len(books), 66)
        ot_books = self.db.get_books("OT")
        nt_books = self.db.get_books("NT")
        self.assertEqual(len(ot_books), 39)
        self.assertEqual(len(nt_books), 27)

    def test_syntax_parser_john_3_16(self):
        parsed = self.parser.parse("Jn 3 16")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['book']['name'], "John")
        self.assertEqual(parsed['chapter'], 3)
        self.assertEqual(parsed['start_verse'], 16)

    def test_syntax_parser_colon_notation(self):
        parsed = self.parser.parse("Jn 3:16")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['book']['name'], "John")
        self.assertEqual(parsed['chapter'], 3)
        self.assertEqual(parsed['start_verse'], 16)

    def test_syntax_parser_verse_range(self):
        parsed = self.parser.parse("Gen 1:1-5")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['book']['name'], "Genesis")
        self.assertEqual(parsed['chapter'], 1)
        self.assertEqual(parsed['start_verse'], 1)
        self.assertEqual(parsed['end_verse'], 5)

    def test_syntax_parser_corinthians(self):
        parsed = self.parser.parse("1 Cor 13 4-8")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['book']['name'], "1 Corinthians")
        self.assertEqual(parsed['chapter'], 13)
        self.assertEqual(parsed['start_verse'], 4)
        self.assertEqual(parsed['end_verse'], 8)

    def test_syntax_parser_psalms(self):
        parsed = self.parser.parse("Ps 23")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['book']['name'], "Psalms")
        self.assertEqual(parsed['chapter'], 23)

    def test_parallel_translations_lookup(self):
        # Test John 3:16 in KJV, WEB, and French LSG
        kjv_v = self.db.get_verses("KJV", 43, 3, 16, 16)
        web_v = self.db.get_verses("WEB", 43, 3, 16, 16)
        lsg_v = self.db.get_verses("LSG", 43, 3, 16, 16)

        self.assertEqual(len(kjv_v), 1)
        self.assertEqual(len(web_v), 1)
        self.assertEqual(len(lsg_v), 1)

        self.assertIn("God so loved the world", kjv_v[0]['text'])
        self.assertIn("one and only Son", web_v[0]['text'])
        self.assertIn("Dieu a tant aimé le monde", lsg_v[0]['text'])

    def test_settings_save_and_merge(self):
        self.settings.set("typography", "font_size", 54)
        self.settings.set("display", "output_mode", "bottom-right")
        self.settings.save()

        # Reload
        s2 = SettingsManager("/tmp/test_bibleshow_settings.json")
        self.assertEqual(s2.get("typography", "font_size"), 54)
        self.assertEqual(s2.get("display", "output_mode"), "bottom-right")
        self.assertEqual(s2.get("typography", "text_color"), "#FFFFFF")

    def test_download_online_bible(self):
        success, msg = self.db.download_online_bible("ASV")
        self.assertTrue(success)
        translations = self.db.get_translations()
        self.assertTrue(any(t['id'] == 'ASV' for t in translations))

        # Check verse
        v = self.db.get_verses("ASV", 43, 3, 16, 16)
        self.assertEqual(len(v), 1)
        self.assertIn("eternal life", v[0]['text'])

    def test_preinstalled_translations_coverage(self):
        translations = self.db.get_translations()
        ids = [t['id'] for t in translations]
        required = ["KJV", "WEB", "LSG", "RV1909", "SUV", "ASV", "DARBY", "YLT"]
        for req in required:
            self.assertIn(req, ids, f"Missing required pre-installed translation: {req}")

    def test_all_books_verse_guarantee(self):
        # Query various books & chapters across OT and NT
        # Ruth (book 8), Psalms 23 (book 19), John 3 (book 43), Revelation 21 (book 66)
        ruth_v = self.db.get_verses("KJV", 8, 1)
        self.assertGreaterEqual(len(ruth_v), 1)
        self.assertIn("Ruth", ruth_v[0]['book_name'])

        darby_ps = self.db.get_verses("DARBY", 19, 23)
        self.assertGreaterEqual(len(darby_ps), 1)

        ylt_jn = self.db.get_verses("YLT", 43, 3)
        self.assertGreaterEqual(len(ylt_jn), 1)

        suv_rev = self.db.get_verses("SUV", 66, 21)
        self.assertGreaterEqual(len(suv_rev), 1)

    def test_hotkeys_configuration(self):
        hotkeys = self.settings.data.get("hotkeys", {})
        self.assertEqual(hotkeys.get("search"), "Ctrl+F")
        self.assertEqual(hotkeys.get("go_live"), "Return")
        self.assertEqual(hotkeys.get("clear"), "Escape")
        self.assertEqual(hotkeys.get("blackout"), "Ctrl+B")
        self.assertEqual(hotkeys.get("logo"), "Ctrl+L")
        self.assertEqual(hotkeys.get("fullscreen"), "F5")
        self.assertEqual(hotkeys.get("settings"), "Ctrl+T")

        # Custom re-binding
        self.settings.data["hotkeys"]["search"] = "Ctrl+Shift+F"
        self.settings.data["hotkeys"]["go_live"] = "Space"
        self.settings.save()

        s2 = SettingsManager("/tmp/test_bibleshow_settings.json")
        self.assertEqual(s2.data.get("hotkeys", {}).get("search"), "Ctrl+Shift+F")
        self.assertEqual(s2.data.get("hotkeys", {}).get("go_live"), "Space")

    def test_pip_output_modes(self):
        # Secondary monitor output does not auto launch on start
        self.assertFalse(self.settings.get("display", "launch_output_on_start"))
        self.assertEqual(self.settings.get("display", "output_mode"), "off")

        # Test changing PIP modes
        for mode in ["bottom-right", "bottom-left", "top-right", "top-left", "fullscreen", "off"]:
            self.settings.set("display", "output_mode", mode)
            self.assertEqual(self.settings.get("display", "output_mode"), mode)

if __name__ == "__main__":
    unittest.main()


