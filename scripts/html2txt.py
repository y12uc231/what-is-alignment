"""Convert saved arXiv HTML (or other HTML) to plain text with '## ' section markers.

Usage: python3 -I scripts/html2txt.py IN.html OUT.txt
"""

import re
import sys
from html.parser import HTMLParser

SKIP = {"script", "style", "nav", "header", "footer", "math", "annotation", "svg"}
HEADINGS = {"h1", "h2", "h3", "h4"}
BLOCKS = {"p", "div", "li", "tr", "br", "section", "figcaption", "table", "blockquote"} | HEADINGS


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.head = [], 0, False

    def handle_starttag(self, tag, attrs):
        # MathML is dropped; existing reads were verified against text built this way.
        if tag in SKIP:
            self.skip += 1
            return
        if tag in HEADINGS:
            self.out.append("\n\n## ")
            self.head = True
        elif tag in BLOCKS:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag in HEADINGS:
            self.out.append("\n")
            self.head = False
        elif tag in BLOCKS:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def convert(html):
    p = Extract()
    p.feed(html)
    text = "".join(p.out)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip() + "\n"


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8", errors="replace") as f:
        html = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(convert(html))
