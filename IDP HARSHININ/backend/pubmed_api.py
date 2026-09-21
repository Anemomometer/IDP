import requests
import json
import os
import xml.etree.ElementTree as ET


# ---------------------------------------------------------
# NCBI E-utilities URLs
# ---------------------------------------------------------

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


# ---------------------------------------------------------
# Where we will save Batch 2 abstracts
# ---------------------------------------------------------

OUTPUT_FILE = os.path.join(
    "data",
    "pubmed_abstracts_batch2.json"
)


# ---------------------------------------------------------
# NCBI application information
# ---------------------------------------------------------

TOOL_NAME = "ClinicalTrialNLP"
EMAIL = "koneharshini2025@vitstudent.ac.in"


# ---------------------------------------------------------
# Search PubMed
# ---------------------------------------------------------

def search_pubmed(query, max_results=20):

    print("\nSearching PubMed...")
    print("Query:", query)

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "tool": TOOL_NAME,
        "email": EMAIL
    }

    response = requests.get(
        ESEARCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    pmids = data["esearchresult"]["idlist"]

    print(f"Found {len(pmids)} PubMed articles.")

    return pmids


# ---------------------------------------------------------
# Fetch abstracts
# ---------------------------------------------------------

def fetch_abstracts(pmids):

    if not pmids:
        return []

    print("\nFetching abstracts...")

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "tool": TOOL_NAME,
        "email": EMAIL
    }

    response = requests.get(
        EFETCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    articles = []

    for article in root.findall(".//PubmedArticle"):

        pmid_element = article.find(".//PMID")

        if pmid_element is None:
            continue

        pmid = pmid_element.text

        # Collect all abstract sections
        abstract_parts = []

        for abstract_text in article.findall(
            ".//Abstract/AbstractText"
        ):

            if abstract_text.text:

                abstract_parts.append(
                    abstract_text.text
                )

        # Skip articles without an abstract
        if not abstract_parts:
            continue

        abstract = " ".join(abstract_parts)

        articles.append({
            "pmid": pmid,
            "text": abstract
        })

    print(f"Retrieved {len(articles)} abstracts.")

    return articles


# ---------------------------------------------------------
# Save abstracts
# ---------------------------------------------------------

def save_abstracts(articles):

    # Make sure data folder exists
    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            articles,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nSaved abstracts to:")
    print(OUTPUT_FILE)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    # We collect more clinical trials related to diabetes.
    query = (
        "clinical trial[Publication Type] "
        "AND diabetes"
    )

    pmids = search_pubmed(
        query,
        max_results=20
    )

    articles = fetch_abstracts(pmids)

    save_abstracts(articles)


# ---------------------------------------------------------
# Run program
# ---------------------------------------------------------

if __name__ == "__main__":
    main()