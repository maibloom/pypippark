#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import getpass

# ─── CONFIG ────────────────────────────────────────────────────────────────
# Always keep the venv under the current user's home
VENV_PATH  = os.path.expanduser("~/.local/share/pypippark-dep")
SYSTEM_PY  = sys.executable            # e.g. /usr/bin/python3
LOG_PREFIX = "[pypippark] "            # Unified log prefix
# ──────────────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    """ Unified logging with emojis. """
    icons = {
        "INFO":    "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR":   "❌"
    }
    emoji = icons.get(level, "")
    print(f"{LOG_PREFIX}{emoji} {msg}")

def ensure_venv(path):
    """
    1) Create venv if it doesn't exist.
    2) If root owns it and you're running as root, chown to your user.
    3) Return (python3_bin, pip_bin) inside that venv.
    """
    if not os.path.isdir(path):
        log(f"Creating virtualenv at {path}", "INFO")
        subprocess.run([SYSTEM_PY, "-m", "venv", path], check=True)

    # If venv directory isn’t writable and we’re root, hand it off to real user
    if not os.access(path, os.W_OK) and os.geteuid() == 0:
        user = getpass.getuser()
        log(f"Fixing ownership on {path} → {user}:{user}", "WARNING")
        subprocess.run(["chown", "-R", f"{user}:{user}", path], check=True)

    python_bin = os.path.join(path, "bin", "python3")
    pip_bin    = os.path.join(path, "bin", "pip")
    return python_bin, pip_bin

def activate_env(path):
    """
    Return a copy of os.environ configured to use the venv:
      - VIRTUAL_ENV
      - PATH with venv/bin first
      - no PYTHONHOME
    """
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = path
    env["PATH"] = os.path.join(path, "bin") + os.pathsep + env.get("PATH", "")
    env.pop("PYTHONHOME", None)
    return env

def cmd_install(pkgs):
    """ Install one or more packages into the venv. """
    _, pip = ensure_venv(VENV_PATH)
    log(f"Installing {', '.join(pkgs)} …", "INFO")
    subprocess.run([pip, "install"] + pkgs,
                   env=activate_env(VENV_PATH), check=True)
    log(f"Installed {', '.join(pkgs)}", "SUCCESS")

def cmd_list():
    """ List installed packages in the venv. """
    _, pip = ensure_venv(VENV_PATH)
    log("Listing installed packages …", "INFO")
    subprocess.run([pip, "list"],
                   env=activate_env(VENV_PATH), check=True)

def cmd_remove(pkgs):
    """ Uninstall one or more packages from the venv. """
    _, pip = ensure_venv(VENV_PATH)
    log(f"Removing {', '.join(pkgs)} …", "WARNING")
    subprocess.run([pip, "uninstall", "-y"] + pkgs,
                   env=activate_env(VENV_PATH), check=True)
    log(f"Removed {', '.join(pkgs)}", "SUCCESS")

def cmd_update():
    """ Upgrade pip, then find and upgrade all outdated packages. """
    _, pip = ensure_venv(VENV_PATH)
    env = activate_env(VENV_PATH)

    # 1) Upgrade pip itself
    log("Upgrading pip …", "INFO")
    subprocess.run([pip, "install", "--upgrade", "pip"],
                   env=env, check=True)

    # 2) Check for outdated packages
    log("Checking for outdated packages …", "INFO")
    proc = subprocess.run(
        [pip, "list", "--outdated", "--format=freeze"],
        capture_output=True, text=True, env=env
    )
    out = proc.stdout.strip()
    if not out:
        log("All packages are already up-to-date", "SUCCESS")
        return

    # 3) Parse names & batch-upgrade
    pkgs = [line.split("==")[0] for line in out.splitlines() if line]
    log(f"Upgrading {', '.join(pkgs)} …", "INFO")
    subprocess.run([pip, "install", "--upgrade"] + pkgs,
                   env=env, check=True)
    log("All packages updated", "SUCCESS")

def cmd_run(script, script_args):
    """ Run a .py script inside the venv. """
    python_bin, _ = ensure_venv(VENV_PATH)
    if not os.path.isfile(script):
        log(f"Script not found: {script}", "ERROR")
        sys.exit(1)

    log(f"Running {script!r} …", "INFO")
    subprocess.run([python_bin, script] + script_args,
                   env=activate_env(VENV_PATH), check=True)
    log(f"Finished {script!r}", "SUCCESS")

def main():
    parser = argparse.ArgumentParser(
        prog="pypippark",
        description="Manage your per-user venv at ~/.local/share/pypippark-dep"
    )
    subs = parser.add_subparsers(dest="cmd", required=True)

    i = subs.add_parser("install", help="Install packages")
    i.add_argument("pkgs", nargs="+", help="packages (pip syntax)")

    subs.add_parser("list", help="List installed packages")

    r = subs.add_parser("remove", help="Remove packages")
    r.add_argument("pkgs", nargs="+", help="packages to uninstall")

    subs.add_parser("update", help="Update all packages")

    run = subs.add_parser("run", help="Run a Python script inside the venv")
    run.add_argument("script", help="path to your .py file")
    run.add_argument("args", nargs=argparse.REMAINDER,
                     help="arguments to pass to the script")

    args = parser.parse_args()
    if args.cmd == "install":
        cmd_install(args.pkgs)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(args.pkgs)
    elif args.cmd == "update":
        cmd_update()
    elif args.cmd == "run":
        cmd_run(args.script, args.args)

if __name__ == "__main__":
    main()
