import os
import time
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import urllib.parse
import httpx

class PubMedAPIError(Exception):
    """Base exception for PubMed API failures."""
    pass

class PubMedRateLimitError(PubMedAPIError):
    """Raised when NCBI rate limits are hit (429 / 503 / throttling)."""
    pass

class PubMedClient:
    """
    Client for NCBI E-utilities API (ESearch + EFetch) with automatic rate throttling
    and text normalization.
    """
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("NCBI_API_KEY")
        # NCBI limits: 3 req/sec unauthenticated, 10 req/sec with API key
        self.min_interval = 0.11 if self.api_key else 0.35
        self.last_request_time = 0.0

    def _throttle(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def search(self, query: str, max_results: int = 10) -> List[str]:
        """
        Runs ESearch query to get matching PMIDs.
        """
        self._throttle()
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(max_results)
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.ESEARCH_URL, params=params)

                if response.status_code == 429:
                    raise PubMedRateLimitError("NCBI API Rate Limit exceeded (HTTP 429). Please wait before retrying.")
                elif response.status_code != 200:
                    raise PubMedAPIError(f"PubMed ESearch failed with status HTTP {response.status_code}")

                data = response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                return id_list
        except httpx.TimeoutException:
            raise PubMedAPIError("PubMed API request timed out. Please check network connection.")
        except httpx.RequestError as exc:
            raise PubMedAPIError(f"PubMed network request failed: {str(exc)}")

    def fetch_abstracts(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Runs EFetch for a list of PMIDs and returns parsed abstract dicts.
        """
        if not pmids:
            return []

        self._throttle()
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(self.EFETCH_URL, params=params)

                if response.status_code == 429:
                    raise PubMedRateLimitError("NCBI API Rate Limit exceeded (HTTP 429). Please wait before retrying.")
                elif response.status_code != 200:
                    raise PubMedAPIError(f"PubMed EFetch failed with status HTTP {response.status_code}")

                return self._parse_xml_abstracts(response.text)
        except httpx.TimeoutException:
            raise PubMedAPIError("PubMed API request timed out during EFetch.")
        except httpx.RequestError as exc:
            raise PubMedAPIError(f"PubMed EFetch network request failed: {str(exc)}")

    def normalize_text(self, text: str) -> str:
        """
        Normalizes abstract text by removing XML/HTML tags and cleaning spaces.
        """
        if not text:
            return ""
        # Strip HTML/XML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Collapse multiple spaces/newlines
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _parse_xml_abstracts(self, xml_content: str) -> List[Dict[str, Any]]:
        abstracts = []
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            raise PubMedAPIError("Failed to parse PubMed XML response.")

        for article in root.findall(".//PubmedArticle"):
            pmid_elem = article.find(".//MedlineCitation/PMID")
            if pmid_elem is None or not pmid_elem.text:
                continue
            pmid = pmid_elem.text.strip()

            title_elem = article.find(".//ArticleTitle")
            title = "".join(title_elem.itertext()).strip() if title_elem is not None else "No Title"
            title = self.normalize_text(title)

            # Abstract text can have multiple AbstractText elements (BACKGROUND, METHODS, RESULTS, etc.)
            abstract_elems = article.findall(".//Abstract/AbstractText")
            abstract_parts = []
            for a_elem in abstract_elems:
                label = a_elem.get("Label")
                a_text = "".join(a_elem.itertext()).strip()
                if label and label.upper() not in ("UNLABELLED", "UNASSIGNED"):
                    abstract_parts.append(f"{label}: {a_text}")
                else:
                    abstract_parts.append(a_text)

            raw_abstract_text = " ".join(abstract_parts) if abstract_parts else "No abstract text available."
            normalized_text = self.normalize_text(raw_abstract_text)

            abstracts.append({
                "abstract_id": pmid,
                "title": title,
                "raw_text": raw_abstract_text,
                "normalized_text": normalized_text
            })

        return abstracts
