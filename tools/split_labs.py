#!/usr/bin/env python3
"""Give the hands-on labs (Chapter 16 of the book) their own section of the site.

build_site.py writes Chapter 16 as one page under Part V. This script, which build_site.py runs after writing
the pages and before insert_demos.py, turns it into a top-level "Hands-on Labs" section:
  labs/index.html    /labs/         the chapter's lead and objectives, Table 16.1 with links, "Where to go next"
  labs/lab-N.html    /labs/lab-N/   one page per lab (Lab 0 to Lab 7), children of the section
It rewrites every link into the old page, drops the chapter from the Part V list, and leaves a stub at the old
address that forwards readers, #anchors included, to the new pages. Section, figure and table numbers stay those
of the PDF edition (16.x). If the chapter page is already the stub, it does nothing, so it is safe to run twice.
Run it by hand after editing it:  python3 tools/split_labs.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = "/chapters/16-hands-on-labs-with-serdespy/"
OLD_FILE = ROOT / "chapters" / "16-hands-on-labs-with-serdespy.html"
SECTION = "Hands-on Labs"
NAV_ORDER = 6.5                     # after Part V (nav_order 6), before the Appendices (7)
DEMO_BLOCK = re.compile(r"\n?<!-- demo:[\w-]+ -->.*?<!-- /demo -->\n?", re.S)   # insert_demos.py re-adds them


def liquid_url(path):
    return "{% endraw %}{{ '" + path + "' | relative_url }}{% raw %}"


def front_matter(**kw):
    lines = ["---"]
    for k, v in kw.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(lines + ["---"]) + "\n"


def pn_link(cls, href, title):
    arrow = "← Previous" if cls == "prev" else "Next →"
    return '<a class="pn-link %s" href="%s"><small>%s</small>%s</a>' % (cls, href, arrow, title)


def nav_footer(prev, nxt, source):
    return ('\n<nav class="prev-next" aria-label="Chapter navigation">%s%s</nav>\n%s\n' % (prev, nxt, source))


def main():
    txt = OLD_FILE.read_text()
    if '<h2 id="sec:lab0"' not in txt:
        print("split_labs: the labs are already split")
        return 0
    body = txt[txt.index("\n---\n", 4) + 5:]
    body = body.removeprefix("{% raw %}\n").rstrip().removesuffix("{% endraw %}")
    nav_at = body.index('<nav class="prev-next"')
    content, tail = DEMO_BLOCK.sub("\n", body[:nav_at]), body[nav_at:]
    source = re.search(r'<p class="page-source">.*?</p>', tail, re.S).group(0)
    old_prev = re.search(r'<a class="pn-link prev".*?</a>', tail, re.S).group(0)      # Chapter 15
    old_next = re.search(r'<a class="pn-link next".*?</a>', tail, re.S).group(0)      # Appendix A

    # ---- cut the chapter at its sections: intro, Lab 0..7, "Where to go next"
    cuts = [m.start() for m in re.finditer(r'<h2 id="sec:(?:lab\d+|ch16-next)"', content)]
    intro, chunks, wrapup = content[:cuts[0]], [content[a:b] for a, b in zip(cuts, cuts[1:])], content[cuts[-1]:]
    assert wrapup.startswith('<h2 id="sec:ch16-next"'), "the chapter no longer ends with 'Where to go next'"

    m = re.match(r'\s*<h1 id="ch:labs"><span class="chapnum">[^<]*</span>(.*?)</h1>\s*'
                 r'<div class="chapterlead">\s*<p>(.*?)</p>\s*</div>', intro, re.S)
    chap_title, lead, intro_rest = m.group(1), m.group(2), intro[m.end():]
    intro_rest = intro_rest.replace("In this chapter you will learn", "In these labs you will learn")

    labs = []
    for chunk in chunks:
        m = re.match(r'<h2 id="sec:lab(\d+)"><span class="secnum">([^<]*)</span>Lab \1: (.*?)</h2>', chunk)
        n, secnum, t = int(m.group(1)), m.group(2), m.group(3)
        labs.append(dict(n=n, secnum=secnum, title=t[0].upper() + t[1:], short=t, body=chunk[m.end():],
                         permalink=f"/labs/lab-{n}/", file=f"lab-{n}.html"))
    assert [l["n"] for l in labs] == list(range(len(labs))), "labs are not numbered 0, 1, 2, ..."

    # ---- Table 16.1 moves from Lab 0 to the section page, with a linked title column
    tab = re.compile(r'<div id="tab:ch16-labs">\s*</div>\s*<div>\s*<table>.*?</table>\s*</div>', re.S)
    table = tab.search(labs[0]["body"]).group(0)
    labs[0]["body"] = tab.sub("", labs[0]["body"])
    table = table.replace('<th style="text-align: center;"><strong>Lab</strong></th>',
                          '<th style="text-align: center;"><strong>Lab</strong></th>\n'
                          '<th style="text-align: left;"><strong>Title</strong></th>', 1)
    by_n = {l["n"]: l for l in labs}

    def title_cell(mm):
        lab = by_n[int(mm.group(2))]
        return (mm.group(1) + '\n<td style="text-align: left;"><a href="%s">%s</a></td>'
                % (liquid_url(lab["permalink"]), lab["title"]))
    table = re.sub(r'(<tr class="(?:odd|even)">\s*<td style="text-align: center;">(\d+)</td>)', title_cell, table)

    # ---- the pages
    sec_link = pn_link("prev", liquid_url("/labs/"), SECTION)
    pages = []
    index_html = (
        '<p class="part-label">Labs</p>\n'
        f'<h1 id="ch:labs" class="part-title">{chap_title}</h1>\n'
        f'<p class="part-blurb">{lead}</p>\n'
        f'{intro_rest.strip()}\n'
        f'<p>Start with <a href="{liquid_url(labs[0]["permalink"])}">Lab 0: {labs[0]["short"]}</a>, which sets up '
        'serdespy and introduces the shared helpers in <code>common.py</code>. Then work down the table, or open the '
        'lab that goes with the chapter you are reading. In the PDF edition the labs are Chapter 16, so their '
        'section, figure and table numbers start with 16.</p>\n'
        f'{table}\n{wrapup.strip()}\n')
    pages.append(dict(permalink="/labs/", file="index.html", html=index_html,
                      prev=old_prev, next=pn_link("next", liquid_url(labs[0]["permalink"]),
                                                   f'Lab 0. {labs[0]["title"]}'),
                      fm=front_matter(title=SECTION, nav_order=NAV_ORDER, has_children=True, has_toc=False,
                                      permalink="/labs/")))
    for i, lab in enumerate(labs):
        h = (f'<h1 id="sec:lab{lab["n"]}"><span class="chapnum">Lab {lab["n"]} · Section {lab["secnum"]}</span>'
             f'{lab["title"]}</h1>\n{lab["body"].strip()}\n')
        prev = sec_link if i == 0 else pn_link("prev", liquid_url(labs[i - 1]["permalink"]),
                                               f'Lab {labs[i - 1]["n"]}. {labs[i - 1]["title"]}')
        nxt = old_next if i == len(labs) - 1 else pn_link("next", liquid_url(labs[i + 1]["permalink"]),
                                                          f'Lab {labs[i + 1]["n"]}. {labs[i + 1]["title"]}')
        pages.append(dict(permalink=lab["permalink"], file=lab["file"], html=h, prev=prev, next=nxt,
                          fm=front_matter(title=f'Lab {lab["n"]}. {lab["title"]}', parent=SECTION,
                                          nav_order=lab["n"], permalink=lab["permalink"])))

    # ---- where each id now lives; fix in-page links that crossed a split
    idmap = {}
    for p in pages:
        for ident in re.findall(r' id="([^"]+)"', p["html"]):
            idmap.setdefault(ident, p["permalink"])

    def local(p):
        own = set(re.findall(r' id="([^"]+)"', p["html"]))

        def fix(mm):
            ident = mm.group(1)
            if ident in own or ident not in idmap:
                return mm.group(0)
            return 'href="%s#%s"' % (liquid_url(idmap[ident]), ident)
        return fix

    out = ROOT / "labs"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for p in pages:
        html = re.sub(r'href="#([^"]+)"', local(p), p["html"])
        (out / p["file"]).write_text(p["fm"] + "{% raw %}\n" + html + nav_footer(p["prev"], p["next"], source)
                                     + "{% endraw %}\n")

    # ---- links from the rest of the site
    pn_old = re.compile(r'<a class="pn-link (prev|next)" href="\{% endraw %\}\{\{ \'' + re.escape(OLD)
                        + r'\' \| relative_url \}\}\{% raw %\}"><small>[^<]*</small>[^<]*</a>')
    last = labs[-1]

    def pn_fix(mm):
        if mm.group(1) == "next":         # Chapter 15 -> the section page
            return pn_link("next", liquid_url("/labs/"), SECTION)
        return pn_link("prev", liquid_url(last["permalink"]), f'Lab {last["n"]}. {last["title"]}')  # Appendix A
    link_old = re.compile(r"\{\{ '" + re.escape(OLD) + r"' \| relative_url \}\}(\{% raw %\})?(#[^\"'\s)<]+)?")

    def link_fix(mm):
        raw, anchor = mm.group(1) or "", mm.group(2) or ""
        target = idmap.get(anchor[1:], "/labs/") if anchor else "/labs/"
        if anchor == "#ch:labs":
            anchor = ""
        return "{{ '%s' | relative_url }}%s%s" % (target, raw, anchor)
    files = [*ROOT.glob("chapters/*.html"), *ROOT.glob("appendices/*.html"), ROOT / "preface.html",
             ROOT / "references.html", *ROOT.glob("parts/*.md")]
    changed = 0
    for f in files:
        if f == OLD_FILE or not f.exists():
            continue
        t0 = f.read_text()
        t = link_old.sub(link_fix, pn_old.sub(pn_fix, t0))
        if f.parent.name == "parts":      # Part V lists Chapters 14-15 only and points to the section
            line = re.compile(r"^- \[[^\]]*\]\(\{\{ '/labs/' \| relative_url \}\}\)\n?", re.M)
            if line.search(t):
                t = line.sub("", t).rstrip() + (f"\n\nThe hands-on labs have their own section: "
                                                f"[{SECTION}]({{{{ '/labs/' | relative_url }}}}).\n")
        if t != t0:
            f.write_text(t); changed += 1

    # ---- a stub at the old address: forward to the new page, keeping the #anchor
    keep = {k: v.removeprefix("/labs/") for k, v in idmap.items() if re.match(r"(sec|fig|tab|eq|lst|we|ch):", k)}
    OLD_FILE.write_text(
        front_matter(layout="null", permalink=OLD, nav_exclude=True, search_exclude=True).replace('"null"', "null")
        + "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>Hands-on Labs have moved</title>\n<meta name=\"robots\" content=\"noindex\">\n"
        "<link rel=\"canonical\" href=\"{{ '/labs/' | absolute_url }}\">\n"
        "<meta http-equiv=\"refresh\" content=\"0; url={{ '/labs/' | relative_url }}\">\n"
        "<script>\n(function () {\n  var map = " + json.dumps(keep, separators=(",", ":")) + ";\n"
        "  var id = decodeURIComponent(location.hash.slice(1));\n"
        "  location.replace(\"{{ '/labs/' | relative_url }}\" + (map[id] || \"\") + location.hash);\n})();\n</script>\n"
        "</head>\n<body>\n<p>The hands-on labs now have their own section: "
        "<a href=\"{{ '/labs/' | relative_url }}\">Hands-on Labs</a>.</p>\n</body>\n</html>\n")
    print(f"split_labs: labs/ with {len(pages)} pages, {changed} other pages relinked, stub at {OLD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
