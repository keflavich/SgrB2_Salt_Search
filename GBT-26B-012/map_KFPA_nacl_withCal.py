"""
GBT-26B-012 -- KFPA (26 GHz) NaCl v=0 J=2-1 OTF map of Sgr B2 (centered on Sgr B2 M).

Target: map the NaCl 2-1 ABSORPTION against the Sgr B2 continuum and
localize which continuum sources it absorbs against.  Config: VEGAS Mode 4,
single 187.5 MHz window on NaCl v=0 2-1, all 7 KFPA beams, in-band freq sw.

6'x6' map at 26.052 GHz (KFPA, all 7 beams):
    FWHM 28.5" | slew 3.71"/s
    row separation 13.85" = FWHM/2 (Nyquist)  ->  27 rows | 97.0 s/row
    ==> 43.7 min on-source per (single-direction) map.
Sample spacing along the scan is 5.9" < FWHM/4 (7.1") at tint=1.6 s, so
every one of the 7 beams fully samples the map on its own.

10-sigma on the ~15 mK peak => ~3 mK/beam.  Integration per sky point scales
with map duration, so the invariant is TOTAL on-source hours, not the map
count: N_maps = (total on-source time) / 43.7 min.  Multiply any map count
tracked against the old 22-row / 35.6-min geometry by 35.6/43.7 = 0.82.

POINTING IS NOT DONE IN THIS SB.  AutoPeakFocus lives in pointing_K.py so
that a failed Balance or an aborted map never costs a repeated point/focus.
The normal KFPA sequence is one map per pointing, alternating direction:

    pointing_K.py  ->  map_K_NaCl_RaLongMap.py
    pointing_K.py  ->  map_K_NaCl_DecLatMap.py     (repeat)

This SB is the OPTIONAL variant that runs maps_per_block maps back to back
with no re-pointing in between.  At 26 GHz and Sgr B2's low elevation that is
only advisable when pointing is known to be stable; the default of 2 gives a
balanced RA+Dec pair but leaves ~87 min between point/focus solutions.
"""

# assumed to be the same as last time I observed a decade ago...
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_K_NaCl.py")

# ---- map geometry (KFPA, 7 beams) ----
mapsize  = 6/60.          # 0.1 deg square
# Rows must be <= FWHM/2 = 14.2" apart (FWHM 28.5" at 26.05 GHz) for each
# beam to fully sample the map on its own.  mapsize/26 = 13.85" satisfies
# that AND gives exactly 27 rows (mapsize/rowsep + 1), so the map edge lands
# where intended.  The old 51.43/3 = 17.14" was 20% coarser than Nyquist and
# produced a ragged 21.9994 rows.
rowsep   = mapsize / 26.  # 13.85" -> 27 rows, fully sampled in every beam
scanDur  = 97.0           # s per row (6' / 3.71"/s); at tint=1.6 s that is
                          # 5.9"/sample, inside FWHM/4 = 7.1"
# 27 rows x 97 s = 43.7 min of on-sky time per map, plus turnarounds.

# ---- how many maps before handing back for a re-point ----
maps_per_block = 2        # RA + Dec = ~87 min; end the SB, then re-point.

Slew("SgrB2M")
Balance()

for ii in range(maps_per_block):

    # ALTERNATE orthogonal scan directions (basketweave):
    if ii % 2 == 0:
        # RA-scanned rows, stepped in Dec:
        RALongMap("SgrB2M",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
    else:
        # Dec-scanned rows, stepped in RA (orthogonal to the above):
        DecLatMap("SgrB2M",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
