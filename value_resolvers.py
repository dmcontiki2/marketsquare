"""DEPRECATED shim — superseded by tier_resolvers.py.

During the STEP 3-5 build the original module name hit a sandbox mount-coherency
glitch, so the module was re-authored as ``tier_resolvers.py``. This shim only
re-exports it so any stray ``import value_resolvers`` keeps working. bea_main.py
imports ``tier_resolvers`` directly; this file is NOT deployed. Safe to
``git rm`` once nothing references the old name.
"""
from tier_resolvers import *  # noqa: F401,F403
