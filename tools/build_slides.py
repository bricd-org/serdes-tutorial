#!/usr/bin/env python3
"""build_slides.py -- regenerate the 'Intro Slides' gallery page from the exported deck.

Inputs
  assets/pdf/Open-SERDES_Intro_Slides.pdf   the Google Slides deck, exported as PDF
                                            (File > Download > PDF document)
  tools/slides_notes.json                   slide titles, speaker notes, related chapters

Outputs
  assets/slides/slide-NN.png                one 1600 px image per slide (256-colour PNG)
  slides.md                                 the gallery page (/slides/)

Usage (from the repository root):  python3 tools/build_slides.py
Requires poppler-utils (pdftoppm) and Pillow.
"""
import html, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "assets" / "pdf" / "Open-SERDES_Intro_Slides.pdf"
OUT = ROOT / "assets" / "slides"


def render():
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("slide-*.png"):
        f.unlink()
    subprocess.run(["pdftoppm", "-r", "160", "-png", str(PDF), str(OUT / "slide")], check=True)
    files = sorted(OUT.glob("slide-*.png"))
    for f in files:
        im = Image.open(f).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(f, optimize=True)
    return files


def page(meta, files):
    slides = meta["slides"]
    if len(slides) != len(files):
        sys.exit(f"{len(files)} slides in the PDF but {len(slides)} in slides_notes.json")
    url = lambda p: "{{ '%s' | relative_url }}" % p
    parts = ['---', 'title: "Intro Slides"', 'layout: default', 'nav_order: 9', 'permalink: /slides/', '---', '',
             '<div class="slides-intro" markdown="0">',
             '<p class="part-label">Open-SERDES introduction talk</p>',
             '<h1>Intro Slides</h1>',
             '<p class="part-blurb">The talk that introduces Open-SERDES: why an open serial link, why IHP SG13G2, '
             'the anatomy of the link, the open channel-to-GDS flow, what we will build and test, and the roadmap. '
             'Speaker notes sit under each slide; the tutorial chapter that goes deeper is linked where there is one.</p>',
             '<p><a class="btn btn-primary mr-2" href="%s">Download the slides (PDF)</a>'
             '<a class="btn" href="%s">Read the tutorial</a></p>' % (url("/assets/pdf/Open-SERDES_Intro_Slides.pdf"),
                                                                     url("/preface/")),
             '<nav class="slide-index" aria-label="Slides">']
    parts += ['<a href="#slide-%d"><b>%d</b> %s</a>' % (s["n"], s["n"], html.escape(s["title"])) for s in slides]
    parts += ['</nav>', '</div>', '']
    for s, f in zip(slides, files):
        n, t = s["n"], html.escape(s["title"])
        parts.append('<figure class="slide" id="slide-%d" markdown="0">' % n)
        parts.append('<img src="%s" alt="Slide %d: %s" loading="lazy" width="1600" height="900">' %
                     (url("/assets/slides/" + f.name), n, t))
        cap = '<span class="capnum">Slide %d.</span> %s' % (n, t)
        if s.get("related"):
            cap += ' <a class="slide-related" href="%s">%s →</a>' % (url(s["related"]["url"].split("#")[0]) +
                   ("#" + s["related"]["url"].split("#")[1] if "#" in s["related"]["url"] else ""),
                   html.escape(s["related"]["label"]))
        parts.append('<figcaption>%s</figcaption>' % cap)
        parts.append('</figure>')
        if s.get("notes"):
            parts.append('<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>')
            for para in s["notes"].split("\n"):
                if para.strip():
                    parts.append('<p>%s</p>' % html.escape(para.strip()))
            parts.append('</details>')
        parts.append('')
    (ROOT / "slides.md").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    meta = json.loads((ROOT / "tools" / "slides_notes.json").read_text())
    files = render()
    page(meta, files)
    print(f"slides.md: {len(files)} slides")
