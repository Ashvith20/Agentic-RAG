
import json
import re
import os

# Input and output paths
INPUT_FILE = "data/raw/gainwell_text.json"
OUTPUT_JSONL = "data/processed/gainwell_clean.jsonl"
OUTPUT_TXT = "data/processed/gainwell_clean.txt"

# Make sure output directory exists
os.makedirs(os.path.dirname(OUTPUT_JSONL), exist_ok=True)

def clean_text(text):
    """Basic cleaning for Gainwell website text."""
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace/newlines
    text = re.sub(r'Medicaid Enterprise \| Gainwell', '', text)
    text = re.sub(r'Gainwell Technologies', '', text)
    text = re.sub(r'Language [A-Za-z()\s]+', '', text)
    return text.strip()

# Open both files for writing
with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_JSONL, "w", encoding="utf-8") as jsonl_out, \
     open(OUTPUT_TXT, "w", encoding="utf-8") as txt_out:

    data = json.load(infile)
    for i, doc in enumerate(data):
        cleaned = clean_text(doc["text"])

        # --- Write JSONL line ---
        json_line = json.dumps({"url": doc["url"], "text": cleaned})
        jsonl_out.write(json_line + "\n")

        # --- Write human-readable text ---
        txt_out.write(f"[Document {i+1}] {doc['url']}\n")
        txt_out.write(cleaned + "\n\n" + "="*100 + "\n\n")

print(f" Cleaned data saved to:\n - {OUTPUT_JSONL}\n - {OUTPUT_TXT}")

