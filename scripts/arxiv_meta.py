"""Fetch verified metadata for arXiv ids from arxiv.org/abs meta tags (~1 req/s).

Usage: python3 -I scripts/arxiv_meta.py ID [ID ...]   -> one JSON object per line on stdout
Fields: id, title, date (YYYY-MM-DD of v1 as listed), authors, abstract, comment (venue hints), ok.
"""
import html, json, re, sys, time, urllib.request

def meta(page, name):
    return [html.unescape(m) for m in re.findall(r'<meta name="%s" content="(.*?)"\s*/?>' % name, page, re.S)]

def fetch(aid):
    url = f"https://arxiv.org/abs/{aid}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "survey-metadata/0.1 (research)"})
            page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            break
        except Exception as e:  # noqa: BLE001
            err = str(e); time.sleep(3 + 3 * attempt)
    else:
        return {"id": aid, "ok": False, "error": err}
    title = (meta(page, "citation_title") or [""])[0]
    date = (meta(page, "citation_date") or meta(page, "citation_online_date") or [""])[0].replace("/", "-")
    m = re.search(r'<td class="tablecell comments[^"]*">(.*?)</td>', page, re.S)
    comment = re.sub(r"<[^>]+>", "", html.unescape(m.group(1))).strip() if m else ""
    return {"id": aid, "ok": bool(title), "title": re.sub(r"\s+", " ", title).strip(), "date": date,
            "authors": meta(page, "citation_author"), "abstract": re.sub(r"\s+", " ", (meta(page, "citation_abstract") or [""])[0]).strip(),
            "comment": comment}

if __name__ == "__main__":
    for i, aid in enumerate(sys.argv[1:]):
        if i:
            time.sleep(1.0)
        print(json.dumps(fetch(re.sub(r"v\d+$", "", aid.strip()))), flush=True)
