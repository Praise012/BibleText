import re
from typing import Optional, Tuple, Dict
from database import BibleDatabase

class BibleReferenceParser:
    """
    Parses fast user inputs in BibleShow format:
    Examples:
      - 'Jn 3 16' -> John, chap 3, verse 16
      - 'Jn 3:16' -> John, chap 3, verse 16
      - 'Gen 1:1-5' -> Genesis, chap 1, verses 1 through 5
      - 'Gen 1 1-5' -> Genesis, chap 1, verses 1 through 5
      - '1 Cor 13 4-8' -> 1 Corinthians, chap 13, verses 4 through 8
      - 'Ps 23' -> Psalms, chap 23, all verses
      - '1John 1:9' -> 1 John, chap 1, verse 9
    """
    def __init__(self, db: BibleDatabase):
        self.db = db

    def parse(self, input_text: str) -> Optional[Dict]:
        """
        Parses text and returns:
        {
           'book': book_dict,
           'chapter': int,
           'start_verse': int or None,
           'end_verse': int or None,
           'raw_reference': str
        }
        or None if parsing failed.
        """
        text = input_text.strip()
        if not text:
            return None

        # Pattern 1: Leading book identifier (including optional number '1', '2', '3')
        # e.g., "1 Cor 13:4-8", "Jn 3 16", "Gen 1:1-5", "Ps 23"
        # Regex captures:
        # 1. Book text (may have numbers and spaces e.g. "1 Cor", "Song of Solomon", "Jn")
        # 2. Chapter number
        # 3. Optional verse / verse range separated by ':' or space
        regex = r'^\s*([1-3]?\s*[a-zA-Z\s]+?)\s*(\d+)(?:[:\s]+(\d+)(?:\s*[-–]\s*(\d+))?)?\s*$'
        match = re.match(regex, text)

        if not match:
            # Fallback check: maybe just book name e.g. "Genesis" or "John"
            book_only = self.db.find_book_by_name_or_abbrev(text)
            if book_only:
                return {
                    'book': book_only,
                    'chapter': 1,
                    'start_verse': 1,
                    'end_verse': 1,
                    'raw_reference': f"{book_only['name']} 1:1"
                }
            return None

        book_str, chap_str, start_verse_str, end_verse_str = match.groups()

        book = self.db.find_book_by_name_or_abbrev(book_str.strip())
        if not book:
            return None

        chapter = int(chap_str)
        # Cap chapter to book limit if exceeded
        if chapter < 1:
            chapter = 1
        elif chapter > book['chapter_count']:
            chapter = book['chapter_count']

        start_verse = int(start_verse_str) if start_verse_str else None
        end_verse = int(end_verse_str) if end_verse_str else None

        if start_verse and end_verse and end_verse < start_verse:
            start_verse, end_verse = end_verse, start_verse

        if start_verse and end_verse:
            raw_ref = f"{book['name']} {chapter}:{start_verse}-{end_verse}"
        elif start_verse:
            raw_ref = f"{book['name']} {chapter}:{start_verse}"
        else:
            raw_ref = f"{book['name']} {chapter}"

        return {
            'book': book,
            'chapter': chapter,
            'start_verse': start_verse,
            'end_verse': end_verse,
            'raw_reference': raw_ref
        }
