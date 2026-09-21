import json
import sqlite3

from pipeline import run_pipeline
from database import save_result

DATABASE = "data/clinical_trials.db"
DATA_FILE = "data/combined_annotations_unique.json"


def main():

    # Load annotated abstracts
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("================================")
    print("POPULATING SQLITE DATABASE")
    print("================================")

    print("\nTotal abstracts:", len(data))

    for i, item in enumerate(data, start=1):

        pmid = item["pmid"]
        text = item["text"]

        print(f"\nProcessing {i}/{len(data)} - PMID: {pmid}")

        # Run our NLP pipeline
        result = run_pipeline(text)

        # Save NLP results
        save_result(
            pmid,
            text,
            result["entities"],
            result["relations"]
        )

    print("\n================================")
    print("DATABASE POPULATION COMPLETE")
    print("================================")


if __name__ == "__main__":
    main()