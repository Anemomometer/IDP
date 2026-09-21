from pipeline import run_pipeline
from database import save_result


text = """
A randomized clinical trial evaluated Metformin in 350 patients
with type 2 diabetes. The study measured HbA1c and blood glucose
levels after 24 weeks of treatment.
"""

pmid = "TEST001"

# Run NLP pipeline
result = run_pipeline(text)

# Save results to database
save_result(
    pmid,
    text,
    result["entities"],
    result["relations"]
)

print("\nData inserted into SQLite successfully!")