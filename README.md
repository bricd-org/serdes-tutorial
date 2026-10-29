# Open-SERDES Tutorial — *Designing a Serial Link from Scratch*

A design tutorial for undergraduate engineers building an open-source 5 Gb/s NRZ SerDes in the
IHP SG13G2 130 nm SiGe BiCMOS open PDK, written for the Open-SERDES project at
[BRICD](https://www.thebricd.org).

**Read it online:** https://www.thebricd.org/serdes-tutorial/
**PDF edition:** [assets/pdf/Open-SERDES_Tutorial.pdf](assets/pdf/Open-SERDES_Tutorial.pdf)

It has 16 chapters in five parts, 135+ figures and seven serdespy labs:

| Part | Chapters |
|---|---|
| I. Foundations | Why serial links? · Signals and systems · The channel · Link budgets and statistical analysis |
| II. Equalization | Fundamentals · TX FFE · CTLE · DFE and adaptation |
| III. Transceiver circuits | The transmitter · RX front-end and samplers |
| IV. Clocking | Jitter · The PLL · Clock and data recovery |
| V. Putting it together | The Open-SERDES architecture · Open-source design flow · Hands-on labs |

## Repository layout

```
book/                 LaTeX source of the book: the same files as the Overleaf project
  tutorial.tex          main file (pdfLaTeX + BibTeX)
  tutorial/chapters/    one .tex file per chapter
  tutorial/figsrc/      Python scripts that draw every plot (house style: bricdstyle.py)
  tutorial/code/        serdespy lab scripts (Chapter 16)
  tutorial/tikzext/     pre-compiled TikZ figures
tools/build_site.py   converts book/ into the website pages below
chapters/ appendices/ parts/ preface.html references.html   generated pages (do not edit by hand)
assets/figs/          generated figures (SVG/PNG)    assets/pdf/   the compiled book and the intro slides
assets/figs/analog/   the analog schematics in the intro slides, copied from open-serdes doc/fig/analog/ (build_site.py leaves them alone)
tools/build_slides.py  rebuilds the Intro Slides page (slides.md, assets/slides/) from the exported deck
_config.yml, _sass/, _includes/   Jekyll + just-the-docs theme settings (BRICD colours and fonts)
.github/workflows/pages.yml       builds the site and deploys it to GitHub Pages
```

## Updating the book and the site

The LaTeX book is the single source of truth. The website pages are generated from it, so
cross-references, figure numbers, equation numbers and citations always match the PDF.

1. Edit the LaTeX in `book/`, or copy the updated files in from Overleaf.
2. Regenerate the site. You need TeX Live, pandoc ≥ 3 and poppler-utils:
   ```bash
   python3 tools/build_site.py          # compiles the book, then rebuilds pages, figures and the PDF
   ```
3. Commit and push. GitHub Actions rebuilds and redeploys the site.

To preview locally (Ruby ≥ 3.1):

```bash
bundle install
bundle exec jekyll serve      # http://localhost:4000/serdes-tutorial/
```

To regenerate a Python figure, run its script with the tutorial's Python environment
(`numpy`, `scipy`, `matplotlib`, `serdespy`), for example
`cd book/tutorial/figsrc && python ch03_physics.py`.

## Hosting

GitHub Pages serves this repository from the `bricd-org` organization. The organization's user
site (`bricd-org.github.io`) has the custom domain `www.thebricd.org`, so this project site
appears at `https://www.thebricd.org/serdes-tutorial/`. No extra DNS setup is needed. In the
repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

## Credits

The tutorial draws on:

- Prof. Sam Palermo's ECEN 720 course (Texas A&M)
- Benjamin Liu's equalizer and CDR notes
- [serdespy](https://github.com/richard259/serdespy) (Richard Barrie and Katherine Liang)
- the IHP Open PDK
- JKU's IIC-OSIC-TOOLS and AMS chip template

The site layout follows the SkillSurf
[Art of Analog IC Design](https://github.com/SkillSurf/art_of_aicd) workshop and uses the
[just-the-docs](https://github.com/just-the-docs/just-the-docs) theme.

This is a living draft (v0.1, October 2026). Corrections are welcome as issues or pull requests.

## Licence

© 2026 the Open-SERDES Tutorial authors, BRICD.

- **Content**: the LaTeX book and its text, figures, tables and slides, the website pages and the
  PDFs are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).
  You may share and adapt them, including in your own courses and commercially, if you give
  credit, for example *"Open-SERDES Tutorial, BRICD, https://www.thebricd.org/serdes-tutorial/,
  CC BY 4.0"*, and say what you changed.
- **Code**: the lab scripts in `book/tutorial/code/`, the figure scripts in `book/tutorial/figsrc/`,
  the build tools in `tools/`, and the site's configuration, includes and styles are licensed under
  the [MIT licence](LICENSE-CODE).

Neither licence covers:

- the BRICD name and logo;
- the works the tutorial cites. Their ideas and results remain with their authors (see Credits
  above and the [References](https://www.thebricd.org/serdes-tutorial/references/) page), and
  figures marked "After …" are redrawn from the credited source;
- the Canva elements in the graphics made with Canva (`book/tutorial/canva/`,
  `assets/figs/canva_*`), which are used under Canva's content licence.
