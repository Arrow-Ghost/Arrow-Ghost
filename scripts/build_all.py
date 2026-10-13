"""Rebuild every static graphic in assets/.

    python scripts/build_all.py

Telemetry (assets/telemetry.svg, assets/langs.svg) is rebuilt separately by
scripts/generate_stats.py, which the telemetry workflow runs on a schedule.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

BUILDERS = ["build_hero", "build_headers", "build_buttons", "build_terminal", "build_arsenal",
            "build_projects", "build_archive", "build_readme"]

env = dict(os.environ, PYTHONIOENCODING="utf-8")
failed = []
for name in BUILDERS:
    path = os.path.join(HERE, name + ".py")
    if not os.path.exists(path):
        print(f"skip {name} (missing)")
        continue
    print(name)
    if subprocess.run([sys.executable, path], cwd=HERE, env=env).returncode:
        failed.append(name)

if failed:
    sys.exit("failed: " + ", ".join(failed))
