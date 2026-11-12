import re, sys
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"-\s*\n\s*", "", s)          # hyphen at line end
    return re.sub(r"\s+", " ", s).lower()
def find(path, phrase, ctx=260):
    pages = open(path, encoding="utf-8", errors="replace").read().split("\f")
    p = norm(phrase); hits = []
    for i, pg in enumerate(pages, 1):
        t = norm(pg); j = t.find(p)
        while j >= 0:
            hits.append((i, t[max(0, j - ctx): j + len(p) + ctx])); j = t.find(p, j + 1)
    return hits
if __name__ == "__main__":
    path = sys.argv[1]
    for phrase in sys.argv[2:]:
        h = find(path, phrase)
        print(f"=== {phrase!r}: {len(h)} hit(s)")
        for pg, c in h[:3]:
            print(f"  p.{pg}: ...{c}...")
