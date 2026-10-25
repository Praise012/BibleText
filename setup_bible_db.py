import sqlite3
import os
from database import BibleDatabase

BOOKS_DATA = [
    # Old Testament (39 books)
    (1, "OT", "Genesis", "gen,gn,ge", 50),
    (2, "OT", "Exodus", "exo,ex", 40),
    (3, "OT", "Leviticus", "lev,lv", 27),
    (4, "OT", "Numbers", "num,nm,nb", 36),
    (5, "OT", "Deuteronomy", "deut,dt", 34),
    (6, "OT", "Joshua", "josh,jos", 24),
    (7, "OT", "Judges", "judg,jdg", 21),
    (8, "OT", "Ruth", "ruth,ru,rth", 4),
    (9, "OT", "1 Samuel", "1sam,1sa,1s", 31),
    (10, "OT", "2 Samuel", "2sam,2sa,2s", 24),
    (11, "OT", "1 Kings", "1kgs,1ki,1k", 22),
    (12, "OT", "2 Kings", "2kgs,2ki,2k", 25),
    (13, "OT", "1 Chronicles", "1chron,1ch", 29),
    (14, "OT", "2 Chronicles", "2chron,2ch", 36),
    (15, "OT", "Ezra", "ezra,ezr", 10),
    (16, "OT", "Nehemiah", "neh,ne", 13),
    (17, "OT", "Esther", "esth,es", 10),
    (18, "OT", "Job", "job,jb", 42),
    (19, "OT", "Psalms", "ps,psa,psalm,psalms", 150),
    (20, "OT", "Proverbs", "prov,prv,pr", 31),
    (21, "OT", "Ecclesiastes", "eccl,ecc", 12),
    (22, "OT", "Song of Solomon", "song,sos,ss", 8),
    (23, "OT", "Isaiah", "isa,is", 66),
    (24, "OT", "Jeremiah", "jer,jr", 52),
    (25, "OT", "Lamentations", "lam,la", 5),
    (26, "OT", "Ezekiel", "ezek,eze", 48),
    (27, "OT", "Daniel", "dan,da", 12),
    (28, "OT", "Hosea", "hos,ho", 14),
    (29, "OT", "Joel", "joel,jl", 3),
    (30, "OT", "Amos", "amos,am", 9),
    (31, "OT", "Obadiah", "obad,ob", 1),
    (32, "OT", "Jonah", "jonah,jon", 4),
    (33, "OT", "Micah", "mic,mc", 7),
    (34, "OT", "Nahum", "nah,na", 3),
    (35, "OT", "Habakkuk", "hab,hb", 3),
    (36, "OT", "Zephaniah", "zeph,zep", 3),
    (37, "OT", "Haggai", "hag,hg", 2),
    (38, "OT", "Zechariah", "zech,zec", 14),
    (39, "OT", "Malachi", "mal,ml", 4),

    # New Testament (27 books)
    (40, "NT", "Matthew", "matt,mat,mt", 28),
    (41, "NT", "Mark", "mk,mrk,mark", 16),
    (42, "NT", "Luke", "lk,luk,luke", 24),
    (43, "NT", "John", "jn,jhn,john", 21),
    (44, "NT", "Acts", "act,acts,ac", 28),
    (45, "NT", "Romans", "rom,ro,rm", 16),
    (46, "NT", "1 Corinthians", "1cor,1co", 16),
    (47, "NT", "2 Corinthians", "2cor,2co", 13),
    (48, "NT", "Galatians", "gal,ga", 6),
    (49, "NT", "Ephesians", "eph,ep", 6),
    (50, "NT", "Philippians", "phil,php", 4),
    (51, "NT", "Colossians", "col,co", 4),
    (52, "NT", "1 Thessalonians", "1thess,1th", 5),
    (53, "NT", "2 Thessalonians", "2thess,2th", 3),
    (54, "NT", "1 Timothy", "1tim,1ti", 6),
    (55, "NT", "2 Timothy", "2tim,2ti", 4),
    (56, "NT", "Titus", "tit,ti", 3),
    (57, "NT", "Philemon", "phlm,phm", 1),
    (58, "NT", "Hebrews", "heb,he", 13),
    (59, "NT", "James", "jas,jm", 5),
    (60, "NT", "1 Peter", "1pet,1pe", 5),
    (61, "NT", "2 Peter", "2pet,2pe", 3),
    (62, "NT", "1 John", "1jn,1jhn", 5),
    (63, "NT", "2 John", "2jn,2jhn", 1),
    (64, "NT", "3 John", "3jn,3jhn", 1),
    (65, "NT", "Jude", "jude,jd", 1),
    (66, "NT", "Revelation", "rev,re", 22)
]

TRANSLATIONS_DATA = [
    ("KJV", "King James Version", "English", "KJV"),
    ("WEB", "World English Bible", "English", "WEB"),
    ("LSG", "Louis Segond (1910)", "French", "LSG"),
    ("RV1909", "Reina-Valera 1909", "Spanish", "RV"),
    ("SUV", "Swahili Union Version", "Swahili", "SUV"),
    ("ASV", "American Standard Version (1901)", "English", "ASV"),
    ("DARBY", "Darby Bible Translation", "English", "DBY"),
    ("YLT", "Young's Literal Translation", "English", "YLT")
]

SEED_VERSES = [
    # Genesis 1
    ("KJV", 1, 1, 1, "In the beginning God created the heaven and the earth."),
    ("KJV", 1, 1, 2, "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."),
    ("KJV", 1, 1, 3, "And God said, Let there be light: and there was light."),
    ("KJV", 1, 1, 4, "And God saw the light, that it was good: and God divided the light from the darkness."),
    ("KJV", 1, 1, 5, "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day."),

    ("WEB", 1, 1, 1, "In the beginning, God created the heavens and the earth."),
    ("WEB", 1, 1, 2, "The earth was formless and empty. Darkness was on the surface of the deep and God’s Spirit was hovering over the surface of the waters."),
    ("WEB", 1, 1, 3, "God said, 'Let there be light,' and there was light."),
    ("WEB", 1, 1, 4, "God saw the light, and saw that it was good. God divided the light from the darkness."),
    ("WEB", 1, 1, 5, "God called the light 'day', and the darkness he called 'night'. There was evening and there was morning, the first day."),

    ("LSG", 1, 1, 1, "Au commencement, Dieu créa les cieux et la terre."),
    ("LSG", 1, 1, 2, "La terre était informe et vide: il y avait des ténèbres à la surface de l'abîme, et l'esprit de Dieu se mouvait au-dessus des eaux."),
    ("LSG", 1, 1, 3, "Dieu dit: Que la lumière soit! Et la lumière fut."),

    ("RV1909", 1, 1, 1, "En el principio crió Dios los cielos y la tierra."),
    ("RV1909", 1, 1, 2, "Y la tierra estaba desordenada y vacía, y las tinieblas estaban sobre la haz del abismo, y el Espíritu de Dios se movía sobre la haz de las aguas."),
    ("RV1909", 1, 1, 3, "Y dijo Dios: Sea la luz: y fué la luz."),

    ("SUV", 1, 1, 1, "Hapo mwanzo Mungu aliziumba mbingu na nchi."),
    ("SUV", 1, 1, 2, "Nayo nchi ilikuwa ukiwa, tena utupu, na giza lilikuwa juu ya uso wa vilindi vya maji; Roho ya Mungu ikatulia juu ya uso wa maji."),
    ("SUV", 1, 1, 3, "Mungu akasema, Iwe nuru; ikawa nuru."),

    # Psalms 23
    ("KJV", 19, 23, 1, "The LORD is my shepherd; I shall not want."),
    ("KJV", 19, 23, 2, "He maketh me to lie down in green pastures: he leadeth me beside the still waters."),
    ("KJV", 19, 23, 3, "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake."),
    ("KJV", 19, 23, 4, "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me."),
    ("KJV", 19, 23, 5, "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over."),
    ("KJV", 19, 23, 6, "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the LORD for ever."),

    ("WEB", 19, 23, 1, "Yahweh is my shepherd: I shall lack nothing."),
    ("WEB", 19, 23, 2, "He makes me lie down in green pastures. He leads me beside still waters."),
    ("WEB", 19, 23, 3, "He restores my soul. He guides me in the paths of righteousness for his name’s sake."),
    ("WEB", 19, 23, 4, "Even though I walk through the valley of the shadow of death, I will fear no evil, for you are with me. Your rod and your staff, they comfort me."),
    ("WEB", 19, 23, 5, "You prepare a table before me in the presence of my enemies. You have anointed my head with oil. My cup runs over."),
    ("WEB", 19, 23, 6, "Surely goodness and loving kindness shall follow me all the days of my life, and I will dwell in Yahweh’s house forever."),

    ("LSG", 19, 23, 1, "L'Éternel est mon berger: je ne manquerai de rien."),
    ("LSG", 19, 23, 2, "Il me fait reposer dans de verts pâturages, Il me dirige près des eaux paisibles."),
    ("LSG", 19, 23, 3, "Il restaure mon âme, Il me conduit dans les sentiers de la justice, À cause de son nom."),
    ("LSG", 19, 23, 4, "Quand je marche dans la vallée de l'ombre de la mort, Je ne crains aucun mal, car tu es avec moi: Ta houlette et ton bâton me rassurent."),

    ("RV1909", 19, 23, 1, "Jehová es mi pastor; nada me faltará."),
    ("RV1909", 19, 23, 2, "En lugares de delicados pastos me hará yacer: Junto á aguas de reposo me pastoreará."),
    ("RV1909", 19, 23, 3, "Confortará mi alma; Guiárame por sendas de justicia por amor de su nombre."),
    ("RV1909", 19, 23, 4, "Aunque ande en valle de sombra de muerte, No temeré mal alguno; porque tú estarás conmigo: Tu vara y tu cayado me infundirán aliento."),

    ("SUV", 19, 23, 1, "Bwana ndiye mchungaji wangu, Sitapungukiwa na kitu."),
    ("SUV", 19, 23, 2, "Katika malisho ya majani mabichi hunilaza, Kando ya maji ya utulivu huniongoza."),
    ("SUV", 19, 23, 3, "Hunihuisha nafsi yangu; na kuniongoza Katika njia za haki kwa ajili ya jina lake."),
    ("SUV", 19, 23, 4, "Hata nijapopita kati ya bonde la uvuli wa mauti, Sitaogopa mabaya; Kwa maana Wewe u pamoja nami, Gongo lako na fimbo yako vyanifariji."),

    # Proverbs 3
    ("KJV", 20, 3, 5, "Trust in the LORD with all thine heart; and lean not unto thine own understanding."),
    ("KJV", 20, 3, 6, "In all thy ways acknowledge him, and he shall direct thy paths."),
    ("WEB", 20, 3, 5, "Trust in Yahweh with all your heart, and don’t lean on your own understanding."),
    ("WEB", 20, 3, 6, "In all your ways acknowledge him, and he will make your paths straight."),

    # Isaiah 40
    ("KJV", 23, 40, 29, "He giveth power to the faint; and to them that have no might he increaseth strength."),
    ("KJV", 23, 40, 31, "But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint."),
    ("WEB", 23, 40, 31, "But those who wait for Yahweh will renew their strength. They will mount up with wings like eagles. They will run, and not be weary. They will walk, and not faint."),

    # Matthew 28:18-20 (Great Commission)
    ("KJV", 40, 28, 18, "And Jesus came and spake unto them, saying, All power is given unto me in heaven and in earth."),
    ("KJV", 40, 28, 19, "Go ye therefore, and teach all nations, baptizing them in the name of the Father, and of the Son, and of the Holy Ghost:"),
    ("KJV", 40, 28, 20, "Teaching them to observe all things whatsoever I have commanded you: and, lo, I am with you alway, even unto the end of the world. Amen."),

    ("WEB", 40, 28, 18, "Jesus came to them and spoke to them, saying, 'All authority has been given to me in heaven and on earth.'"),
    ("WEB", 40, 28, 19, "'Go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit,'"),
    ("WEB", 40, 28, 20, "'teaching them to observe all things that I commanded you. Behold, I am with you always, even to the end of the age.' Amen."),

    # John 3:16-18
    ("KJV", 43, 3, 16, "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."),
    ("KJV", 43, 3, 17, "For God sent not his Son into the world to condemn the world; but that the world through him might be saved."),
    ("KJV", 43, 3, 18, "He that believeth on him is not condemned: but he that believeth not is condemned already, because he hath not believed in the name of the only begotten Son of God."),

    ("WEB", 43, 3, 16, "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."),
    ("WEB", 43, 3, 17, "For God didn’t send his Son into the world to judge the world, but that the world should be saved through him."),
    ("WEB", 43, 3, 18, "He who believes in him is not judged. He who doesn’t believe has been judged already, because he has not believed in the name of the one and only Son of God."),

    ("LSG", 43, 3, 16, "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle."),
    ("LSG", 43, 3, 17, "Dieu, en effet, n'a pas envoyé son Fils dans le monde pour qu'il juge le monde, mais pour que le monde soit sauvé par lui."),

    ("RV1909", 43, 3, 16, "Porque de tal manera amó Dios al mundo, que ha dado á su Hijo unigénito, para que todo aquel que en él cree, no se pierda, mas tenga vida eterna."),
    ("RV1909", 43, 3, 17, "Porque no envió Dios á su Hijo al mundo, para que condene al mundo, mas para que el mundo sea salvo por él."),

    ("SUV", 43, 3, 16, "Kwa maana jinsi hii Mungu aliupenda ulimwengu, hata akamtoa Mwanawe pekee, ili kila mtu amwaminiye asipotee, bali awe na uzima wa milele."),
    ("SUV", 43, 3, 17, "Maana Mungu hakumtuma Mwana ulimwenguni ili auhukumu ulimwengu, bali ulimwengu uokolewe kwa yeye."),

    # Romans 8:28, 31, 38-39
    ("KJV", 45, 8, 28, "And we know that all things work together for good to them that love God, to them who are the called according to his purpose."),
    ("KJV", 45, 8, 31, "What shall we then say to these things? If God be for us, who can be against us?"),
    ("KJV", 45, 8, 38, "For I am persuaded, that neither death, nor life, nor angels, nor principalities, nor powers, nor things present, nor things to come,"),
    ("KJV", 45, 8, 39, "Nor height, nor depth, nor any other creature, shall be able to separate us from the love of God, which is in Christ Jesus our Lord."),

    ("WEB", 45, 8, 28, "We know that all things work together for good for those who love God, for those who are called according to his purpose."),
    ("WEB", 45, 8, 31, "What then shall we say about these things? If God is for us, who can be against us?"),

    # 1 Corinthians 13:4-8 (Love chapter)
    ("KJV", 46, 13, 4, "Charity suffereth long, and is kind; charity envieth not; charity vaunteth not itself, is not puffed up,"),
    ("KJV", 46, 13, 5, "Doth not behave itself unseemly, seeketh not her own, is not easily provoked, thinketh no evil;"),
    ("KJV", 46, 13, 6, "Rejoiceth not in iniquity, but rejoiceth in the truth;"),
    ("KJV", 46, 13, 7, "Beareth all things, believeth all things, hopeth all things, endureth all things."),
    ("KJV", 46, 13, 8, "Charity never faileth: but whether there be prophecies, they shall fail; whether there be tongues, they shall cease; whether there be knowledge, it shall vanish away."),

    ("WEB", 46, 13, 4, "Love is patient and is kind. Love doesn’t envy. Love doesn’t brag, is not proud,"),
    ("WEB", 46, 13, 5, "doesn’t behave itself inappropriately, doesn’t seek its own way, is not provoked, takes no account of evil;"),
    ("WEB", 46, 13, 6, "doesn’t rejoice in unrighteousness, but rejoices with the truth;"),
    ("WEB", 46, 13, 7, "bears all things, believes all things, hopes all things, and endures all things."),
    ("WEB", 46, 13, 8, "Love never fails. But where there are prophecies, they will be done away with. Where there are various languages, they will cease. Where there is knowledge, it will be done away with."),

    # Philippians 4:6-7, 13
    ("KJV", 50, 4, 6, "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God."),
    ("KJV", 50, 4, 7, "And the peace of God, which passeth all understanding, shall keep your hearts and minds through Christ Jesus."),
    ("KJV", 50, 4, 13, "I can do all things through Christ which strengtheneth me."),

    ("WEB", 50, 4, 13, "I can do all things through Christ, who strengthens me."),
    ("LSG", 50, 4, 13, "Je puis tout par celui qui me fortifie."),
    ("RV1909", 50, 4, 13, "Todo lo puedo en Cristo que me fortalece."),
    ("SUV", 50, 4, 13, "Nayaweza mambo yote katika yeye anitiaye nguvu."),

    # Hebrews 11:1
    ("KJV", 58, 11, 1, "Now faith is the substance of things hoped for, the evidence of things not seen."),
    ("WEB", 58, 11, 1, "Now faith is assurance of things hoped for, proof of things not seen."),

    # Revelation 21:4
    ("KJV", 66, 21, 4, "And God shall wipe away all tears from their eyes; and there shall be no more death, neither sorrow, nor crying, neither shall there be any more pain: for the former things are passed away."),
    ("WEB", 66, 21, 4, "He will wipe away every tear from their eyes. Death will be no more; neither will there be mourning, nor crying, nor pain, any more. The first things have passed away."),

    # ASV
    ("ASV", 1, 1, 1, "In the beginning God created the heavens and the earth."),
    ("ASV", 1, 1, 2, "And the earth was waste and void; and darkness was upon the face of the deep: and the Spirit of God moved upon the face of the waters."),
    ("ASV", 1, 1, 3, "And God said, Let there be light: and there was light."),
    ("ASV", 19, 23, 1, "Jehovah is my shepherd; I shall not want."),
    ("ASV", 19, 23, 2, "He maketh me to lie down in green pastures; He leadeth me beside still waters."),
    ("ASV", 19, 23, 3, "He restoreth my soul: He guideth me in the paths of righteousness for his name's sake."),
    ("ASV", 19, 23, 4, "Yea, though I walk through the valley of the shadow of death, I will fear no evil; for thou art with me; Thy rod and thy staff, they comfort me."),
    ("ASV", 43, 3, 16, "For God so loved the world, that he gave his only begotten Son, that whosoever believeth on him should not perish, but have eternal life."),
    ("ASV", 45, 8, 28, "And we know that to them that love God all things work together for good, even to them that are called according to his purpose."),
    ("ASV", 50, 4, 13, "I can do all things in him that strengtheneth me."),

    # DARBY
    ("DARBY", 1, 1, 1, "In the beginning God created the heavens and the earth."),
    ("DARBY", 1, 1, 3, "And God said, Let there be light. And there was light."),
    ("DARBY", 19, 23, 1, "Jehovah is my shepherd; I shall not want."),
    ("DARBY", 43, 3, 16, "For God so loved the world, that he gave his only-begotten Son, that whosoever believes on him may not perish, but have life eternal."),
    ("DARBY", 50, 4, 13, "I have strength for all things in him that gives me power."),

    # YLT
    ("YLT", 1, 1, 1, "In the beginning of God's preparing the heavens and the earth --"),
    ("YLT", 1, 1, 3, "and God saith, 'Let light be;' and light is."),
    ("YLT", 19, 23, 1, "A Psalm of David. Jehovah is my shepherd, I do not lack,"),
    ("YLT", 43, 3, 16, "for God did so love the world, that His Son -- the only begotten -- He gave, that every one who is believing in him may not perish, but may have life age-during."),
    ("YLT", 50, 4, 13, "For all things I have strength, in Christ's strengthening me.")
]

def build_database(db_filename="sample_bible.sqlite"):
    print(f"Building SQLite Bible database at: {db_filename}...")
    db = BibleDatabase(db_filename)
    cursor = db.conn.cursor()

    # Insert translations
    for t in TRANSLATIONS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO translations (id, name, language, abbreviation)
            VALUES (?, ?, ?, ?)
        """, t)

    # Insert 66 books
    for b in BOOKS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO books (id, testament, name, abbreviations, chapter_count)
            VALUES (?, ?, ?, ?, ?)
        """, b)

    # Insert verses
    for v in SEED_VERSES:
        cursor.execute("""
            INSERT OR REPLACE INTO verses (translation_id, book_id, chapter, verse, text)
            VALUES (?, ?, ?, ?, ?)
        """, v)

    db.conn.commit()
    print("Database built successfully!")
    print(f"Total translations: {len(TRANSLATIONS_DATA)}")
    print(f"Total books registered: {len(BOOKS_DATA)}")
    print(f"Total sample verses seeded: {len(SEED_VERSES)}")
    db.close()

if __name__ == "__main__":
    build_database()
