import re
import json

def inspect_file(file_path, out_file):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    out_file.write(f"=== INSPECTION OF {file_path} ===\n")
    out_file.write(f"Length: {len(content)} characters\n")
    
    # Let's find any text blocks, scripts, or json data
    # Let's find all script tags
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    out_file.write(f"Number of script tags: {len(scripts)}\n")
    
    # Print the first 500 chars of each script tag to find which one contains data
    for i, s in enumerate(scripts):
        s_clean = s.strip()
        if len(s_clean) > 0:
            out_file.write(f"Script {i} (len={len(s_clean)}): {s_clean[:300]}...\n\n")

    # Let's search for some text patterns, like "70%" or "router" or "ONNX"
    matches = re.findall(r'[^<>]{10,200}', content)
    out_file.write(f"Sample text matches (out of {len(matches)}):\n")
    for m in matches[:100]:
        m_clean = m.strip()
        if m_clean:
            out_file.write(f"- {m_clean}\n")

with open("scratch/inspection_output.txt", "w", encoding="utf-8") as out:
    inspect_file(r"C:\Users\rajaj\.gemini\antigravity-ide\brain\331bcea9-3f14-4e37-b032-749cd7984dc9\.system_generated\steps\25\content.md", out)
    out.write("\n\n" + "="*40 + "\n\n")
    inspect_file(r"C:\Users\rajaj\.gemini\antigravity-ide\brain\331bcea9-3f14-4e37-b032-749cd7984dc9\.system_generated\steps\29\content.md", out)

print("Inspection complete. Saved to scratch/inspection_output.txt")
