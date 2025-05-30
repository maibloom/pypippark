#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import getpass

# ─── CONFIG ────────────────────────────────────────────────────────────────
VENV_PATH = "/usr/local/bin/pypippark-dep"
SYSTEM_PY = sys.executable  # e.g. /usr/bin/python3
LOG_PREFIX = "[pypippark] "  # Unified log prefix
# ──────────────────────────────────────────────────────────────────────────


def log(msg, level="INFO"):
    """ Unified logging function for all messages. """
    levels = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    emoji = levels.get(level, "❔")
    print(f"{LOG_PREFIX}{emoji} {msg}")


def ensure_venv(path):
    """ Ensure the venv exists and fix permissions if needed. """
    if not os.path.isdir(path):
        log(f"Creating virtualenv at {path!r}", "INFO")
        subprocess.run([SYSTEM_PY, "-m", "venv", path], check=True)

    # Fix ownership if running as root
    if not os.access(path, os.W_OK) and os.geteuid() == 0:
        user = getpass.getuser()
        log(f"Adjusting ownership of {path!r} → {user}:{user}", "WARNING")
        subprocess.run(["chown", "-R", f"{user}:{user}", path], check=True)

    return os.path.join(path, "bin", "python3"), os.path.join(path, "bin", "pip")


def activate_env(path):
    """ Return a copy of os.environ “inside” the venv. """
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = path
    env["PATH"] = os.path.join(path, "bin") + os.pathsep + env.get("PATH", "")
    env.pop("PYTHONHOME", None)
    return env


def cmd_install(pkgs):
    """ Install packages into the venv. """
    _, pip = ensure_venv(VENV_PATH)
    cmd = [pip, "install"] + pkgs
    log(f"Installing {', '.join(pkgs)}...", "INFO")
    subprocess.run(cmd, env=activate_env(VENV_PATH), check=True)
    log(f"Installed {', '.join(pkgs)} successfully!", "SUCCESS")


def cmd_list():
    """ List installed packages in the venv. """
    _, pip = ensure_venv(VENV_PATH)
    log("Listing installed packages...", "INFO")
    subprocess.run([pip, "list"], env=activate_env(VENV_PATH), check=True)


def cmd_remove(pkgs):
    """ Uninstall packages from the venv. """
    _, pip = ensure_venv(VENV_PATH)
    cmd = [pip, "uninstall", "-y"] + pkgs
    log(f"Removing {', '.join(pkgs)}...", "WARNING")
    subprocess.run(cmd, env=activate_env(VENV_PATH), check=True)
    log(f"Removed {', '.join(pkgs)} successfully!", "SUCCESS")


def cmd_update():
    """ Update pip itself, then all other outdated packages in the venv. """
    _, pip = ensure_venv(VENV_PATH)
    env = activate_env(VENV_PATH)

    # 1) Upgrade pip
    log("Upgrading pip...", "INFO")
    subprocess.run([pip, "install", "--upgrade", "pip"], env=env, check=True)

    # 2) List outdated packages in freeze format
    log("Checking for outdated packages…", "INFO")
    proc = subprocess.run(
        [pip, "list", "--outdated", "--format=freeze"],
        capture_output=True, text=True, env=env  # no check=True
    )

    # 3) Parse the output
    out = proc.stdout.strip()
    if not out:
        log("All packages are already up-to-date.", "SUCCESS")
        return

    pkgs = [line.split("==")[0] for line in out.splitlines() if line]
    log(f"Upgrading: {', '.join(pkgs)}", "INFO")

    # 4) Batch-upgrade the outdated packages
    subprocess.run([pip, "install", "--upgrade"] + pkgs, env=env, check=True)
    log("All packages updated successfully!", "SUCCESS")




def cmd_run(script, script_args):
    """ Run a Python script inside the venv. """
    py, _ = ensure_venv(VENV_PATH)
    if not os.path.isfile(script):
        log(f"Script not found: {script}", "ERROR")
        sys.exit(1)
    log(f"Running {script!r}...", "INFO")
    subprocess.run([py, script] + script_args, env=activate_env(VENV_PATH), check=True)
    log(f"Finished running {script!r}", "SUCCESS")


def main():
    p = argparse.ArgumentParser(
        prog="pypippark",
        description="Manage a single, system‐wide venv at /usr/local/bin/pypippark-dep"
    )
    subs = p.add_subparsers(dest="cmd", required=True)

    ins = subs.add_parser("install", help="Install packages")
    ins.add_argument("pkgs", nargs="+", help="package names (pip syntax)")

    subs.add_parser("list", help="List installed packages")

    rem = subs.add_parser("remove", help="Remove packages")
    rem.add_argument("pkgs", nargs="+", help="package names to remove")

    subs.add_parser("update", help="Update all packages")

    run = subs.add_parser("run", help="Run a Python script inside the venv")
    run.add_argument("script", help="path to the .py file")
    run.add_argument("args", nargs=argparse.REMAINDER, help="arguments to pass to the script")

    args = p.parse_args()
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
