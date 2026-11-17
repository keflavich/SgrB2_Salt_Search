# GBT-26B-012 — Salt in Sgr B2(N)

ASTRID observing scripts for the GBT mapping proposal that follows up the
22A-020 VLA non-detection of NaCl in Sgr B2(N). We map a **6′ × 6′** region
centered on **Sgr B2(M)** (encompassing Sgr B2(N) and G0.693−0.027; maps
before 2026-11-17 were centered on Sgr B2(N), 46″ north) at both
Ku- and K-band on-the-fly (OTF), to localize the extended NaCl emission
(13 GHz, seen by PRIMOS, resolved out by the VLA) and the 26 GHz absorption.

## Files

| File | Purpose |
|------|---------|
| `sgrb2_salt.cat` | ASTRID source catalog (map center SgrB2M; SgrB2N kept; J2000, LSR) |
| `config_Ku_NaCl.py` | Ku-band VEGAS config — NaCl v=0 **1‑0** (13 GHz, emission) |
| `config_K_NaCl.py` | K-band VEGAS + KFPA config — NaCl v=0 **2‑1** (26 GHz, absorption) |
| `pointing_Ku.py` | Ku pointing + focus (standalone SB), `AutoPeakFocus(location="SgrB2M", frequency=13026.0, …)` |
| `pointing_K.py` | KFPA pointing + focus (standalone SB), `AutoPeakFocus(location="SgrB2M", frequency=26051.9, …)` |
| `map_Ku_NaCl_RaLongMap.py` | Ku 6′×6′ OTF map, RA-scanned rows (one map) |
| `map_Ku_NaCl_DecLatMap.py` | Ku 6′×6′ OTF map, Dec-scanned rows (one map) |
| `map_K_NaCl_RaLongMap.py` | KFPA 6′×6′ OTF map, RA-scanned rows (one map) |
| `map_K_NaCl_DecLatMap.py` | KFPA 6′×6′ OTF map, Dec-scanned rows (one map) |
| `map_Ku_NaCl_withCal.py` | Ku RA+Dec map block (2 maps, no pointing) |
| `map_KFPA_nacl_withCal.py` | KFPA RA+Dec map block (2 maps, no pointing) |
| `map_Ku_NaCl.py`, `map_K_NaCl.py` | RA+Dec pair in one SB, with a `Break` — observer-run only |
| `validate_scripts.py` | offline self-consistency check (see below) |
| `plot_windows_on_primos.py` | overplots the Ku windows on the PRIMOS spectrum → `windows_on_primos.png` |
| `drift_rfi.py` | GBT RFI-monitor scans from NRAO DRIFT → RFI in the Ku + K windows, Doppler-mapped to rest frequency for 26B → `rfi_on_primos.png`, `drift_rfi_regions.csv` (raw spectra cached in `drift_cache/`, git-ignored) |
| `reduction/` | GBTIDL OTF reduction: `reduce_session.pro` (driver), `otf_map_scans.pro`, `otf_tsys_table.pro`, `fsw_otf_line.pro`; Python: `grid_tsys.py`, `make_cubes.py`, `line_maps.py`, `diag_*.py` |
| `line_plan.py` | target-line extents + window geometry (both-states band, VEGAS spike and its FSW images); used by the validator and both plots |
| `plot_pointing_overview.py` | map-center options on ALMA 3 mm → `pointing_overview.png` |

## Per-session sequence

**Pointing and mapping are separate scheduling blocks.** `AutoPeakFocus` lives
only in `pointing_<band>.py`; every map SB does its own
`Configure` → `Slew` → `Balance` → map. That way a map that fails to balance,
or has to be aborted, is re-run **on its own** — the point/focus is never
repeated.

The operator queues alternating SBs and lets ASTRID run down the list:

**KFPA (26 GHz)** — one map per pointing (a map is 43.7 min):

| | SB | ≈ |
|---|---|---|
| 1 | `pointing_K.py` | 5 min |
| 2 | `map_K_NaCl_RaLongMap.py` | 43.7 min |
| 3 | `pointing_K.py` | 5 min |
| 4 | `map_K_NaCl_DecLatMap.py` | 43.7 min |
| | … repeat, alternating RA and Dec | |

**Ku (13 GHz)** — a map is only 12.9 min, so each map SB runs a balanced
RA+Dec pair (`maps_per_block = 2`, ~26 min) between pointings:

| | SB | ≈ |
|---|---|---|
| 1 | `pointing_Ku.py` | 5 min |
| 2 | `map_Ku_NaCl_withCal.py` | 25.8 min |
| | … repeat | |

Each map is **one single-direction OTF pass**, and the queue **alternates
RA-scanned and Dec-scanned passes** so coverage is basketweaved — orthogonal
maps suppress scan-direction striping and 1/f drifts. Stop when time is up:
any completed map counts toward the campaign total.

Campaign totals to track: **131 maps (Ku)** at 12.9 min each, and for KFPA a
count derived from the on-source budget at **43.7 min/map** (see the K bullet
below).

We do frequent pointing (every ~30-40m) because of the low elevation.

Scripts are meant to run verbatim; they assume the project directory is
`/users/aginsbur/GBT-26B-012` (`PROJPATH`).

`map_KFPA_nacl_withCal.py` is the KFPA equivalent of the Ku block script — two
maps back to back with no re-point. At 26 GHz that leaves ~87 min between
point/focus solutions, so it is **not** the default flow; use the
single-direction SBs above unless pointing is known to be stable.

## Reduction (`reduction/`)

GBTIDL procedures plus one Python gridder. On a GBO machine, in GBTIDL:

```idl
!path = expand_path('+/users/aginsbur/GBT-26B-012/reduction') + ':' + !path
reduce_session, 'AGBT26B_012_01'          ; or /live while observing
```

This writes, for every RALongMap/DecLatMap row in the session:

- `AGBT26B_012_01_tsys.csv`: Tsys of every integration (all 4 windows,
  both beams and pols, both FSW states) with position and elevation.
  `python grid_tsys.py AGBT26B_012_01_tsys.csv` grids it into raw Tsys maps
  per beam and an edge-referenced continuum map per window (FITS + PNG).
- `AGBT26B_012_01_H2CO.fits`: one calibrated, folded spectrum per
  integration (Ta, LSR −650…+650 km/s, 0.47 km/s channels). Each spectrum has
  a baseline fitted outside the line and its two FSW images.
  `gbtgridder --clobber -o AGBT26B_012_01_H2CO AGBT26B_012_01_H2CO.fits`
  makes the cube.

Grid each session separately and combine the cubes afterwards. Doppler
tracking is on NaCl 1-0, so the velocity of a given W2 channel shifts slightly
between sessions, and gbtgridder assumes every input spectrum has the same
channels.

### Whole windows and moment maps (local Python)

fourier has no astropy, so the gridding and maps run locally on copies of the
keep files.

```idl
reduce_session, 'AGBT26B_012_01', /notsys, /windows   ; -> _W1.._W4.fits, whole folded windows
```

| script | does |
|---|---|
| `make_cubes.py KEEP.fits ...` | grids keep files into `<root>_cube.fits` (+ `_wt.fits`); gbtgridder's kernel and frequency convention, numpy/scipy only |
| `line_maps.py CUBE.fits ...` | per-line local baseline (±150 km/s around the line, avoiding PRIMOS features and FSW images), moment-0 + error FITS, `<root>_lines.csv`, `<root>_mom0.png` gallery and `<root>_spectra.png` toward N and M. It maps the named lines, the RRLs (Rydberg formula) and unknown PRIMOS features ≥ 15 mK |
| `make_primos_features.py` | regenerates `primos_features.csv` (PRIMOS detections in W1–W4) from `../PRIMOS_Full.txt` |
| `diag_feed_spectra.py KEEP.fits` | mean spectrum per feed × pol, off-source and on M: shows the FSW baseline ripple of each feed/pol |
| `diag_crosstalk.py KEEP.fits --blob RA DEC` | tests whether a compact feature is real sky or one feed leaking into the other |

Diagnostic outputs go in `diagnostics/` next to the data (the default
`--outdir`), so they are kept.

## Spectral setup

**VEGAS Mode 4, 187.5 MHz windows, 32768 channels (5.7 kHz), in-band
frequency switching** (`swmode='sp'`, cal on). Native resolution is far finer
than needed, so smooth to ~1 km/s in reduction.

- **Ku:** **4 windows × 2 beams = 8 banks** (the dual-beam limit). NaCl is the
  top priority. Window centers are rest frequencies (MHz); `config_Ku_NaCl.py`
  is the source of truth.

  | W | center | lines (offset from center, MHz) |
  |---|---|---|
  | 1 | 13085.66 | **NaCl v=0 1‑0 13026.061 (−59.6)**, H79α 13088.85 (+3.2), He79α 13094.18 (+8.5), H₂C¹⁸O 2₁₁‑2₁₂ 13166.04 (+80.4) |
  | 2 | 14516.0 | H₂CO 2₁₁‑2₁₂ 14488.479 (−27.5) |
  | 3 | 13753.8 | H₂¹³CO 2₁₁‑2₁₂ 13778.804 (+25.0) |
  | 4 | 12916.41 | vib.-excited NaCl 12929.260 (+12.8), 12833.076 (−83.3) |

  The switching offsets are symmetric (`swfreq = −5.86, +5.86`), so each
  window keeps center ±87.89 MHz in band in both states, for either sign
  convention. VEGAS also puts a one-channel spike at the center of each
  state's band, i.e. at center ±5.86, and folding copies it to center ±17.58.
  `line_plan.py` lists each target line's extent: measured in PRIMOS where
  the line is detected (including the H₂CO / H₂¹³CO foreground absorption),
  otherwise ±30 km/s (NaCl) or ±40 km/s (RRLs). `validate_scripts.py` checks
  that every extent is ≥3 MHz inside the both-states band and clears the
  spike and its images. H₂CO and H₂¹³CO therefore sit 25–28 MHz off their
  window centers. The +5.86 spike falls between H79α and He79α, 61 km/s from
  each; no placement does better while keeping H₂C¹⁸O in W1 and W1/W4
  overlapping. The both-states ranges of W4 (12828.5–13004.3) and W1
  (12997.8–13173.6) overlap by 6.5 MHz, so nothing between NaCl v=2 and
  H₂C¹⁸O is lost. `dopplertrackfreq` stays on NaCl
  (13026.061), which is not a window center; the GBT configure docs allow this
  (`validate_scripts.py` warns about it — expected).
  `python plot_windows_on_primos.py` overplots the windows on the PRIMOS
  spectrum (read from the config, so it cannot drift).
- **K (2‑1):** 7 KFPA beams, **one** window on **NaCl v=0 2‑1 = 26051.898 MHz**
  (absorption), replicated across beams (7 beams ⇒ 1 bank/beam). 0.065 km/s
  native.
- **Throw 11.72 MHz** in both bands, as symmetric offsets ±5.86 MHz (see the
  K-band caveat below). With symmetric offsets, VEGAS's center-channel spike
  never sits on a line placed at a window center (H₂CO, H₂¹³CO, NaCl 2‑1).

**Frequency switching vs position switching.** We use FSW because the lines are
narrow, and because it validates that the region is emission-free. Both
phases are recorded, so the same data can also be reduced as total power with
an "off" built from the median (or n‑th percentile) spectrum of the map,
masking bright emission/absorption.

**Ku bright-line check (SO).** SO 1₂‑1₁ at 13043.81 MHz (2.3 K in PRIMOS, ~50×
NaCl) is 17.75 MHz above NaCl. With the 11.72 MHz throw the closest approach of
either line's switching image to the other line is 6.03 MHz (139 km/s); the
folded-spectrum ghost in the NaCl channels is ≤~3 mK vs a 45 mK NaCl peak
(both fold signs tested on PRIMOS). The SO image's nearest edge is only ~2 MHz
(~46 km/s) from the NaCl emission edge, so check for velocity differences
across the map in the first data. Changing the throw does not obviously help.

**Beam 2 (Ku).** Both beams are recorded but maps use `beamName="1"`; beam 2
sits 330″ (5.5′) away in cross-elevation, so it samples a patch just outside
the 6′ field (recombination lines, whatever else the windows catch). That
offset rotates with parallactic angle (up to ~35° at Sgr B2's low elevation),
so beam 2 gives an arc of uneven coverage, not a clean adjacent tile.

## Map / sensitivity budget

One map = one single-direction 6′ OTF pass giving integration time ~19
s/beam; alternate RA/Dec across repeats to basketweave.

- **Ku** —  FWHM 57″,
  row sep 24″ (Nyquist), 16 rows, 48.5 s/row → 12.9 min/map.
  10σ on the ~30 mK peak → ~3 mK/beam → ~2500 s/beam → 131 maps →
  ~28 h on-source, ~36 h with overhead → 12 × 3 h sessions.
- **K (KFPA)** — FWHM 28.5″, row sep **13.85″ = FWHM/2**, 27 rows,
  97 s/row → **43.7 min/map**. The default 51.4″ row step relies on different
  beams of the 7-beam KFPA filling the gaps; I want each beam fully sampled on
  its own, which needs Nyquist spacing. (51.43/3 = 17.14″ was an earlier
  attempt at this — it is still 20% coarser than Nyquist, and gave a ragged
  21.9994 rows. `mapsize/26` fixes both.) 10σ on the ~15 mK peak → ~3 mK/beam.
  → ~2.4 h/session at 3 maps + a point/focus SB before each.

  **Integration per sky point scales with map duration, so the invariant is
  total on-source hours, not map count**: `N_maps = total_on_source / 43.7 min`.
  Multiply any count tracked against the older 22-row/35.6-min geometry by
  35.6/43.7 = 0.82. Note the "~41 h on-source" figure below never reconciled
  with either the 116-map or the 39-map line — re-derive it from the
  allocation before committing to a session count.
- Total allocation: 87 h.

## Observing notes / to confirm before submission

- **KFPA calibration:** include a per-session KFPA cal observation (diode
  strengths drift between sessions) — see `pointing_K.py`.
- **Freq-switch throws** are set to clear the line and use an integer
  number of channels: 11.71875 MHz = 187.5/16 = exactly 2048 channels.
  At K that is only **135 km/s**, which does *not* fully clear a
  ±100 km/s absorption complex — switch to 23.4375 MHz (4096 chan,
  270 km/s) if a clean reference is needed.
- Edit `PROJPATH` in each script to the project's GBT script directory.

## `validate_scripts.py` — offline self-consistency check

**Run this after editing any config, before uploading to ASTRID:**

```
python validate_scripts.py [-v]      # exits nonzero on ERROR
```

ASTRID's validator only checks syntax and legality of each config *in
isolation*. Because `Configure()` evaluates every `keyword = value` line in its
own namespace, every derived number has to be typed in as a hand-computed
literal — and nothing on the telescope will notice when one drifts out of sync.
This script re-derives them.

Consistency relations are written into the configs themselves as `CHECK:`
annotations, evaluated against the *full* config namespace:

```python
swfreq = -5.859375, 5.859375   # CHECK: (-bandwidth*2**-5, bandwidth*2**-5)
                               # CHECK: (-1024*chanwidth, 1024*chanwidth)
tint   = 1.6                # CHECK: 2*swper
```

Change `bandwidth` and forget `swfreq`, and you get
`the hand-typed literal has drifted from its formula`. Helpers available inside
a `CHECK:` expression: `chanwidth` (MHz), `chanvel` (km/s), `fwhm` (arcsec),
`primaryfreq`, `nbeams`, `nwindows`, `c_kms`, plus everything in `math`.

On top of that it checks, without a telescope:

- ASTRID's per-keyword evaluation — reproduces the `NameError` locally
- enumerated keyword values; receiver frequency range, beam count, native pol
- the VEGAS mode table: `bandwidth`/`nchan` is a real mode, `tint` above the
  mode minimum, `tint` an integer multiple of `swper`
- **switching-phase blanking** — models the blank as one mode-minimum
  integration, which reproduces ASTRID's own
  *"more than 10% of your data will be blanked in BankX"* warning
- freq-switch throw: integer channels, stays inside the half-window, km/s
- VEGAS bank budget (windows × beams against the per-beam routing limit)
- data rate and GB/map/hour
- catalog format, and that every source a scan names actually exists
- SB command ordering: `Configure` → `Slew` → `Balance` → scans, and that
  `AutoPeakFocus` is always followed by a re-`Configure`
- map geometry *against the config*: scan rate, sample spacing vs FWHM/4,
  row step vs Nyquist, integer row count, the 30 s scan-leg minimum

It emulates the ASTRID commands rather than calling them, so it runs anywhere
with a stock Python (2 or 3), no GBT software needed.

## ASTRID gotchas (learned the hard way)

- **Config values must be self-contained literals.** `Configure()` evaluates
  each `keyword = value` line in its *own* namespace, so
  `swfreq = 0.0, bandwidth*2**-4` fails with
  `NameError: name 'bandwidth' is not defined`. Same for `bandwidth[0]*...`.
- **`bandwidth` is a single float**, even with multiple `restfreq` values.
- **`swtype = 'fsw'` is required** alongside `swmode = 'sp'`; without it
  nothing is frequency-switched.
- **`beam` takes comma-separated integers** (`'1,2'`), not `'B12'`.
- **Both Rcvr12_18 and the KFPA are circular-polarization** receivers, so
  `pol = 'Circular'`.
- **Always `Balance()`** after the science `Configure()`, on-source, at the
  observing elevation — and always re-`Configure()` after `AutoPeakFocus`,
  which runs its own continuum config.
- **VEGAS bank limits:** dual-beam ⇒ ≤4 banks/beam (so 4 windows × 2 Ku beams
  = 8 banks is exactly at the limit); 5+ beams ⇒ 1 bank/beam (so the 7-beam
  KFPA setup can only have one spectral window).
- Raster legs must be ≥30 s (48.5 s Ku / 97 s K — fine).
- **`swper` must be long enough that VEGAS blanking is <10%.** With
  `swmode='sp'` there are 4 phases per cycle, and Mode 4 blanks ~11 ms at each
  transition, so `swper=0.4` → 100 ms/phase → 11% blanked and ASTRID warns.
  Both bands now use `swper=0.8` (200 ms/phase, ~5.5%) with `tint=1.6`.
