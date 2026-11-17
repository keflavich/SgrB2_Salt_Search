"""
GBT-26B-012 -- Ku-band (13 GHz) NaCl v=0 J=1-0 OTF map of Sgr B2 (centered on Sgr B2 M).

6'x6' map at 13.026 GHz:
    FWHM 56.7" | slew 7.42"/s
    row separation 24"  ->  16 rows | scanDuration 48.5 s/row
    ==> 12.9 min on-source per (single-direction) map.

Proposal plan (GBT-26B-012): 10-sigma on the ~30 mK peak => ~3 mK/beam
=> ~2500 s/beam => 131 maps => ~28 h on-source, ~36 h w/ overhead,
12 x 3 h sessions (~11 maps/session).

Config: VEGAS Mode 4, single 187.5 MHz window on NaCl v=0 1-0, both Ku beams,
in-band freq sw.

POINTING IS NOT DONE IN THIS SB.  AutoPeakFocus lives in pointing_Ku.py so
that a failed Balance or an aborted map never costs a repeated point/focus.
Each run of this SB is one pointing-free block of maps_per_block maps, which
alternate RA- and Dec-scanned passes to basketweave:

    pointing_Ku.py  ->  map_Ku_NaCl_withCal.py     (repeat)

maps_per_block = 2 keeps the RA/Dec pair balanced and puts ~26 min of mapping
between point/focus solutions, which suits Sgr B2's low elevation.  Raise it
to 4 (~52 min) in stable conditions; keep it EVEN so the two scan directions
stay balanced.

Track the cumulative map count toward 131 across sessions.
"""

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_Ku_NaCl.py")

# ---- calculator-matched geometry ----
arcsec   = 1/3600.
mapsize  = 6/60.          # 0.1 deg square (encompasses N, M, G0.693)
rowsep   = 24.0*arcsec    # Nyquist at 57" beam -> 16 rows over 6'
scanDur  = 48.5           # s per row (6' / 7.42"/s)

# ---- how many maps before handing back for a re-point ----
maps_per_block = 2        # RA + Dec = ~26 min; end the SB, then re-point.

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
