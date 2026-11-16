# Missing installed scenario preflight — 2026-11-16

A user launch found the new Python source but failed to find the newly added
installed `scenario_compact.json`. The launch wrapper now checks the selected
installed configuration before creating a run folder and explicitly directs the
user to **01 Build visual demo** / `bash tools/workbench.sh build`.

Targeted reproduction in the disposable Humble execution copy temporarily moved
only the installed compact-config symlink (the source JSON was preserved).
The new preflight exited 2 with the expected rebuild message, no traceback and
no new run directory. Running the ordinary two-package workbench build restored
the symlink; all three installed JSON configurations parsed successfully:
compact, tiered and precision. The temporary backup link was removed afterward.
The scoped build completed both packages. Shell syntax, documentation links and
source inventory checks passed. No motion code changed or fresh full-cycle
acceptance is claimed by this packaging diagnostic.
