# CAM-BOT presentation package

The project is complete for its accepted **visual ROS 2 demonstrator** scope.
Advanced Tasks 7–15 are future work, not prerequisites for presenting this result.

For live code execution, use [the VS Code tasks and setup guide](../docs/VSCODE.md).

## Open these first

- [Offline presentation with recorded-event replay](CAM-BOT.html): download and
  open in a browser; no server or internet required. Use arrow keys and N for notes.
- [Editable PowerPoint](CAM-BOT.pptx): 12 slides with speaker notes.
- [Static PDF](CAM-BOT.pdf): projector/printing fallback.
- [Speaker notes](speaker_notes.md): ten-minute narration and slide cues.
- [Demo guide](DEMO_GUIDE.md): prepared live RViz flow and fallback procedure.
- [How to present your run outputs](RESULTS_WALKTHROUGH.md): file order and talking points.
- [Final report](FINAL_REPORT.md) and [contribution record](CONTRIBUTIONS.md).

The HTML replay uses one archived trial's actual event times and states. Its
RViz image is a static recorded screenshot; the browser is not running ROS or
reconstructing robot motion. The measured results summarize the separate
five-trial qualified dataset. Supporting controller and CAD work is clearly
labelled as supplementary investigation.

GitHub does not execute HTML previews: download the file or open it from your
local checkout. If local-file navigation is restricted, run
`bash tools/workbench.sh presentation` and open
`http://127.0.0.1:8765/CAM-BOT.html`; this serves only the presentation folder on
your own machine and needs no internet. The HTML embeds its images and replay data; PowerPoint/PDF are
also self-contained. Source evidence stays in its original repository locations.

## Regenerate into a new directory

`python-pptx` 1.0.2 is used for PowerPoint generation; the Python standard library
builds HTML and notes. From repository root:

```bash
python tools/build_presentation.py --output /tmp/cambot-presentation-NEW
```

The output directory must not exist. The generator reads and hashes source
artifacts, checks that metrics identify the same raw inputs, and embeds the
first qualifying trial for replay. It never modifies sealed captures.
PDF is produced by printing the HTML in Chromium; browser automation validation
and the retained PDF were generated separately after checking navigation/replay.
Run `python tools/validate_presentation.py NEW_DIRECTORY --chromium /usr/bin/chromium`
with Playwright and PyMuPDF installed for the browser/PDF checks.
See `verification.json` for the exact checks and artifact hashes in `manifest.json`.

The live wrapper `bash tools/present_demo.sh` requires the already prepared
Humble GUI environment and installed core packages. No fresh ROS/RViz runtime
pass is claimed solely from creating this presentation. The previous accepted
runtime and human-review evidence remain the baseline.
