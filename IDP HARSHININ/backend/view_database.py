import sqlite3

DATABASE = "data/clinical_trials.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("\n========== ABSTRACTS ==========")

cursor.execute("SELECT * FROM abstracts")

for row in cursor.fetchall():
    print(row)


print("\n========== ENTITIES ==========")

cursor.execute("SELECT * FROM entities")

for row in cursor.fetchall():
    print(row)


print("\n========== RELATIONS ==========")

cursor.execute("SELECT * FROM relations")

for row in cursor.fetchall():
    print(row)


conn.close()