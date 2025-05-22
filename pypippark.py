#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.")
    print("")
    print("This script creates a virtual environment in the specified directory and installs packages into it.")

def update_bashrc():
    bashrc_path = os.path.expanduser("~/.bashrc")
    # Instead of PYTHONPATH we add the venv's bin directory to PATH.
    env_line = 'export PATH="$HOME/pypippark/deps/bin:$PATH"'
    # Read current lines to avoid adding multiple times.
    if os.path.exists(bashrc_path):
        with open(bashrc_path, 'r') as f:
            lines = f.read().splitlines()
    else:
        lines = []
    if env_line not in lines:
        with open(bashrc_path, 'a') as f:
            f.write("\n" + env_line + "\n")
        print("Added the virtual environment bin directory to your ~/.bashrc.")
    else:
        print("Your ~/.bashrc already has the virtual environment bin directory in PATH.")

def create_or_get_venv(install_dir):
    """Create a virtual environment in install_dir if it does not exist yet."""
    activate_path = os.path.join(install_dir, "bin", "activate")
    if not os.path.exists(activate_path):
        print("Creating virtual environment at:", install_dir)
        # The venv module will create a complete environment with pip installed.
        venv.create(install_dir, with_pip=True)
    else:
        print("Using existing virtual environment at:", install_dir)

def install_packages(install_dir, packages):
    # Use the Python executable from the virtual environment to call pip.
    pip_executable = os.path.join(install_dir, "bin", "pip")
    # Install the packages using the virtual env's pip.
    command = [pip_executable, "install"] + packages
    print("Installing package(s):", packages)
    result = subprocess.run(command)
    if result.returncode != 0:
        print("Error occurred during package installation.")
        sys.exit(result.returncode)
    else:
        print("Packages installed successfully.")

def main():
    # Help message handling.
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()
        sys.exit(0)
    
    # If packages are passed as arguments, use them. Otherwise, prompt the user.
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = input("Enter the Python package name(s) to install (separated by space): ").split()
    
    if not packages:
        print("No packages specified. Exiting.")
        sys.exit(1)

    # Define where the virtual environment (and thus packages) will live.
    install_dir = os.path.expanduser("~/pypippark/deps")
    
    # Ensure the installation directory exists.
    os.makedirs(install_dir, exist_ok=True)

    # Create (or reuse) the virtual environment.
    create_or_get_venv(install_dir)

    # Optionally update the user shell configuration to include the venv's bin directory in PATH.
    update_bashrc()
    print("\nTo activate your environment manually, run:")
    print("  source {}/bin/activate\n".format(install_dir))
    print("New terminals will pick up the change if you restart them or source your ~/.bashrc\n")
    
    # Install the specified packages into the virtual environment.
    install_packages(install_dir, packages)

if __name__ == "__main__":
    main()
