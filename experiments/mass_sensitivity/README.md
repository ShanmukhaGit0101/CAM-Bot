# Mass Sensitivity Experiments

Three 10% link-mass perturbations of the UR5, comparing recorded joint
trajectory statistics against an unmodified baseline run of the machine-shop
cycle.

| ID | Link | Baseline | Perturbed | Δ |
|---|---|---:|---:|---:|
| EXP01 | Upper arm | 8.3930 kg | 9.2323 kg | +0.8393 kg |
| EXP02 | Forearm | 2.3300 kg | 2.5630 kg | +0.2330 kg |
| EXP03 | Shoulder | 3.7000 kg | 4.0700 kg | +0.3700 kg |

Full analysis:
[`docs/progress/phase2-mass-sensitivity.md`](../../docs/progress/phase2-mass-sensitivity.md)

---

## ⚠️ How to read these results

Baseline and experiment recordings have **different sample counts and
durations** and are not time-aligned. Acceleration is obtained by applying
`numpy.gradient` twice to position.

These are therefore **trajectory-statistic comparisons**, not point-by-point
trajectory error, and not measurements of torque, motor current, or physical
acceleration capability. Percentage changes in the hundreds reflect
differentiation noise, not dynamics.

---

## Directory layout

Each experiment follows the same structure:

```text
expNN-<link>-10pct/
├── params/       physical_parameters_*.yaml    mass values used
├── urdf/         perturbed and baseline URDFs
├── scripts/      extraction, analysis, plotting
├── data/         raw /joint_states CSV          (Git LFS)
├── plots/        generated figures
└── results/      numerical comparisons, bag metadata
```

## Reproducing

```bash
cd exp01-upper-arm-10pct
python3 scripts/extract_joint_states.py     # bag → CSV
python3 scripts/compare_exp01.py            # numerical comparison
python3 scripts/compare_exp01_plots.py      # figures
```

Script names differ slightly per experiment — see each `scripts/` directory.

**Environment note.** Plotting requires a matching NumPy/matplotlib pair. A
NumPy 2.x system install against an apt matplotlib built for NumPy 1.x produces
`_ARRAY_API not found` and `Unknown projection '3d'`. Use an isolated venv with
NumPy 1.26.4 and matplotlib 3.10.9.

## Known gaps

- `exp03` is missing `physical_parameters_baseline.yaml` — it has only the
  perturbed parameters. The baseline values are recoverable from `exp01`/`exp02`.
- Baseline metadata sits in `results/` for exp01 and exp03 but at the package
  root for exp02.
- exp01 and exp02 carry three URDFs each; exp03 carries one.
- `exp02` has a `summary.txt`; the others do not.

These are cosmetic but should be normalized before the dataset is cited in a
report.
