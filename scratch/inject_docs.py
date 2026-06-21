import os
import json
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT_DIR, "operations_dashboard.html")
JSON_FILE = os.path.join(ROOT_DIR, "scratch", "all_docs.json")

def inject():
    # 1. Load documents from JSON file
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found. Run scan_docs.py first.")
        return
        
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)
        
    print(f"Loaded {len(documents)} documents to inject.")
    
    # Format document list to pretty javascript indentation
    docs_js = json.dumps(documents, indent=8, ensure_ascii=False)
    # Adjust indentation to match the file's style
    docs_js = docs_js.rstrip("]") + "      ]"
    
    # 2. Read operations_dashboard.html
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # 3. Locate the "documents": [ ... ] block
    # We match "documents": [ followed by anything up to the ending ] of that array
    pattern = r'("documents":\s*\[)(.*?)(\]\s*)(?=\r?\n\s*\};)'
    
    # Since the array contains nested objects, a simple non-greedy match might stop too early if not careful.
    # To be extremely safe, we find where '"documents": [' starts, and trace the matching brackets, or we can use a regex that matches '"documents": \[[^\]]*\]' if we know there are no nested brackets, or since the documents JSON contains no brackets inside its strings (only curly braces), we can match up to the closing square bracket followed by a newline and the closing bracket of DEFAULT_CONFIG (e.g. \r?\n\s*\};).
    # Let's inspect the target file structure around those lines:
    # 1317:       ]
    # 1318:     };
    # So the pattern is: "documents": [ followed by elements and then a closing bracket ] followed by a newline and };
    
    match = re.search(r'"documents":\s*\[.*?\n\s*\](?=\s*\r?\n\s*\};)', html_content, re.DOTALL)
    if not match:
        print("Error: Could not find 'documents' config array in HTML file.")
        return
        
    old_block = match.group(0)
    new_block = f'"documents": {docs_js}'
    
    updated_html = html_content.replace(old_block, new_block)
    
    # 4. Save operations_dashboard.html
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)
        
    print(f"Successfully injected documentation database into {HTML_FILE}.")

if __name__ == "__main__":
    inject()
