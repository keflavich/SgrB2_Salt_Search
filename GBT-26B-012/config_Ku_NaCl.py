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
#   W1  13058.79  centered between NaCl v=0 1-0 (13026.061, -32.7 MHz) and the
#                 H79a/He79a pair (13088.85 / 13094.18, +30 / +35 MHz).  Putting
#                 the pair's midpoint (13091.52) and NaCl in ONE window keeps
#                 NaCl well off the band edge; centering on NaCl instead would
#                 leave H/He79a 63-68 MHz out, with the FSW image at ~80 MHz.
#   W2  14488.479 H2CO 2(1,1)-2(1,2).  (H2(13)CO 2(1,1)-2(1,2) is at 13778.804,
#                 710 MHz away -- not reachable in this window.)
#   W3  14131.49  centered between H77a (14128.61) and He77a (14134.36).
#   W4  12881.17  centered between the two vibrationally excited NaCl lines,
#                 12929.260 (+48 MHz) and 12833.076 (-48 MHz).
# All lines sit inside +/-82 MHz of their window center, so both FSW phases
# (throw 11.72 MHz) keep them in band.
# below 12706 RFI gets super ratty (in PRIMOS)
#
# NOTE: 4 windows x 2 beams = 8 VEGAS banks.  A dual-beam receiver is limited
# to 4 banks per beam, so this is exactly at the limit -- no room for a 5th
# window without dropping to a single beam.
restfreq  = 13058.79, 14488.479, 14131.49, 12881.17
bandwidth = 187.5           # MHz (VEGAS Mode 4), single value for all windows
dopplertrackfreq = 13026.061   # NaCl 1-0 (not window 1's center, 13058.79)
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
swfreq    = 0.0, 11.71875   # CHECK: (0.0, bandwidth*2**-4)
                            # CHECK: (0.0, 2048*chanwidth)
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
#   [window 1 spans ~12965-13152 MHz: NaCl 1-0, H79a, He79a]
# Beam FWHM ~ 57" at 13 GHz.
#
# NOTE: the two Ku feeds are separated by 330" (5.5') in cross-elevation, so
# with beamName='1' in the map scans, beam 2 sweeps a 6'x6' patch ~5.5' away
# from Sgr B2(N) -- it does not add sensitivity on target.
# ---------------------------------------------------------------------
