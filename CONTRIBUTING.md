# Contributing to CAMBOT

## Before your first commit

```bash
git config user.name  "Your Name"
git config user.email "you@example.com"
git lfs install
```

Git identity is needed to **commit**. GitHub credentials are needed to **push**.
They are separate — an unset identity will block a commit even when GitHub auth
is fine.

## Branches

```text
main
│
├── development
│
├── feature/kinematics
├── feature/control
├── feature/carrier-design
├── feature/simulation
└── feature/perception
```

- Never push experimental or broken code directly to `main`.
- Create a feature branch for any substantial work.
- Review before merging to `main`.

## Commit messages

```text
feat:     add inverse kinematics solver
fix:      correct transformation matrix
docs:     update system architecture
test:     add workspace validation
refactor: reorganize ROS packages
chore:    update gitignore
```

Keep commits small and meaningful. Avoid "Add files via upload" — commit from
the command line so history stays reviewable.

## What not to commit

Covered by `.gitignore`:

```text
__pycache__/  *.pyc  build/  install/  log/  .venv/
```

Large binaries (`*.csv`, `*.webm`, `*.docx`, `*.pptx`) route through Git LFS via
`.gitattributes`. Raw rosbags never go in the repository at all.

## Filenames

- Lowercase with hyphens for directories: `exp01-upper-arm-10pct/`
- **No spaces.** No colons — files like
  `Screencast from 08-28-2026 02:16:43 AM.webm` cannot be checked out on Windows.
- No trailing space before an extension (`task1_chat .md`).

## Documentation

- **Status goes in `docs/STATUS.md` only.** Do not duplicate progress tables
  into other files — they will contradict each other, and they already have.
- Write documentation for a reader, not as a chat transcript. No "Absolutely,
  here is…", no "in the next chat", no prompts addressed to an assistant.
- Record design decisions in `docs/DECISIONS.md` with the reasoning, not just
  the outcome.
- If a document describes code, that code must be committed. Prose describing
  uncommitted work is how Phase 4 ended up unreproducible.

## Portability

No absolute paths. Use ROS package discovery (`ament_index`, `$(find pkg)`) and
relative paths. Anyone with Ubuntu 22.04 + ROS 2 Humble should reproduce the
work from a fresh clone.

Verify with:

```bash
grep -rn "/home/" --include="*.py" --include="*.yaml" --include="*.xacro" .
```

## Before opening a PR

```bash
colcon build --symlink-install && source install/setup.bash
xacro src/carrier_description/urdf/<file>.xacro > /tmp/check.urdf
check_urdf /tmp/check.urdf
```

Confirm `docs/STATUS.md` reflects what you changed.
