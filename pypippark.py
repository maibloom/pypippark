#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import getpass

# ─── CONFIG ────────────────────────────────────────────────────────────────
VENV_PATH = "/usr/local/bin/pypippark-dep"
SYSTEM_PY = sys.executable   # e.g. /usr/bin/python3
# ──────────────────────────────────────────────────────────────────────────

def ensure_venv(path):
    """
    1) Create the venv if missing
    2) Fix ownership/permissions so non-root installs work subsequently
    3) Return (python_bin, pip_bin) inside the venv
    """
    if not os.path.isdir(path):
        print(f"> Creating virtualenv at {path!r}")
        subprocess.run([SYSTEM_PY, "-m", "venv", path], check=True)

    # If we can’t write, and we’re root, chown it to the invoking user
    if not os.access(path, os.W_OK):
        if os.geteuid() != 0:
            sys.exit(f"✋ Permission denied on {path!r}; run as root once or fix perms")
        user = getpass.getuser()
        print(f"> Adjusting ownership of {path!r} → {user}:{user}")
        subprocess.run(["chown", "-R", f"{user}:{user}", path], check=True)

    py_bin  = os.path.join(path, "bin", "python3")
    pip_bin = os.path.join(path, "bin", "pip")
    return py_bin, pip_bin

def activate_env(path):
    """
    Return a copy of os.environ “inside” the venv:
      - VIRTUAL_ENV
      - PATH is prefixed with venv/bin
      - PYTHONHOME is removed
    """
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = path
    env["PATH"] = os.path.join(path, "bin") + os.pathsep + env.get("PATH", "")
    env.pop("PYTHONHOME", None)
    return env

def cmd_install(pkgs):
    py, pip = ensure_venv(VENV_PATH)
    cmd = [pip, "install"] + pkgs
    print("> ▶️", " ".join(cmd))
    subprocess.run(cmd, env=activate_env(VENV_PATH), check=True)
    print(f"✅ Installed {', '.join(pkgs)} into {VENV_PATH}")
    print("> 🔚 Deactivated venv (returned to system environment)")


def cmd_run(script, script_args):
    py, _ = ensure_venv(VENV_PATH)
    if not os.path.isfile(script):
        sys.exit(f"✋ Script not found: {script}")
    cmd = [py, script] + script_args
    print("> ▶️", " ".join(cmd))
    subprocess.run(cmd, env=activate_env(VENV_PATH), check=True)
    print(f"> 🔚 Finished running {script!r}")

def main():
    p = argparse.ArgumentParser(
        prog="pypippark",
        description="Manage a single, system‐wide venv at /usr/local/bin/pypippark-dep"
    )
    subs = p.add_subparsers(dest="cmd", required=True)

    ins = subs.add_parser("install", help="Install packages into the pypippark venv")
    ins.add_argument("pkgs", nargs="+", help="package names (pip syntax)")

    run = subs.add_parser("run", help="Run a Python script inside the pypippark venv")
    run.add_argument("script", help="path to the .py file")
    run.add_argument("args", nargs=argparse.REMAINDER,
                     help="arguments to pass to the script")

    args = p.parse_args()
    if args.cmd == "install":
        cmd_install(args.pkgs)
    elif args.cmd == "run":
        cmd_run(args.script, args.args)

if __name__ == "__main__":
    main()
