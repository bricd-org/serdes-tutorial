#!/usr/bin/env python3
"""Insert the interactive demos (_includes/demos/NAME.html) into the generated chapter pages.

The pages are regenerated from the LaTeX by build_site.py, which calls this at the end, so the
demos survive every rebuild. Run it by hand after adding a demo:  python3 tools/insert_demos.py

Each entry: (page file under ROOT, demo name, anchor). The anchor is either
  "after:fig:ID"  -> just after the </figure> that follows <div id="fig:ID">
  "end:sec:ID"    -> just before the next <h2>/<h3> after the heading with id sec:ID
The script removes old <!-- demo:... --> blocks first, so it is idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CH = "chapters/"

DEMOS = [
    (CH + "02-signals-systems-and-the-language-of-links.html", "nrzpsd", "after:fig:ch2-psd"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "isieye", "after:fig:ch2-isi-tau"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "berq", "after:fig:ch2-ber"),
    (CH + "03-the-channel.html", "bounce", "after:fig:ch3-bounce"),
    (CH + "11-jitter.html", "bathtub", "after:fig:ch11-bathtub"),
]

BLOCK = re.compile(r"\n?<!-- demo:[\w-]+ -->.*?<!-- /demo -->\n?", re.S)


def insert(html, name, anchor):
    kind, ident = anchor.split(":", 1)
    if kind == "after":
        m = re.search(r'<div id="%s">' % re.escape(ident), html)
        if not m:
            raise ValueError(f"no figure {ident}")
        pos = html.index("</figure>", m.end()) + len("</figure>")
    elif kind == "end":
        m = re.search(r'<h[23] id="%s">' % re.escape(ident), html)
        if not m:
            raise ValueError(f"no section {ident}")
        nxt = re.compile(r"<h[23] |<nav class=\"prev-next\"").search(html, m.end())
        pos = nxt.start() if nxt else len(html)
    else:
        raise ValueError(f"bad anchor {anchor}")
    block = ("\n<!-- demo:%s -->{%% endraw %%}{%% include demos/%s.html %%}{%% raw %%}<!-- /demo -->\n"
             % (name, name))
    return html[:pos] + block + html[pos:]


def main():
    errors = 0
    pages = {}
    for page, name, anchor in DEMOS:
        if not (ROOT / "_includes" / "demos" / f"{name}.html").exists():
            print(f"missing include for {name}", file=sys.stderr); errors += 1; continue
        pages.setdefault(page, []).append((name, anchor))
    for page, items in pages.items():
        path = ROOT / page
        html = BLOCK.sub("", path.read_text())
        for name, anchor in items:
            try:
                html = insert(html, name, anchor)
            except ValueError as e:
                print(f"{page}: {e}", file=sys.stderr); errors += 1
        path.write_text(html)
        print(f"{page}: {len(items)} demo(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
