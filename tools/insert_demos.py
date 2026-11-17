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
    (CH + "01-why-serial-links.html", "skew", "after:fig:ch1-parser"),
    (CH + "01-why-serial-links.html", "clockplan", "after:fig:link-anatomy"),
    (CH + "01-why-serial-links.html", "epb", "after:fig:ch1-glance"),
    (CH + "01-why-serial-links.html", "fo4rule", "after:fig:ch1-speed"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "nrzpsd", "after:fig:ch2-psd"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "lfsr", "after:fig:ch2-prbs"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "onepole", "after:fig:ch2-onepole"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "superpos", "after:fig:ch2-superposition"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "isieye", "after:fig:ch2-isi-tau"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "eyefold", "after:fig:ch2-eye-fold"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "berq", "after:fig:ch2-ber"),
    (CH + "02-signals-systems-and-the-language-of-links.html", "bathtub2", "after:fig:ch2-bathtub"),
    (CH + "03-the-channel.html", "tline", "end:sec3.2.1-when-is-a-wire-a-transmission-line"),
    (CH + "03-the-channel.html", "skin", "after:fig:ch3-skin"),
    (CH + "03-the-channel.html", "lossbuild", "after:fig:ch3-loss"),
    (CH + "03-the-channel.html", "bounce", "after:fig:ch3-bounce"),
    (CH + "03-the-channel.html", "padbond", "after:fig:ch3-pad"),
    (CH + "03-the-channel.html", "viastub", "after:fig:ch3-via"),
    (CH + "03-the-channel.html", "s21pulse", "after:fig:ref-pulse"),
    (CH + "04-link-budgets-and-statistical-analysis.html", "pda", "after:fig:ch4-pda"),
    (CH + "04-link-budgets-and-statistical-analysis.html", "isipdf", "after:fig:ch4-isipdf"),
    (CH + "04-link-budgets-and-statistical-analysis.html", "margin", "after:fig:ch4-waterfall"),
    (CH + "04-link-budgets-and-statistical-analysis.html", "pam4", "after:fig:ch4-pam4"),
    (CH + "05-equalization-fundamentals.html", "zfnoise", "after:fig:ch5-inverse"),
    (CH + "05-equalization-fundamentals.html", "cable", "after:fig:ch5-cable"),
    (CH + "05-equalization-fundamentals.html", "whoowns", "after:fig:ch5-anatomy"),
    (CH + "06-transmit-ffe.html", "ffefreq", "after:fig:ch6-ffefreq"),
    (CH + "06-transmit-ffe.html", "zfsolve", "after:fig:ch6-zf"),
    (CH + "06-transmit-ffe.html", "ffe", "after:fig:ch6-ref"),
    (CH + "07-continuous-time-linear-equalizer.html", "rlc", "after:fig:ch7-rlc"),
    (CH + "07-continuous-time-linear-equalizer.html", "ctlebode", "after:fig:ch7-bode"),
    (CH + "07-continuous-time-linear-equalizer.html", "ctleref", "after:fig:ch7-ref"),
    (CH + "08-decision-feedback-equalization-and-adaptation.html", "dfe", "after:fig:ch8-cancel"),
    (CH + "08-decision-feedback-equalization-and-adaptation.html", "tap1", "after:fig:ch8-timing"),
    (CH + "08-decision-feedback-equalization-and-adaptation.html", "sslms", "after:fig:ch8-sslms"),
    (CH + "11-jitter.html", "slope", "after:fig:ch11-slope"),
    (CH + "09-the-transmitter.html", "fo4rule", "after:fig:ch9-fo4"),
    (CH + "09-the-transmitter.html", "cmlsst", "after:fig:ch9-current"),
    (CH + "09-the-transmitter.html", "ffecurr", "after:fig:ch9-ffe"),
    (CH + "09-the-transmitter.html", "tcoil", "after:fig:ch9-pad"),
    (CH + "10-receiver-front-end-and-samplers.html", "latch", "after:fig:ch10-meta"),
    (CH + "10-receiver-front-end-and-samplers.html", "offsetcal", "after:fig:ch10-offset"),
    (CH + "10-receiver-front-end-and-samplers.html", "margin", "end:sec:ch10-noise"),
    (CH + "11-jitter.html", "tie", "after:fig:ch11-tie"),
    (CH + "11-jitter.html", "dualdirac", "after:fig:ch11-hist"),
    (CH + "11-jitter.html", "bathtub", "after:fig:ch11-bathtub"),
    (CH + "11-jitter.html", "pllnoise", "after:fig:ch11-pn"),
    (CH + "11-jitter.html", "jbudget", "after:fig:ch11-budget"),
    (CH + "12-clock-generation-the-phase-locked-loop.html", "pfd", "after:fig:ch12-pfd"),
    (CH + "12-clock-generation-the-phase-locked-loop.html", "pllloop", "after:fig:ch12-loop"),
    (CH + "12-clock-generation-the-phase-locked-loop.html", "pllnoise", "after:fig:ch12-noise"),
    (CH + "12-clock-generation-the-phase-locked-loop.html", "leeson", "after:fig:ch12-leeson"),
    (CH + "13-clock-and-data-recovery.html", "alex", "after:fig:ch13-alex"),
    (CH + "13-clock-and-data-recovery.html", "bbgain", "after:fig:ch13-bbchar"),
    (CH + "13-clock-and-data-recovery.html", "jtol", "after:fig:ch13-jtol"),
    (CH + "13-clock-and-data-recovery.html", "pi", "after:fig:ch13-pi"),
    (CH + "13-clock-and-data-recovery.html", "cdrsim", "after:fig:ch13-sim"),
    (CH + "14-the-open-serdes-architecture.html", "clockplan", "after:fig:ch14-clock"),
    (CH + "14-the-open-serdes-architecture.html", "padbond", "end:sec14.5.3-package-and-pinout"),
    (CH + "14-the-open-serdes-architecture.html", "power", "after:fig:ch14-power"),
    (CH + "15-design-and-verification-flow-with-open-tools.html", "mcruns", "end:sec:testbenches"),
    (CH + "15-design-and-verification-flow-with-open-tools.html", "bercount", "end:sec:labtest"),
    (CH + "16-hands-on-labs-with-serdespy.html", "labmap", "end:sec:lab0"),
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
