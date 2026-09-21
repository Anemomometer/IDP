import sqlite3

DATABASE = "data/clinical_trials.db"


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abstracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pmid TEXT UNIQUE,
            abstract TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abstract_id INTEGER,
            entity_text TEXT,
            entity_type TEXT,
            assertion TEXT,
            start_pos INTEGER,
            end_pos INTEGER,
            FOREIGN KEY (abstract_id) REFERENCES abstracts(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abstract_id INTEGER,
            source_entity TEXT,
            relation_type TEXT,
            target_entity TEXT,
            FOREIGN KEY (abstract_id) REFERENCES abstracts(id)
        )
    """)

    conn.commit()
    conn.close()

    print("Database created successfully!")


def save_result(pmid, text, entities, relations):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Insert abstract
    cursor.execute(
        "INSERT OR IGNORE INTO abstracts (pmid, abstract) VALUES (?, ?)",
        (pmid, text)
    )

    # Get abstract ID
    cursor.execute(
        "SELECT id FROM abstracts WHERE pmid = ?",
        (pmid,)
    )

    abstract_id = cursor.fetchone()[0]

    # Remove old extracted data for this abstract
    # This prevents duplicates when we run the pipeline again.
    cursor.execute(
        "DELETE FROM entities WHERE abstract_id = ?",
        (abstract_id,)
    )

    cursor.execute(
        "DELETE FROM relations WHERE abstract_id = ?",
        (abstract_id,)
    )

    # Store unique entities
    seen_entities = set()

    for entity in entities:

        entity_text = " ".join(entity["text"].split())
        entity_type = entity["label"]
        assertion = entity["assertion"]

        # Unique key
        key = (
            entity_text.lower(),
            entity_type,
            assertion
        )

        if key in seen_entities:
            continue

        seen_entities.add(key)

        cursor.execute("""
            INSERT INTO entities
            (
                abstract_id,
                entity_text,
                entity_type,
                assertion,
                start_pos,
                end_pos
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            abstract_id,
            entity_text,
            entity_type,
            assertion,
            entity["start"],
            entity["end"]
        ))

    # Store unique relations
    seen_relations = set()

    for relation in relations:

        source = " ".join(relation["source"].split())
        relation_type = relation["relation"]
        target = " ".join(relation["target"].split())

        key = (
            source.lower(),
            relation_type,
            target.lower()
        )

        if key in seen_relations:
            continue

        seen_relations.add(key)

        cursor.execute("""
            INSERT INTO relations
            (
                abstract_id,
                source_entity,
                relation_type,
                target_entity
            )
            VALUES (?, ?, ?, ?)
        """, (
            abstract_id,
            source,
            relation_type,
            target
        ))

    conn.commit()
    conn.close()

    print(f"Data saved successfully for PMID {pmid}!")


if __name__ == "__main__":
    create_database()