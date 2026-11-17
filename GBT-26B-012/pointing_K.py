# GBT-26B-012 -- K-band (KFPA) pointing & focus.  Run at the start of each
# session and again between maps (~every 30-45 min); K-band needs more
# frequent pointing than Ku, especially at Sgr B2's low elevation and during
# the day.
#
# This is a STANDALONE scheduling block: it does pointing/focus and nothing
# else.  Mapping lives in map_K_NaCl_RaLongMap.py / map_K_NaCl_DecLatMap.py,
# which Configure, Slew and Balance for themselves.  Keeping them separate
# means that if a map fails to Balance, or has to be aborted, only the map SB
# is re-run -- the point/focus is not repeated.

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")

# AutoPeakFocus runs its own continuum configuration, so do NOT Configure first.
# location="SgrB2M" makes it slew to the neighborhood of Sgr B2 and pick the
# pointing/focus calibrator close to it (important: Sgr B2 is low in the sky,
# so a calibrator picked without regard to the science position can be far away
# in azimuth/elevation).  frequency (MHz) matches the pointing model to the
# science band.  [Suggestion from Tony.]
AutoPeakFocus(location="SgrB2M", frequency=26051.9, beamName="1")

# ALWAYS reconfigure after AutoPeakFocus so the system is never left in its
# continuum pointing configuration.  The map SB configures again itself; this
# is just to leave things in a safe state.
Configure(PROJPATH + "/config_K_NaCl.py")

# NOTE: KFPA noise-diode strengths drift between sessions -- do a KFPA
# calibration observation once per session so Ta* scaling is reliable across
# all 7 beams.  (See the KFPA Observer's Guide; typically a short scan on a
# cal source.)
