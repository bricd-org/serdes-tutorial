---
title: "Intro Slides"
layout: default
nav_order: 9
permalink: /slides/
---

<div class="slides-intro" markdown="0">
<p class="part-label">Open-SERDES introduction talk</p>
<h1>Intro Slides</h1>
<p class="part-blurb">The talk that introduces Open-SERDES: why an open serial link, why IHP SG13G2, the anatomy of the link, the open channel-to-GDS flow, what we will build and test, and the roadmap. Speaker notes sit under each slide; the tutorial chapter that goes deeper is linked where there is one.</p>
<p><a class="btn btn-primary mr-2" href="{{ '/assets/pdf/Open-SERDES_Intro_Slides.pdf' | relative_url }}">Download the slides (PDF)</a><a class="btn" href="{{ '/preface/' | relative_url }}">Read the tutorial</a></p>
<nav class="slide-index" aria-label="Slides">
<a href="#slide-1"><b>1</b> Open-SERDES: towards an open-source high-speed serial link</a>
<a href="#slide-2"><b>2</b> Raise your hand if…</a>
<a href="#slide-3"><b>3</b> Every fast interface is a SerDes</a>
<a href="#slide-4"><b>4</b> What exists in the open today</a>
<a href="#slide-5"><b>5</b> Part 1 · Why IHP SG13G2?</a>
<a href="#slide-6"><b>6</b> SG13G2: a BiCMOS process built for speed</a>
<a href="#slide-7"><b>7</b> We don’t start from zero</a>
<a href="#slide-8"><b>8</b> Part 2 · Anatomy of a serial link</a>
<a href="#slide-9"><b>9</b> Anatomy of a serial link</a>
<a href="#slide-10"><b>10</b> 5 Gb/s, in numbers</a>
<a href="#slide-11"><b>11</b> The design space we’ll explore</a>
<a href="#slide-12"><b>12</b> Part 3 · An open flow, channel to GDS</a>
<a href="#slide-13"><b>13</b> The Open-SERDES flow</a>
<a href="#slide-14"><b>14</b> Tool map: every step on open tools</a>
<a href="#slide-15"><b>15</b> Closing the loop: model ↔ silicon</a>
<a href="#slide-16"><b>16</b> One repository, one command</a>
<a href="#slide-17"><b>17</b> One command: the make targets</a>
<a href="#slide-18"><b>18</b> Why it’s hard, and why it’s worth it</a>
<a href="#slide-19"><b>19</b> Part 4 · What we’ll build and test</a>
<a href="#slide-20"><b>20</b> Highlights &amp; deliverables</a>
<a href="#slide-21"><b>21</b> Chip block diagram (concept)</a>
<a href="#slide-22"><b>22</b> Floorplan concept</a>
<a href="#slide-23"><b>23</b> Simulation testbench &amp; sign-off</a>
<a href="#slide-24"><b>24</b> Test bench in the lab</a>
<a href="#slide-25"><b>25</b> Package &amp; pinout (concept)</a>
<a href="#slide-26"><b>26</b> Part 5 · Roadmap &amp; community</a>
<a href="#slide-27"><b>27</b> Roadmap: blocks → 5 Gb/s → beyond</a>
<a href="#slide-28"><b>28</b> Get involved</a>
<a href="#slide-29"><b>29</b> References</a>
</nav>
</div>

<figure class="slide" id="slide-1" markdown="0">
<img src="{{ '/assets/slides/slide-01.png' | relative_url }}" alt="Slide 1: Open-SERDES: towards an open-source high-speed serial link" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 1.</span> Open-SERDES: towards an open-source high-speed serial link</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Close on the call to action: Open-SERDES is an open BRICD project. We are looking for contributors and collaborators at every level, from link modeling to layout and measurement. Contact: kithminr@uom.lk, thebricd.org. Thank the audience and invite questions.</p>
</details>

<figure class="slide" id="slide-2" markdown="0">
<img src="{{ '/assets/slides/slide-02.png' | relative_url }}" alt="Slide 2: Raise your hand if…" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 2.</span> Raise your hand if…</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Icebreaker, borrowed from the FSiC format. Expect many hands for the first two, fewer for CML/StrongARM and S-parameters, some for open-PDK tapeouts, and essentially none for the last one. That silence is the motivation for the whole project.</p>
</details>

<figure class="slide" id="slide-3" markdown="0">
<img src="{{ '/assets/slides/slide-03.png' | relative_url }}" alt="Slide 3: Every fast interface is a SerDes" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 3.</span> Every fast interface is a SerDes <a class="slide-related" href="{{ '/chapters/01-why-serial-links/' | relative_url }}#sec:anatomy">Ch 1 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>A SerDes turns a wide, slow parallel bus into one fast serial stream and back. Example numbers: 16 lanes at 312.5 Mb/s become a single 5 Gb/s NRZ stream on one differential pair. That is why every modern high-speed interface uses one. The catch: every production SerDes is closed IP, so almost nobody outside a handful of companies ever sees a complete design.</p>
</details>

<figure class="slide" id="slide-4" markdown="0">
<img src="{{ '/assets/slides/slide-04.png' | relative_url }}" alt="Slide 4: What exists in the open today" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 4.</span> What exists in the open today <a class="slide-related" href="{{ '/chapters/01-why-serial-links/' | relative_url }}#sec:os-targets">Ch 1 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Be fair to prior work. Purdue’s OpenSerDes (Kumar, Chatterjee, Sen, DATE 2021) is the closest: a fully synthesizable all-digital link in SKY130 at 2 Gb/s in post-layout simulation, about 438 mW including SER/DES/CDR, with no equalization. The Python and Julia link simulators are excellent but live at the system level. JKU’s template gives us the flow. Nobody has yet put these together into a mixed-signal, equalized, multi-Gb/s link on an open PDK. That is the gap Open-SERDES targets.</p>
</details>

<figure class="slide" id="slide-5" markdown="0">
<img src="{{ '/assets/slides/slide-05.png' | relative_url }}" alt="Slide 5: Part 1 · Why IHP SG13G2?" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 5.</span> Part 1 · Why IHP SG13G2?</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Part 1: the process. Why we chose IHP’s open SiGe BiCMOS PDK, and the SG13G2 work we already have.</p>
</details>

<figure class="slide" id="slide-6" markdown="0">
<img src="{{ '/assets/slides/slide-06.png' | relative_url }}" alt="Slide 6: SG13G2: a BiCMOS process built for speed" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 6.</span> SG13G2: a BiCMOS process built for speed <a class="slide-related" href="{{ '/chapters/01-why-serial-links/' | relative_url }}#sec:sg13g2">Ch 1 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>SG13G2 is IHP’s high-performance 130 nm SiGe:C BiCMOS. The PDK documentation lists HBTs with about 300 GHz fT and 500 GHz fmax (IHP’s MOS-AK 2025 talk quotes 350 / 450 GHz, with BVceo of 1.6 V). For a 5 Gb/s NRZ link the Nyquist frequency is only 2.5 GHz, so HBT current-mode logic has enormous headroom; that is exactly what the 130 nm SKY130 CMOS designs lacked. Seven aluminium layers, the top two 2 µm and 3 µm thick, give us decent inductors and lines. And, crucially, there is an open MPW path, including Tiny Tapeout on IHP.</p>
</details>

<figure class="slide" id="slide-7" markdown="0">
<img src="{{ '/assets/slides/slide-07.png' | relative_url }}" alt="Slide 7: We don’t start from zero" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 7.</span> We don’t start from zero <a class="slide-related" href="{{ '/chapters/12-clock-generation-the-phase-locked-loop/' | relative_url }}#sec:lcvco">Ch 12 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Three threads come together. First, our own open SG13G2 PLL, accepted at SMACD 2026: a 2.4 GHz type-II fractional-N PLL with a cross-coupled LC-VCO and a custom 4 nH spiral (Q of 16.8, modelled in openEMS), −100.8 dBc/Hz at 1 MHz, 12.73 mW, 0.347 mm². A half-rate 5 Gb/s link needs a 2.5 GHz clock, right next door. Second, an earlier University of Moratuwa project modelled a 5 Gb/s SerDes in a commercial 28 nm library, with a fast-locking ring-VCO PLL under 10 ps peak-to-peak jitter. Third, Purdue showed that open RTL-to-GDS automation can produce a working link. Open-SERDES combines all three on a faster, open BiCMOS node.</p>
</details>

<figure class="slide" id="slide-8" markdown="0">
<img src="{{ '/assets/slides/slide-08.png' | relative_url }}" alt="Slide 8: Part 2 · Anatomy of a serial link" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 8.</span> Part 2 · Anatomy of a serial link</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Part 2: the link itself. What blocks a serial link needs, what 5 Gb/s means in numbers, and which architectural choices are still open.</p>
</details>

<figure class="slide" id="slide-9" markdown="0">
<img src="{{ '/assets/slides/slide-09.png' | relative_url }}" alt="Slide 9: Anatomy of a serial link" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 9.</span> Anatomy of a serial link <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:arch-block">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Walk the link left to right. TX: a 16:1 serializer (a mux tree whose last stage runs at the full rate), a 2–3 tap feed-forward equalizer to pre-distort against channel loss, and a driver, current-mode (CML) or voltage-mode (SST), into a 100 Ω differential line. The channel is package, PCB traces and connectors, characterized by S-parameters. RX: a CTLE boosts high frequencies, a sampler (optionally with a DFE) decides bits, and the deserializer fans them back out. Clocking is the hard part: a TX PLL generates the half-rate 2.5 GHz clocks; on the RX side a CDR extracts timing from the data itself and steers the sampling phase.</p>
</details>

<figure class="slide" id="slide-10" markdown="0">
<img src="{{ '/assets/slides/slide-10.png' | relative_url }}" alt="Slide 10: 5 Gb/s, in numbers" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 10.</span> 5 Gb/s, in numbers <a class="slide-related" href="{{ '/chapters/04-link-budgets-and-statistical-analysis/' | relative_url }}#sec:noisebudget">Ch 4 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>At 5 Gb/s NRZ each bit lasts 200 ps and the channel has to carry energy up to the 2.5 GHz Nyquist frequency. A BER of 1e-12 or better is the usual serial-link target. This is the same rate class as PCIe Gen 2, USB 3.2 Gen 1 and 5GBASE-KR backplane Ethernet, so standard channel models exist to test against. The bracketed numbers are deliberately open: the first deliverable of the project is a feasibility study that fixes the channel, jitter, power and area budgets.</p>
</details>

<figure class="slide" id="slide-11" markdown="0">
<img src="{{ '/assets/slides/slide-11.png' | relative_url }}" alt="Slide 11: The design space we’ll explore" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 11.</span> The design space we’ll explore <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-decisions">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>This is where we want community input. Our current baseline: NRZ, because at 5 Gb/s PAM4 costs SNR and receiver complexity for no real gain. An HBT current-mode driver, since SG13G2’s bipolars make CML fast and robust; a source-series-terminated voltage-mode driver is the low-power alternative. A 2–3 tap TX FFE, an RX CTLE and a 2-tap half-rate DFE: the split the tutorial&#x27;s equalization study recommends for the reference channel (more taps only if a harder channel needs them). For the sampler we want to build both an HBT CML latch and a CMOS StrongARM and compare them. Half-rate clocking means a 2.5 GHz clock, very close to our existing 2.4 GHz LC-PLL. And a bang-bang (Alexander) phase detector with a digital loop filter, the most robust CDR to get working first; baud-rate Mueller–Müller and oversampled CDRs are alternatives.</p>
</details>

<figure class="slide" id="slide-12" markdown="0">
<img src="{{ '/assets/slides/slide-12.png' | relative_url }}" alt="Slide 12: Part 3 · An open flow, channel to GDS" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 12.</span> Part 3 · An open flow, channel to GDS</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Part 3: the workflow. This is the real contribution: a design and simulation flow anyone can rerun, from a channel S-parameter file all the way to a tapeout-ready GDS.</p>
</details>

<figure class="slide" id="slide-13" markdown="0">
<img src="{{ '/assets/slides/slide-13.png' | relative_url }}" alt="Slide 13: The Open-SERDES flow" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 13.</span> The Open-SERDES flow <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#sec:toolchain">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Five stages. One: a system-level link model in Python or Julia (serdespy, PyBERT, JLSD, with scikit-rf for S-parameters) turns a channel into block specifications: EQ taps, CTLE peaking, jitter budget. Two: transistor-level design in Xschem with ngspice, Xyce or VACASK, and CACE for PVT corners and Monte Carlo. Three: the digital side (serializer, deserializer, PRBS generator and checker, CDR loop logic) in SystemVerilog, verified with Verilator and cocotb, hardened with Yosys and LibreLane. Four: custom layout in KLayout or Magic, LVS with Netgen, parasitic extraction, and openEMS for inductors and pads. Five: top-level sign-off and a GDS ready for an IHP open MPW or Tiny Tapeout. The orange loop is the key idea: extracted results go back into the link model, so the model stays honest.</p>
</details>

<figure class="slide" id="slide-14" markdown="0">
<img src="{{ '/assets/slides/slide-14.png' | relative_url }}" alt="Slide 14: Tool map: every step on open tools" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 14.</span> Tool map: every step on open tools <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#sec:toolchain">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Mirrors the IIC-OSIC-TOOLS overview: one open tool, or a small set of alternatives, for each stage of the Open-SERDES flow. All of them run inside the IIC-OSIC-TOOLS container with the IHP SG13G2 Open-PDK.</p>
</details>

<figure class="slide" id="slide-15" markdown="0">
<img src="{{ '/assets/slides/slide-15.png' | relative_url }}" alt="Slide 15: Closing the loop: model ↔ silicon" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 15.</span> Closing the loop: model ↔ silicon <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#sec:model-loop">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>This is the piece nobody has in the open today. System-level link simulators are usually driven by idealized numbers; circuit designers work against specs handed to them. We want both directions automated: the link model generates block specs (gain, CTLE peaking, output swing, jitter allocations), and the circuit flow returns extracted pulse responses, CTLE transfer functions and noise that are dropped straight back into the model. The outcome is a statistical eye and BER for each design point, a Python GUI in the spirit of JLSD for exploring settings, and a model whose every number traces back to a simulated, and later measured, SG13G2 cell.</p>
</details>

<figure class="slide" id="slide-16" markdown="0">
<img src="{{ '/assets/slides/slide-16.png' | relative_url }}" alt="Slide 16: One repository, one command" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 16.</span> One repository, one command <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>We do not want to reinvent the project infrastructure. Simon Dorrer and Harald Pretl’s ihp-sg13g2-ams-chip-template already gives a Makefile-driven, recursive macro structure that goes to a tapeout-ready chip with one make all. Open-SERDES would add a model folder and a channels folder, and treat each SerDes block as a macro. The key addition is a single spec file read by both the Python model and the analog testbenches, plus continuous-integration checks that include eye opening, not only DRC and LVS. The folder names here are a proposal, and the licence is still to be decided.</p>
</details>

<figure class="slide" id="slide-17" markdown="0">
<img src="{{ '/assets/slides/slide-17.png' | relative_url }}" alt="Slide 17: One command: the make targets" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 17.</span> One command: the make targets <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Mirrors the JKU template Makefile tree. make all calls five top-level targets; build, sim and verify recurse into every macro folder, which all expose the same targets, so each block can also be built and tested on its own.</p>
</details>

<figure class="slide" id="slide-18" markdown="0">
<img src="{{ '/assets/slides/slide-18.png' | relative_url }}" alt="Slide 18: Why it’s hard, and why it’s worth it" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 18.</span> Why it’s hard, and why it’s worth it <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-risks">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Be honest about the risk. At these speeds the weak points are model accuracy (HBT compact models and layout parasitics at multi-GHz), the maturity of open RF extraction and EM tools for pads, ESD structures and inductors, simulation time for PLL and CDR loops, and the very practical problem of packaging and measuring a 5 Gb/s signal. Each of those is also a contribution in its own right. If we succeed, the community gets the first open multi-Gb/s reference design, a reusable CML cell library, a calibrated link model, and a complete teaching path from textbook link theory to silicon.</p>
</details>

<figure class="slide" id="slide-19" markdown="0">
<img src="{{ '/assets/slides/slide-19.png' | relative_url }}" alt="Slide 19: Part 4 · What we’ll build and test" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 19.</span> Part 4 · What we’ll build and test</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Part 4: what we will actually deliver, what the chip looks like, and how we will test it, in simulation and in the lab. Everything here is a concept and will evolve.</p>
</details>

<figure class="slide" id="slide-20" markdown="0">
<img src="{{ '/assets/slides/slide-20.png' | relative_url }}" alt="Slide 20: Highlights &amp; deliverables" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 20.</span> Highlights &amp; deliverables <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-deliver">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>The A-to-Z summary. Highlights: what makes the project new. Deliverables: what anyone will be able to download at the end: the GDS, the RTL and benches, the link model with its GUI, a reusable HBT/CML cell library, documentation, and the paper with open measurement data.</p>
</details>

<figure class="slide" id="slide-21" markdown="0">
<img src="{{ '/assets/slides/slide-21.png' | relative_url }}" alt="Slide 21: Chip block diagram (concept)" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 21.</span> Chip block diagram (concept) <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-testchip">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>One possible test chip, in the spirit of the TinyWhisper block diagram. Digital on the left: SPI configuration registers, a PRBS-7/31 generator and a PRBS checker with error counter. TX on top: serializer, FFE and driver to the TX pads. RX below: CTLE, sampler with optional DFE, and deserializer back to the checker. The LC-PLL takes an external reference and clocks the TX; the CDR recovers timing for the sampler. An internal loopback lets us test TX into RX on chip, and the external test PCB closes the loop through a real channel.</p>
</details>

<figure class="slide" id="slide-22" markdown="0">
<img src="{{ '/assets/slides/slide-22.png' | relative_url }}" alt="Slide 22: Floorplan concept" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 22.</span> Floorplan concept <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-testchip">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>What the die could look like, in the spirit of the TinyWhisper chip render. High-speed TX and RX pads sit on one edge to keep bond wires short; the LC-PLL gets its own corner, guard ring and supply; the digital core is hardened with LibreLane. Size and placement are placeholders until the blocks exist.</p>
</details>

<figure class="slide" id="slide-23" markdown="0">
<img src="{{ '/assets/slides/slide-23.png' | relative_url }}" alt="Slide 23: Simulation testbench &amp; sign-off" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 23.</span> Simulation testbench &amp; sign-off <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#sec:testbenches">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Inspired by the full top-level LVS and simulation slide. The top-level testbench drives a PRBS-31 pattern through the post-layout TX, an S-parameter channel model and the post-layout RX into a checker that reports eye, BER and jitter. We sweep channel loss, PVT, jitter and settings against pass criteria that the feasibility study will fix, and sign off with full-chip DRC and LVS without black boxes, all in CI.</p>
</details>

<figure class="slide" id="slide-24" markdown="0">
<img src="{{ '/assets/slides/slide-24.png' | relative_url }}" alt="Slide 24: Test bench in the lab" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 24.</span> Test bench in the lab <a class="slide-related" href="{{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#sec:labtest">Ch 15 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Inspired by the TinyWhisper breadboard and scope photos. A PC runs the Python GUI and talks to an FPGA or MCU board over USB; that board configures the chip over SPI and reads back the BER counter. A bench supply powers the test PCB, a clean reference clock feeds the PLL, TX goes out through SMA into a channel or loopback and back into RX, and a sampling scope or BERT captures eyes, jitter and BER.</p>
</details>

<figure class="slide" id="slide-25" markdown="0">
<img src="{{ '/assets/slides/slide-25.png' | relative_url }}" alt="Slide 25: Package &amp; pinout (concept)" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 25.</span> Package &amp; pinout (concept) <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-testchip">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Inspired by the TinyWhisper bonding diagram. A QFN package with the high-speed TX and RX pins on one side and the shortest bond wires, an external reference clock, SPI for configuration and BER readout, separate supply domains, and a few status pins. As in the JKU template, the bonding plan would be generated from a config file.</p>
</details>

<figure class="slide" id="slide-26" markdown="0">
<img src="{{ '/assets/slides/slide-26.png' | relative_url }}" alt="Slide 26: Part 5 · Roadmap &amp; community" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 26.</span> Part 5 · Roadmap &amp; community</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Part 5: how we get there, and where you come in.</p>
</details>

<figure class="slide" id="slide-27" markdown="0">
<img src="{{ '/assets/slides/slide-27.png' | relative_url }}" alt="Slide 27: Roadmap: blocks → 5 Gb/s → beyond" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 27.</span> Roadmap: blocks → 5 Gb/s → beyond <a class="slide-related" href="{{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#sec:ch14-roadmap">Ch 14 →</a></figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Five phases. Phase 0 is the feasibility study: an industry-standard channel, the link model, the architecture decision and frozen block specs. Phase 1 builds and tapes out the building blocks on a test shuttle, such as Tiny Tapeout IHP or an IHP open MPW. Phase 2 is the headline goal: a complete 5 Gb/s NRZ transceiver with TX, RX, PLL and CDR, verified with an on-chip PRBS loopback, taped out as a full chip. Phase 3 is measurement and publication, with open data, targeting IEEE JSSC or TCAS and SMACD 2027. Phase 4 pushes to 10 Gb/s and beyond: adaptive DFE, PAM4, multiple lanes and chiplet-style links. [Add dates once the timeline is agreed.]</p>
</details>

<figure class="slide" id="slide-28" markdown="0">
<img src="{{ '/assets/slides/slide-28.png' | relative_url }}" alt="Slide 28: Get involved" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 28.</span> Get involved</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>We need people across the whole stack, and you do not need to know everything to start: curiosity and willingness to learn count most. System modellers in Python or Julia; analog and RF designers for CML, CTLE, samplers and the PLL; digital designers for the serializer, deserializer, PRBS and CDR logic; layout and EM people; anyone with a lab bench for measurement; and people who love writing tutorials. Everything will live publicly on GitHub.</p>
</details>

<figure class="slide" id="slide-29" markdown="0">
<img src="{{ '/assets/slides/slide-29.png' | relative_url }}" alt="Slide 29: References" loading="lazy" width="1600" height="900">
<figcaption><span class="capnum">Slide 29.</span> References</figcaption>
</figure>
<details class="slide-notes" markdown="0"><summary>Speaker notes</summary>
<p>Reference slide; leave it up during questions if useful.</p>
</details>

