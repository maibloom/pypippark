#!/usr/bin/env python3
import sys
import subprocess

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.\n")
    print("This script installs the specified packages globally,")
    print("ensuring you have the latest versions, and does all of this within your current terminal session.")

def update_pip():
    """Update pip globally."""
    print("Updating pip to the latest version...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    if result.returncode != 0:
        print("Warning: pip update failed. Proceeding with existing pip version.")
    else:
        print("pip updated successfully.")

def install_packages(packages):
    """
    Install (or update) the given packages globally using pip.
    The --upgrade flag ensures that the newest versions are installed.
    """
    command = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
    print("Installing/updating packages:", packages)
    result = subprocess.run(command)
    if result.returncode != 0:
        print("An error occurred during package installation.")
        sys.exit(result.returncode)
    print("Packages installed/updated successfully.")

def main():
    # If the help option is provided, show usage.
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()
        sys.exit(0)

    # Get package names from command line arguments or prompt the user.
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = input("Enter package name(s) (space separated): ").split()

    if not packages:
        print("No packages specified. Exiting.")
        sys.exit(1)

    # Update pip and install (or update) the packages globally.
    update_pip()
    install_packages(packages)

    print("Installation complete. All packages are installed globally in your current environment.")

if __name__ == "__main__":
    main()
