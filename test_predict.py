"""Send two example requests to a running service.

Start the service first:
    uv run uvicorn predict:app --host 0.0.0.0 --port 9696
Then:
    uv run python test_predict.py            # local
    uv run python test_predict.py <base-url> # deployed service
"""

import sys

import requests

base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:9696"

# Two real rows from the dataset, one of each class
phishing_example = {
    "having_ip_address": -1, "url_length": 1, "shortining_service": 1,
    "having_at_symbol": 1, "double_slash_redirecting": -1, "prefix_suffix": -1,
    "having_sub_domain": -1, "sslfinal_state": -1, "domain_registeration_length": -1,
    "favicon": 1, "port": 1, "https_token": -1, "request_url": 1, "url_of_anchor": -1,
    "links_in_tags": 1, "sfh": -1, "submitting_to_email": -1, "abnormal_url": -1,
    "redirect": 0, "on_mouseover": 1, "rightclick": 1, "popupwidnow": 1, "iframe": 1,
    "age_of_domain": -1, "dnsrecord": -1, "web_traffic": -1, "page_rank": -1,
    "google_index": 1, "links_pointing_to_page": 1, "statistical_report": -1,
}

legitimate_example = {
    "having_ip_address": 1, "url_length": 0, "shortining_service": -1,
    "having_at_symbol": 1, "double_slash_redirecting": 1, "prefix_suffix": -1,
    "having_sub_domain": 1, "sslfinal_state": 1, "domain_registeration_length": -1,
    "favicon": 1, "port": 1, "https_token": 1, "request_url": 1, "url_of_anchor": 0,
    "links_in_tags": 0, "sfh": -1, "submitting_to_email": 1, "abnormal_url": 1,
    "redirect": 0, "on_mouseover": -1, "rightclick": 1, "popupwidnow": -1, "iframe": 1,
    "age_of_domain": -1, "dnsrecord": -1, "web_traffic": 0, "page_rank": -1,
    "google_index": 1, "links_pointing_to_page": 1, "statistical_report": 1,
}

print("health:", requests.get(f"{base_url}/health").json())

for name, example in [("phishing", phishing_example), ("legitimate", legitimate_example)]:
    response = requests.post(f"{base_url}/predict", json=example)
    print(f"{name} example ->", response.json())
