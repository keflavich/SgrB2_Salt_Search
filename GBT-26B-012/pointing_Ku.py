# GBT-26B-012 -- Ku-band pointing & focus.  Run at the start of each session
# and again between map blocks (~every 30-60 min, or after a large slew /
# elevation change).  Sgr B2 transits at low elevation from Green Bank, so
# point/focus often.
#
# This is a STANDALONE scheduling block: it does pointing/focus and nothing
# else.  Mapping lives in map_Ku_NaCl_withCal.py (and the single-direction
# map_Ku_NaCl_RaLongMap.py / map_Ku_NaCl_DecLatMap.py), which Configure, Slew
# and Balance for themselves.  Keeping them separate means that if a map fails
# to Balance, or has to be aborted, only the map SB is re-run -- the
# point/focus is not repeated.

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")

# AutoPeakFocus runs its own continuum configuration, so do NOT Configure first.
# location="SgrB2N" makes it slew to the neighborhood of Sgr B2 and pick the
# pointing/focus calibrator close to it (important: Sgr B2 is low in the sky,
# so a calibrator picked without regard to the science position can be far away
# in azimuth/elevation).  frequency (MHz) matches the pointing model to the
# science band.  [Suggestion from Tony.]
AutoPeakFocus(location="SgrB2N", frequency=13026.0, beamName="1")

# ALWAYS reconfigure after AutoPeakFocus so the system is never left in its
# continuum pointing configuration.  The map SB configures again itself; this
# is just to leave things in a safe state.
Configure(PROJPATH + "/config_Ku_NaCl.py")
