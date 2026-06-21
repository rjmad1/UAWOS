from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style"]:
            self.in_script_or_style = True

    def handle_endtag(self, tag):
        if tag in ["script", "style"]:
            self.in_script_or_style = False

    def handle_data(self, data):
        if not self.in_script_or_style:
            self.result.append(data)

    def get_text(self):
        full_text = "".join(self.result)
        # Clean up whitespace
        lines = (line.strip() for line in full_text.splitlines())
        cleaned_text = "\n".join(line for line in lines if line)
        return cleaned_text


def clean_html(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    parser = HTMLTextExtractor()
    parser.feed(content)
    return parser.get_text()


print("--- WEAVEROUTER TEXT ---")
try:
    print(
        clean_html(
            r"C:\Users\rajaj\.gemini\antigravity-ide\brain\331bcea9-3f14-4e37-b032-749cd7984dc9\.system_generated\steps\25\content.md"
        )
    )
except Exception as e:
    print("Error reading Weaverouter:", e)

print("\n\n--- FREELLMAPI TEXT ---")
try:
    print(
        clean_html(
            r"C:\Users\rajaj\.gemini\antigravity-ide\brain\331bcea9-3f14-4e37-b032-749cd7984dc9\.system_generated\steps\29\content.md"
        )
    )
except Exception as e:
    print("Error reading FreeLLMAPI:", e)
