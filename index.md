---
title: Home
layout: default
nav_order: 0
permalink: /
---

<div class="hero">
  <div class="hero-cover"><a href="{{ '/assets/pdf/Open-SERDES_Tutorial.pdf' | relative_url }}"><img src="{{ '/assets/images/cover.png' | relative_url }}" alt="Cover of the Open-SERDES Tutorial"></a></div>
  <div class="hero-text">
    <p class="eyebrow">Open-SERDES · IHP SG13G2 · 5 Gb/s NRZ</p>
    <h1>Designing a Serial Link from Scratch</h1>
    <p class="fs-5">A design tutorial for undergraduate engineers building an open-source high-speed SerDes in 130&nbsp;nm SiGe BiCMOS. Channels, link budgets, equalization, transmitter and receiver circuits, jitter, PLLs and clock recovery, the open-source design flow, and hands-on labs.</p>
    <p>
      <a class="btn btn-primary mr-2" href="{{ '/preface/' | relative_url }}">Start reading</a>
      <a class="btn mr-2" href="{{ '/assets/pdf/Open-SERDES_Tutorial.pdf' | relative_url }}">Download the PDF</a>
      <a class="btn" href="https://github.com/bricd-org/serdes-tutorial">Source on GitHub</a>
    </p>
  </div>
</div>

<div class="key-numbers">
  <div><b>5 Gb/s</b><span>NRZ data rate</span></div>
  <div><b>200 ps</b><span>one unit interval</span></div>
  <div><b>2.5 GHz</b><span>Nyquist frequency</span></div>
  <div><b>−17.4 dB</b><span>reference channel loss</span></div>
  <div><b>10⁻¹²</b><span>target bit-error rate</span></div>
</div>

Every fast interface (PCIe, USB, Ethernet, chiplet links) rides on a SerDes, yet SerDes design is rarely taught end to end and almost never in the open. This tutorial follows one design, the **Open-SERDES** transceiver in IHP's open SG13G2 PDK, from the physics of the channel to a tape-out-ready architecture. Every concept follows the same pattern: a short derivation, a worked example with the project's real numbers, and a *what this means for your design* box.

<figure>
  <img src="{{ '/assets/figs/canva_roadmap.png' | relative_url }}" alt="Your path through this tutorial: five parts from Foundations to Putting it together" style="width:760px">
  <figcaption>The five parts of the tutorial. Read Part I first, then follow the system path or the circuit path (see the <a href="{{ '/preface/' | relative_url }}">Preface</a>).</figcaption>
</figure>

## What is inside

<div class="card-grid">
  <div class="card"><span class="card-label">Part I · Ch 1–4</span><h3><a href="{{ '/part-1/' | relative_url }}">Foundations</a></h3><p>Serial links, NRZ and PRBS, pulse responses and eyes, the channel, PDA and statistical link budgets.</p></div>
  <div class="card"><span class="card-label">Part II · Ch 5–8</span><h3><a href="{{ '/part-2/' | relative_url }}">Equalization</a></h3><p>TX FFE, CTLE and DFE theory and circuits, adaptation, and how to split the work between them.</p></div>
  <div class="card"><span class="card-label">Part III · Ch 9–10</span><h3><a href="{{ '/part-3/' | relative_url }}">Transceiver circuits</a></h3><p>Serializer, CML driver, termination and ESD; receiver front-end, StrongARM and HBT latches, metastability.</p></div>
  <div class="card"><span class="card-label">Part IV · Ch 11–13</span><h3><a href="{{ '/part-4/' | relative_url }}">Clocking</a></h3><p>Jitter and the dual-Dirac model, the charge-pump PLL and LC VCO, and a phase-interpolator CDR.</p></div>
  <div class="card"><span class="card-label">Part V · Ch 14–16</span><h3><a href="{{ '/part-5/' | relative_url }}">Putting it together</a></h3><p>The full architecture and budgets, the open-source design and verification flow, and seven serdespy labs.</p></div>
  <div class="card"><span class="card-label">Appendices</span><h3><a href="{{ '/appendices/' | relative_url }}">Reference</a></h3><p>Formula sheet, Q-function and dB tables, design-review checklists, glossary and further reading.</p></div>
</div>

## Hands-on labs

[Chapter 16]({{ '/chapters/16-hands-on-labs-with-serdespy/' | relative_url }}) reproduces the key plots of the book with [serdespy](https://github.com/richard259/serdespy): the reference channel, PRBS eyes, TX FFE, CTLE and DFE sweeps, jitter and BER, and a bang-bang phase-interpolator CDR. The scripts live in [`book/tutorial/code/`](https://github.com/bricd-org/serdes-tutorial/tree/main/book/tutorial/code).

## About

The tutorial is written for the Open-SERDES project at [BRICD](https://www.thebricd.org) (Biomedical Research in Integrated Circuit Design). It draws on Prof. Sam Palermo's ECEN 720 course notes (Texas A&amp;M), serdespy, IHP's open PDK and JKU's IIC-OSIC-TOOLS. Every source is listed on the [References]({{ '/references/' | relative_url }}) page.

**How this tutorial was made.** The Open-SERDES Tutorial was developed with the help of AI tools. The text, figures and code were reviewed by the authors, but errors may remain. The topics, structure and many of the results follow the sources listed in the References, especially Prof. Sam Palermo's ECEN 720 course. If you spot a mistake, please email [bricd.org@gmail.com](mailto:bricd.org@gmail.com) and we will correct it.

This is a living draft (v0.1, October 2026). Corrections and contributions are also welcome through [GitHub issues](https://github.com/bricd-org/serdes-tutorial/issues).
