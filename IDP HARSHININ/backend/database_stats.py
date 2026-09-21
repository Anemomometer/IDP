import sqlite3

DATABASE = "data/clinical_trials.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("\n========== DATABASE STATISTICS ==========")

cursor.execute("SELECT COUNT(*) FROM abstracts")
print("Total abstracts:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM entities")
print("Total entities:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM relations")
print("Total relations:", cursor.fetchone()[0])

print("\n========== ENTITY TYPES ==========")

cursor.execute("""
    SELECT entity_type, COUNT(*)
    FROM entities
    GROUP BY entity_type
""")

for row in cursor.fetchall():
    print(row[0], ":", row[1])

print("\n========== ASSERTION TYPES ==========")

cursor.execute("""
    SELECT assertion, COUNT(*)
    FROM entities
    GROUP BY assertion
""")

for row in cursor.fetchall():
    print(row[0], ":", row[1])

conn.close()