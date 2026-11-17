# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# Ku-band (13 GHz) VEGAS configuration:  NaCl v=0 J=1-0  (EMISSION)
# =====================================================================
# VEGAS Mode 4, 187.5 MHz bandwidth, 32768 channels -> 5.722 kHz
# (0.13 km/s at 13 GHz), FOUR spectral windows, both Ku beams,
# in-band frequency switching.
#
# !! ASTRID RULE !!  Configure() evaluates each "keyword = value" line in its
# OWN namespace, so a value may NOT refer to another keyword.  Both
#     swfreq = 0.0, bandwidth*2**-4
#     swfreq = 0.0, bandwidth[0]*2**-4
# fail with "NameError: name 'bandwidth' is not defined".  Use literals.
#
# !! ASTRID RULE !!  'bandwidth' is a SINGLE float and applies to every
# window; it may not be a comma-separated list even when restfreq is.
# (Per-window bandwidths require the advanced dictionary restfreq syntax.)
# =====================================================================

receiver  = 'Rcvr12_18'     # Ku-band receiver (12-18 GHz), dual-beam
beam      = '1,2'           # BOTH beams.  'beam' takes comma-separated
                            # integers -- 'B12' is not a legal value.
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# 4-window setup, replicated to both beams.  NaCl is the top priority.
#   W1  13085.66  NaCl v=0 1-0 (13026.061, -59.6 MHz), H79a/He79a (13088.85 /
#                 13094.18, +3.2 / +8.5 MHz), H2C18O 2(1,1)-2(1,2) (13166.04,
#                 +80.4 MHz).  The +5.86 MHz VEGAS spike falls midway between
#                 H79a and He79a (61 km/s from each).
#   W2  14516.0   H2CO 2(1,1)-2(1,2) at -27.5 MHz, so the whole Sgr B2
#                 absorption complex (14486.7-14492.9, -91..+37 km/s) is clear
#                 of the spike (+/-5.86) and its FSW images (+/-17.58).
#   W3  13753.8   H2(13)CO 2(1,1)-2(1,2) at +25.0 MHz (same reason).
#                 Replaces H77a/He77a (14128.61/14134.36), no longer observed.
#   W4  12916.41  vibrationally excited NaCl 12929.260 (+12.8 MHz) and
#                 12833.076 (-83.3 MHz).
# With the symmetric swfreq below, each window keeps center +/-87.89 MHz in
# band in BOTH FSW states, for either sign of the throw:
#   W4 12828.52-13004.30, W1 12997.77-13173.55 -> 6.5 MHz overlap, so there is
#   no gap between NaCl v=2 and H2C18O.  NaCl v=2 (+/-30 km/s) is 3.3 MHz and
#   H2C18O 6.7 MHz inside their edges; NaCl 1-0 is 27.5 MHz inside.
# line_plan.py holds the line extents; validate_scripts.py checks every target
# against the band edges, the VEGAS center spike and the spike's FSW images.
# below 12706 RFI gets super ratty (in PRIMOS)
#
# NOTE: 4 windows x 2 beams = 8 VEGAS banks.  A dual-beam receiver is limited
# to 4 banks per beam, so this is exactly at the limit -- no room for a 5th
# window without dropping to a single beam.
restfreq  = 13085.66, 14516.0, 13753.8, 12916.41
bandwidth = 187.5           # MHz (VEGAS Mode 4), single value for all windows
dopplertrackfreq = 13026.061   # NaCl 1-0 (not window 1's center, 13085.66)
                            # CHECK: 13026.061
nchan     = 32768           # -> 5.722 kHz = 0.13 km/s at 13 GHz

# In-band frequency switching
swmode    = 'sp'            # switched power WITH cal
swtype    = 'fsw'           # REQUIRED to actually frequency switch when
                            # swmode='sp'; without it nothing is switched.
swper     = 0.8             # full switching cycle (s).  4 phases -> 200 ms
                            # each; VEGAS blanks ~11 ms (the Mode 4 minimum
                            # integration) at every phase transition, so this
                            # loses ~5.5%.  swper=0.4 gave 100 ms phases and
                            # tripped ASTRID's ">10% of your data will be
                            # blanked in BankX using mode MODE4" warning.
swfreq    = -5.859375, 5.859375   # CHECK: (-bandwidth*2**-5, bandwidth*2**-5)
                            # CHECK: (-1024*chanwidth, 1024*chanwidth)
                            # SYMMETRIC about restfreq (the GBT default form,
                            # -/+ 0.25*bandwidth, scaled down).  Two reasons:
                            # (1) the band kept in BOTH phases is
                            #     restfreq +/- (93.75 - 5.86) = +/-87.89 MHz
                            #     whatever the sign convention of the throw;
                            #     with 0, +11.72 it is only +/-82.03 MHz unless
                            #     the sign is known.
                            # (2) VEGAS has a spike at the exact center of the
                            #     passband (GBT docs: VEGAS > Instrumental
                            #     Features).  With a 0 offset, a line at
                            #     restfreq sits on it in one phase; here the
                            #     spike lands at restfreq -/+ 5.86 MHz.
                            # The throw (difference) is unchanged: 11.71875 MHz.
                            # throw = 187.5/16 MHz = exactly 2048 channels of
                            # 5.722 kHz = 270 km/s at 13.026 GHz.
                            # Known bright line at 13043 (+17 MHz) is _just_
                            # missed.  Recommended value in the configure docs:
                            # https://gbtdocs.readthedocs.io/en/latest/references/observing/configure.html#swfreq-float-float
tint      = 1.6             # CHECK: 2*swper
                            # dump time.  At 6'/48.5 s = 7.42"/s
                            # -> 11.9"/sample, still inside FWHM/4 (14.2").
                            # VEGAS Mode 4 minimum is 11 ms.
                            # 8-bank data rate at tint=1.6: ~5.2 MB/s = ~19 GB/hr.
                            # "the integration time (tint), switching period
                            #  (swper), and the frequency switching offset
                            #  (swfreq) values must each be the same for all
                            #  banks."

vlow      = 0
vhigh     = 0
vframe    = 'lsrk'          # LSR kinematic (standard for Galactic work)
vdef      = 'Radio'
noisecal  = 'lo'
pol       = 'Circular'      # Rcvr12_18 has cooled polarizers producing
                            # CIRCULAR polarization -- 'Linear' is wrong here.

# ---------------------------------------------------------------------
# Ku-band line reference (MHz, LSR rest):
#   NaCl v=0 1-0  13026.061   <-- PRIMARY target (emission)
#   [window 1 spans 12991.91-13179.41 MHz: NaCl 1-0, H79a, He79a, H2C18O]
# Beam FWHM ~ 57" at 13 GHz.
#
# NOTE: the two Ku feeds are separated by 330" (5.5') in cross-elevation, so
# with beamName='1' in the map scans, beam 2 sweeps a 6'x6' patch ~5.5' away
# from Sgr B2(N) -- it does not add sensitivity on target.
# ---------------------------------------------------------------------
