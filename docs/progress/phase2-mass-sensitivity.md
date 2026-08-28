# Phase 2 — UR5 Mass Sensitivity Study

**Status:** ✅ Complete (EXP01–03)
**Question:** how does adding mass at different locations along the UR5 serial
chain affect the recorded joint trajectory statistics of the machine-shop cycle?

---

## 1. Method

For each experiment, one link's mass is increased by **10%** in the URDF. The
standard machine-shop cycle is then run and `/joint_states` is recorded, and the
resulting trajectory statistics are compared against an unmodified baseline run.

**Metrics per joint:**

- position range
- maximum absolute velocity
- maximum absolute acceleration

Velocity and acceleration are **numerically derived**, not measured:

```text
position --numpy.gradient--> velocity --numpy.gradient--> acceleration
```

---

## 2. Read this before interpreting any number below

Baseline and experiment recordings have **different sample counts and
durations**. They are not time-aligned.

Consequently these are **trajectory-statistic comparisons**, not point-by-point
trajectory error. Double numerical differentiation of unsynchronized recordings
amplifies sampling noise substantially, which is why the acceleration column
swings by hundreds of percent while position barely moves at all.

These results must **not** be read as measurements of:

- actuator torque
- motor current
- physical acceleration capability

They describe how the *recorded motion statistics* shifted. Nothing more.
Treating the acceleration deltas as dynamics results would be a serious
overclaim.

---

## 3. EXP01 — Upper arm +10%

```text
upper_arm_link:  8.3930 kg → 9.2323 kg   (+0.8393 kg)
```

| Dataset | Samples | Duration | Rate |
|---|---:|---:|---:|
| Baseline | 46 318 | 463.424 s | ~99.945 Hz |
| Experiment | 50 652 | 506.785 s | ~99.946 Hz |

| Joint | Δ position range | Δ max velocity | Δ max acceleration |
|---|---:|---:|---:|
| Shoulder pan | 0.000% | +0.207% | −1.350% |
| Shoulder lift | 0.000% | 0.000% | −1.640% |
| Elbow | 0.000% | 0.000% | −0.798% |
| Wrist 1 | 0.000% | 0.000% | −8.980% |
| Wrist 2 | 0.000% | 0.000% | −0.569% |
| Wrist 3 | 0.000% | 0.000% | −11.407% |

Position envelope unchanged; velocity effectively unchanged; acceleration
changes small, largest at the distal wrist joints.

---

## 4. EXP02 — Forearm +10%

```text
forearm:  2.3300 kg → 2.5630 kg   (+0.2330 kg)
```

| Dataset | Samples | Duration |
|---|---:|---:|
| Baseline | 46 318 | 463.424 s |
| Experiment | 46 085 | 461.082 s |

| Joint | Δ position range | Δ max velocity | Δ max acceleration |
|---|---:|---:|---:|
| Shoulder pan | −0.00% | −0.07% | +95.13% |
| Shoulder lift | +0.14% | +4.95% | +292.12% |
| Elbow | −0.02% | +7.45% | +355.48% |
| Wrist 1 | −0.10% | +31.99% | +478.34% |
| Wrist 2 | +0.03% | +40.66% | +517.48% |
| Wrist 3 | +0.01% | −0.05% | −34.18% |

Position envelope essentially unchanged. Velocity changes grow toward the distal
joints. The acceleration column shows very large values — see §2. A +517%
derived acceleration change from a 233 g mass increase is far more likely to be
a differentiation artifact than a physical effect, and should be stated that way
in any report.

---

## 5. EXP03 — Shoulder +10%

```text
shoulder:  3.7000 kg → 4.0700 kg   (+0.3700 kg)
other links unchanged:  upper arm 8.3930 kg,  forearm 2.3300 kg
```

| Dataset | Samples | Duration |
|---|---:|---:|
| Baseline | 46 318 | 463.424 s |
| Experiment | 46 218 | 462.405 s |

| Joint | Δ position range | Δ max velocity | Δ max acceleration |
|---|---:|---:|---:|
| Shoulder pan | −0.00% | −1.71% | −49.08% |
| Shoulder lift | +0.14% | +2.93% | −33.99% |
| Elbow | −0.02% | −3.95% | −40.46% |
| Wrist 1 | −0.10% | −3.23% | −39.78% |
| Wrist 2 | +0.03% | −3.28% | −40.43% |
| Wrist 3 | 0.00% | −1.89% | −49.07% |

Uniquely, **all six joints** show reduced derived peak acceleration, in a
consistent 34–49% band.

---

## 6. Conclusions

Across all three perturbations:

> Mass perturbation did not substantially alter the overall position envelope,
> while velocity and especially numerically derived acceleration statistics
> showed joint-dependent changes.

Two observations worth keeping:

1. **Serial-chain coupling.** Changing one link's mass shifts motion statistics
   at joints other than the one modified — including proximal joints. This is
   expected for a serial manipulator and is visible in all three experiments.
2. **The position envelope is robust.** The cycle reaches the same places
   regardless. For a carrier whose job is repeatable positioning, this is the
   result that actually matters.

---

## 7. Why there is no EXP04

Three perturbations covering proximal (shoulder), mid (upper arm), and distal
(forearm) links are sufficient to characterize the trend. A fourth would add
another point to a noisy dataset without answering a new question.

The binding constraint on the project is architectural — the CA → CF → BM
interface — not UR5 dynamics. See [`DECISIONS.md`](../DECISIONS.md) §D-03.

---

## 8. Reproducing

```bash
cd experiments/mass_sensitivity/exp01-upper-arm-10pct
python3 scripts/extract_joint_states.py     # bag → CSV
python3 scripts/compare_exp01.py            # numerical comparison
python3 scripts/compare_exp01_plots.py      # figures
```

Each experiment directory contains `params/`, `urdf/`, `scripts/`, `data/`,
`plots/`, and `results/`. See
[`experiments/mass_sensitivity/README.md`](../../experiments/mass_sensitivity/README.md).

**Next:** [Phase 4 — Carrier flange](phase4-carrier-flange.md)
