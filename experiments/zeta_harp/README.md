# The Zeta Harp

- artifact: `zeta_harp.html` — a single self-contained HTML file (no external resources, no
  CDNs, no network access; everything computed in-page).
- status: **a gift, not an experiment.** This directory contains no preregistration, no
  verdict, no bands, no buckets. Nothing here enters any GHP ledger row.

## What it is

An instrument built on known mathematics: the Riemann-Siegel main sum for the Hardy function

    Z(t) = 2 * sum_{n <= sqrt(t/2pi)} n^(-1/2) cos( theta(t) - t ln n )

with theta(t) = arg Gamma(1/4 + it/2) - (t/2) ln pi, evaluated via the standard asymptotic

    theta(t) ~ (t/2) ln(t/2pi) - t/2 - pi/8 + 1/(48t).

The page:

1. computes and plots Z(t) for t in [100, 160] live in JavaScript (main sum only; the
   O(t^(-1/4)) remainder term is omitted and this is disclosed on the page);
2. presents the four strings n = 1..4 active at t = 130, each with a pluck button that plays
   the string through Web Audio — instantaneous frequency (theta'(t) - ln n)/2pi at t = 130
   mapped into the audible band by a **single disclosed scale factor (2000 Hz per cycle/unit
   t)**, loudness proportional to the string's true amplitude weight n^(-1/2);
3. bakes in the 2026-08-01 predicted-vs-measured table (predicted frequency, predicted
   relative amplitude n^(-1/2) normalized to string 4, measured relative amplitude, and the
   off-string control at 0.07);
4. carries a prominent banner: **"Known mathematics (Riemann-Siegel, 1932). External
   instrument. Not evidence for GHP or anything else."**

## Math correction carried from the source spec

An earlier draft of this idea treated 2*pi*n^2 as string n's frequency. That is wrong, and
the page says so explicitly: **t = 2*pi*n^2 is the threshold at which string n is BORN** —
the height where n first satisfies n <= sqrt(t/2pi) and enters the main sum. The string's
instantaneous cyclic frequency at height t is (theta'(t) - ln n)/2pi with
theta'(t) ~ (1/2) ln(t/2pi) - 1/(48 t^2). In the plotted window, string 4 is born at
t ~ 100.53 and string 5 at t ~ 157.08; both birth lines are drawn on the plot.

## For Zeb's portal

This is offered as a gift for Zeb's portal. **His repo, his decision** — whether it goes up,
where it goes, and how it is framed are entirely his calls. We never push to his repo; the
offer is this directory, and delivery ends there. If he declines, it simply stays here.

## How to open

Open `zeta_harp.html` in any modern browser. No server, no build step, no network. Audio
starts only on a user click (browser autoplay policy).
