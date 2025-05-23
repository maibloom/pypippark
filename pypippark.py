#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.\n")
    print("This script creates (or reuses) a virtual environment in ./venv,")
    print("installs the specified packages, and provides instructions to activate it.")

def update_bashrc(venv_bin_path):
    """
    Optionally append the virtual environment's bin directory to ~/.bashrc if not already present.
    This makes future sessions simpler.
    """
    bashrc_path = os.path.expanduser("~/.bashrc")
    env_line = f'export PATH="{venv_bin_path}:$PATH"'
    try:
        if os.path.isfile(bashrc_path):
            with open(bashrc_path, "r") as file:
                content = file.read()
            if env_line not in content:
                with open(bashrc_path, "a") as file:
                    file.write("\n" + env_line + "\n")
                print("Added the virtual environment bin directory to your ~/.bashrc.")
            else:
                print("Your ~/.bashrc already includes the virtual environment bin directory.")
        else:
            print("No ~/.bashrc file found.")
    except Exception as e:
        print(f"Error while updating bashrc: {e}")

def create_or_get_venv(venv_dir):
    """Create the virtual environment at venv_dir if it doesn’t already exist."""
    activate_script = os.path.join(venv_dir, "bin", "activate")
    if not os.path.exists(activate_script):
        print("Creating virtual environment at:", venv_dir)
        venv.create(venv_dir, with_pip=True)
    else:
        print("Using existing virtual environment at:", venv_dir)
    return activate_script

def install_packages(venv_dir, packages):
    """Install the given packages using the venv’s pip."""
    pip_executable = os.path.join(venv_dir, "bin", "pip")
    command = [pip_executable, "install"] + packages
    print("Installing packages:", packages)
    result = subprocess.run(command)
    if result.returncode != 0:
        print("An error occurred during package installation.")
        sys.exit(result.returncode)
    print("Packages installed successfully.")

def main():
    # If help is requested, show usage.
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()
        sys.exit(0)
    
    # Get package names from command line arguments; prompt if none are given.
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = input("Enter package name(s) (space separated): ").split()
    
    if not packages:
        print("No packages specified. Exiting.")
        sys.exit(1)
    
    # Define the directory for the virtual environment.
    # Changed from ~/pypippark/deps to ./venv in the current working directory.
    venv_dir = os.path.join(os.getcwd(), "venv")
    os.makedirs(venv_dir, exist_ok=True)
    
    # Create (or reuse) the virtual environment.
    activation_script = create_or_get_venv(venv_dir)
    
    # Update ~/.bashrc with the venv's bin directory.
    update_bashrc(os.path.join(venv_dir, "bin"))
    
    # Install the requested packages.
    install_packages(venv_dir, packages)
    
    # Instead of launching a new shell, simply instruct the user on how to activate the venv.
    print("Installation complete.")
    print(f"To activate the virtual environment, run:\n  source {activation_script}")

if __name__ == "__main__":
    main()
