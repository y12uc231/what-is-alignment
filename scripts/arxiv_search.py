"""arXiv API helper (export.arxiv.org, ~3 s between calls).

  python3 -I arxiv_search.py count 'QUERY' FROM TO      -> total hits (dates YYYYMMDD)
  python3 -I arxiv_search.py search 'QUERY' [N] [FROM TO] -> jsonl: id, date, title, comment, authors
QUERY uses arXiv syntax, e.g. 'abs:"reward hacking" AND cat:cs.LG'.
"""
import json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/", "x": "http://arxiv.org/schemas/atom"}

def call(params):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "survey-metadata/0.1 (research)"})
            data = urllib.request.urlopen(req, timeout=60).read()
            time.sleep(3)
            return ET.fromstring(data)
        except Exception:  # noqa: BLE001
            time.sleep(5 + 5 * attempt)
    raise RuntimeError("arXiv API failed")

def q_with_dates(q, a, b):
    return f"({q}) AND submittedDate:[{a}0000 TO {b}2359]" if a else q

def count(q, a, b):
    root = call({"search_query": q_with_dates(q, a, b), "max_results": 1})
    return int(root.find("o:totalResults", NS).text)

def search(q, n=100, a=None, b=None):
    out, start = [], 0
    while start < n:
        root = call({"search_query": q_with_dates(q, a, b), "start": start, "max_results": min(100, n - start),
                     "sortBy": "relevance"})
        ents = root.findall("a:entry", NS)
        if not ents:
            break
        for e in ents:
            aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.rsplit("/abs/", 1)[-1])
            c = e.find("x:comment", NS)
            out.append({"id": aid, "date": e.find("a:published", NS).text[:10],
                        "title": " ".join(e.find("a:title", NS).text.split()),
                        "comment": " ".join(c.text.split()) if c is not None and c.text else "",
                        "authors": [x.find("a:name", NS).text for x in e.findall("a:author", NS)][:8]})
        start += len(ents)
    return out

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "count":
        print(count(sys.argv[2], sys.argv[3], sys.argv[4]))
    else:
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        a, b = (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else (None, None)
        for r in search(sys.argv[2], n, a, b):
            print(json.dumps(r))
