import sqlite3

DATABASE = "data/clinical_trials.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, pmid
    FROM abstracts
    ORDER BY id
""")

rows = cursor.fetchall()

print("\n========== ABSTRACTS IN DATABASE ==========")

for row in rows:
    print(row[0], ":", row[1])

print("\nTotal:", len(rows))

conn.close()