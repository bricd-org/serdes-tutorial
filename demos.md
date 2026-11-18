---
title: "Interactive Demos"
nav_order: 1.5
permalink: "/demos/"
---

# Interactive demos

57 interactive demos break the hard ideas of the book into things you can move. Each one runs in the page, with no install, and reproduces the numbers its chapter quotes at its default settings; most of the channel and equalizer demos run a JavaScript port of the labs' link model. Click a demo to jump to it in its chapter.
{: .fs-5 .fw-300 }

## 1. Why Serial Links?

- [Parallel bus vs serial link]({{ '/chapters/01-why-serial-links/' | relative_url }}#bdSkew): skew closes a parallel bus as the bit rate rises.
- [The clock plan]({{ '/chapters/01-why-serial-links/' | relative_url }}#bdClockPlan): every clock in the Open-SERDES chip against the line rate.
- [Energy per bit]({{ '/chapters/01-why-serial-links/' | relative_url }}#bdEpb): energy per bit of a link.
- [How fast can CMOS clock?]({{ '/chapters/01-why-serial-links/' | relative_url }}#bdFo4): the 8-FO4 clock rule and the serializer architecture.

## 2. Signals, Systems and the Language of Links

- [NRZ spectrum]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdNrzPsd): where the power of random NRZ sits.
- [LFSR and PRBS]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdLfsr): an LFSR generating a PRBS pattern.
- [Bandwidth ↔ rise time]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdOnePole): bandwidth and rise time of a one-pole channel.
- [Superposition]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdSuperpos): a received waveform is a sum of shifted pulse responses.
- [ISI and the eye]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdIsiEye): how a slower channel spreads the pulse and closes the eye.
- [Fold the waveform into an eye]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdEyeFold): an eye diagram folds the waveform every 2 UI.
- [The BER cliff]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdBerQ): bit-error rate as the Gaussian tail beyond half the eye.
- [The bathtub]({{ '/chapters/02-signals-systems-and-the-language-of-links/' | relative_url }}#bdBathtub2): bathtub curve from Gaussian edge jitter.

## 3. The Channel

- [When is a wire a transmission line?]({{ '/chapters/03-the-channel/' | relative_url }}#bdTline): when a wire becomes a transmission line.
- [Skin effect]({{ '/chapters/03-the-channel/' | relative_url }}#bdSkin): skin depth and the resistance of a stripline.
- [Where the loss comes from]({{ '/chapters/03-the-channel/' | relative_url }}#bdLossBuild): conductor and dielectric loss of the channel.
- [Reflections]({{ '/chapters/03-the-channel/' | relative_url }}#bdBounce): lattice diagram of reflections on a transmission line.
- [Bond wire and pad]({{ '/chapters/03-the-channel/' | relative_url }}#bdPadBond): return loss of a bond wire and a pad capacitance.
- [Via stub]({{ '/chapters/03-the-channel/' | relative_url }}#bdViaStub): a via stub is a quarter-wave notch in the channel.
- [From S21 to the pulse]({{ '/chapters/03-the-channel/' | relative_url }}#bdS21Pulse): from channel loss to the pulse response and its cursors.

## 4. Link Budgets and Statistical Analysis

- [Peak distortion]({{ '/chapters/04-link-budgets-and-statistical-analysis/' | relative_url }}#bdPda): peak distortion analysis of the REF channel.
- [ISI distribution]({{ '/chapters/04-link-budgets-and-statistical-analysis/' | relative_url }}#bdIsiPdf): the ISI distribution as a convolution of two-point distributions.
- [Margin budget]({{ '/chapters/04-link-budgets-and-statistical-analysis/' | relative_url }}#bdMargin): the voltage margin budget at the sampler.
- [NRZ or PAM4?]({{ '/chapters/04-link-budgets-and-statistical-analysis/' | relative_url }}#bdPam4): when PAM4 beats NRZ on the REF-type line.

## 5. Equalization Fundamentals

- [The price of inverting the channel]({{ '/chapters/05-equalization-fundamentals/' | relative_url }}#bdZfNoise): an inverse equalizer amplifies noise.
- [Loss in dB → pulse]({{ '/chapters/05-equalization-fundamentals/' | relative_url }}#bdCable): a dielectric-loss cable model ties loss in dB to the pulse.
- [Who removes which cursor]({{ '/chapters/05-equalization-fundamentals/' | relative_url }}#bdWhoOwns): which equalizer removes which part of the pulse.

## 6. Transmit FFE

- [De-emphasis]({{ '/chapters/06-transmit-ffe/' | relative_url }}#bdFfeFreq): de-emphasis levels and the frequency response of a 2-tap FFE.
- [Zero forcing, tap by tap]({{ '/chapters/06-transmit-ffe/' | relative_url }}#bdZfSolve): zero forcing removes only the cursors it is told to.
- [TX FFE on REF]({{ '/chapters/06-transmit-ffe/' | relative_url }}#bdFfe): a 3-tap TX FFE on the REF channel.

## 7. Continuous-Time Linear Equalizer

- [RLC peaking]({{ '/chapters/07-continuous-time-linear-equalizer/' | relative_url }}#bdRlc): an inductively peaked load buys boost with ringing.
- [CTLE pole-zero designer]({{ '/chapters/07-continuous-time-linear-equalizer/' | relative_url }}#bdCtleBode): degenerated-pair CTLE, from components to boost.
- [CTLE on REF]({{ '/chapters/07-continuous-time-linear-equalizer/' | relative_url }}#bdCtleRef): CTLE peaking on the REF channel.

## 8. Decision-Feedback Equalization and Adaptation

- [DFE]({{ '/chapters/08-decision-feedback-equalization-and-adaptation/' | relative_url }}#bdDfe): a DFE cancelling post-cursors on REF after a CTLE.
- [Tap-1 timing]({{ '/chapters/08-decision-feedback-equalization-and-adaptation/' | relative_url }}#bdTap1): the DFE tap-1 timing budget.
- [Sign-sign LMS]({{ '/chapters/08-decision-feedback-equalization-and-adaptation/' | relative_url }}#bdSsLms): sign-sign LMS adapting a 2-tap DFE.

## 11. Jitter

- [Three jitter numbers]({{ '/chapters/11-jitter/' | relative_url }}#bdTie): TIE, period jitter and cycle-to-cycle jitter from clock edges.
- [Noise → jitter]({{ '/chapters/11-jitter/' | relative_url }}#bdSlope): voltage noise becomes timing jitter through the edge slope.
- [RJ ⊗ DJ and the dual-Dirac fit]({{ '/chapters/11-jitter/' | relative_url }}#bdDualDirac): total jitter and the dual-Dirac fit.
- [The bathtub]({{ '/chapters/11-jitter/' | relative_url }}#bdBathtub): dual-Dirac bathtub curve and eye width at a BER.
- [The optimum PLL bandwidth]({{ '/chapters/11-jitter/' | relative_url }}#bdPllNoise): PLL bandwidth trades reference noise against VCO noise.
- [Jitter budget]({{ '/chapters/11-jitter/' | relative_url }}#bdJBudget): the Open-SERDES jitter budget.

## 9. The Transmitter

- [How fast can CMOS clock?]({{ '/chapters/09-the-transmitter/' | relative_url }}#bdFo4): the 8-FO4 clock rule and the serializer architecture.
- [CML or SST driver?]({{ '/chapters/09-the-transmitter/' | relative_url }}#bdCmlSst): driver current and power, CML against voltage mode.
- [FFE tap currents]({{ '/chapters/09-the-transmitter/' | relative_url }}#bdFfeCurr): FFE tap currents in a CML driver.
- [Pad capacitance and the T-coil]({{ '/chapters/09-the-transmitter/' | relative_url }}#bdTcoil): sizing a bridged T-coil for the pad capacitance.

## 10. Receiver Front-End and Samplers

- [Regeneration and metastability]({{ '/chapters/10-receiver-front-end-and-samplers/' | relative_url }}#bdLatch): latch regeneration and metastability.
- [Offset calibration]({{ '/chapters/10-receiver-front-end-and-samplers/' | relative_url }}#bdOffsetCal): sampler offset spread and a trim DAC.
- [Margin budget]({{ '/chapters/10-receiver-front-end-and-samplers/' | relative_url }}#bdMargin): the voltage margin budget at the sampler.

## 12. Clock Generation: The Phase-Locked Loop

- [PFD and charge pump]({{ '/chapters/12-clock-generation-the-phase-locked-loop/' | relative_url }}#bdPfd): phase-frequency detector and charge pump waveforms.
- [PLL loop designer]({{ '/chapters/12-clock-generation-the-phase-locked-loop/' | relative_url }}#bdPllLoop): charge-pump PLL loop filter designer.
- [The optimum PLL bandwidth]({{ '/chapters/12-clock-generation-the-phase-locked-loop/' | relative_url }}#bdPllNoise): PLL bandwidth trades reference noise against VCO noise.
- [Leeson's model]({{ '/chapters/12-clock-generation-the-phase-locked-loop/' | relative_url }}#bdLeeson): Leeson's phase-noise model of an LC VCO.

## 13. Clock and Data Recovery

- [Alexander phase detector]({{ '/chapters/13-clock-and-data-recovery/' | relative_url }}#bdAlex): the Alexander bang-bang phase detector.
- [Bang-bang detector gain]({{ '/chapters/13-clock-and-data-recovery/' | relative_url }}#bdBbGain): jitter linearizes the bang-bang phase detector.
- [Jitter tolerance]({{ '/chapters/13-clock-and-data-recovery/' | relative_url }}#bdJtol): jitter tolerance of a bang-bang CDR against the mask.
- [Phase interpolator]({{ '/chapters/13-clock-and-data-recovery/' | relative_url }}#bdPI): phase interpolator weights and their nonlinearity.
- [PI-CDR locking]({{ '/chapters/13-clock-and-data-recovery/' | relative_url }}#bdCdrSim): behavioural simulation of the Open-SERDES PI-based bang-bang CDR.

## 14. The Open-SERDES Architecture

- [The clock plan]({{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#bdClockPlan): every clock in the Open-SERDES chip against the line rate.
- [Bond wire and pad]({{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#bdPadBond): return loss of a bond wire and a pad capacitance.
- [Power budget]({{ '/chapters/14-the-open-serdes-architecture/' | relative_url }}#bdPower): the Open-SERDES power budget and energy per bit.

## 15. Design and Verification Flow with Open Tools

- [How many Monte Carlo runs?]({{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#bdMcRuns): how many Monte Carlo runs it takes to know a sigma.
- [Bits needed to claim a BER]({{ '/chapters/15-design-and-verification-flow-with-open-tools/' | relative_url }}#bdBerCount): how many bits it takes to claim a BER.
