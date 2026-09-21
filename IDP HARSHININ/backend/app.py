from flask import Flask, request, jsonify
import sqlite3

from pipeline import run_pipeline

app = Flask(__name__)

DATABASE = "data/clinical_trials.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# 1. GET ALL ABSTRACTS
# ==========================================

@app.route("/api/abstracts", methods=["GET"])
def get_abstracts():

    conn = get_db_connection()

    abstracts = conn.execute("""
        SELECT id, pmid, abstract
        FROM abstracts
        ORDER BY id
    """).fetchall()

    conn.close()

    result = []

    for row in abstracts:
        result.append({
            "id": row["id"],
            "pmid": row["pmid"],
            "abstract": row["abstract"]
        })

    return jsonify(result)


# ==========================================
# 2. GET ONE ABSTRACT
# ==========================================

@app.route("/api/abstract/<pmid>", methods=["GET"])
def get_abstract(pmid):

    conn = get_db_connection()

    abstract = conn.execute("""
        SELECT id, pmid, abstract
        FROM abstracts
        WHERE pmid = ?
    """, (pmid,)).fetchone()

    if abstract is None:
        conn.close()
        return jsonify({
            "error": "Abstract not found"
        }), 404

    abstract_id = abstract["id"]

    # Get entities
    entities = conn.execute("""
        SELECT
            entity_text,
            entity_type,
            assertion,
            start_pos,
            end_pos
        FROM entities
        WHERE abstract_id = ?
    """, (abstract_id,)).fetchall()

    # Get relations
    relations = conn.execute("""
        SELECT
            source_entity,
            relation_type,
            target_entity
        FROM relations
        WHERE abstract_id = ?
    """, (abstract_id,)).fetchall()

    conn.close()

    return jsonify({
        "pmid": abstract["pmid"],
        "abstract": abstract["abstract"],
        "entities": [dict(row) for row in entities],
        "relations": [dict(row) for row in relations]
    })


# ==========================================
# 3. ANALYZE NEW ABSTRACT
# ==========================================

@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({
            "error": "Please provide abstract text"
        }), 400

    text = data["text"]

    if not text.strip():
        return jsonify({
            "error": "Abstract text cannot be empty"
        }), 400

    result = run_pipeline(text)

    return jsonify(result)


# ==========================================
# 4. DATABASE STATISTICS
# ==========================================

@app.route("/api/stats", methods=["GET"])
def get_stats():

    conn = get_db_connection()

    total_abstracts = conn.execute("""
        SELECT COUNT(*) FROM abstracts
    """).fetchone()[0]

    total_entities = conn.execute("""
        SELECT COUNT(*) FROM entities
    """).fetchone()[0]

    total_relations = conn.execute("""
        SELECT COUNT(*) FROM relations
    """).fetchone()[0]

    disease_count = conn.execute("""
        SELECT COUNT(*)
        FROM entities
        WHERE entity_type = 'DISEASE'
    """).fetchone()[0]

    intervention_count = conn.execute("""
        SELECT COUNT(*)
        FROM entities
        WHERE entity_type = 'INTERVENTION'
    """).fetchone()[0]

    endpoint_count = conn.execute("""
        SELECT COUNT(*)
        FROM entities
        WHERE entity_type = 'ENDPOINT'
    """).fetchone()[0]

    sample_size_count = conn.execute("""
        SELECT COUNT(*)
        FROM entities
        WHERE entity_type = 'SAMPLE_SIZE'
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "total_abstracts": total_abstracts,
        "total_entities": total_entities,
        "total_relations": total_relations,
        "diseases": disease_count,
        "interventions": intervention_count,
        "endpoints": endpoint_count,
        "sample_sizes": sample_size_count
    })


# ==========================================
# RUN FLASK SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)