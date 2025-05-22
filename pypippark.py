#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.\n")
    print("This script creates (or reuses) a virtual environment in ~/pypippark/deps,")
    print("installs the specified packages, and if run from an interactive terminal,")
    print("automatically launches a new shell with the environment activated.")

def update_bashrc(venv_bin_path):
    """
    Append the virtual environment's bin directory to ~/.bashrc if not already present.
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

def activate_shell(activation_script):
    """
    Automatically launch an interactive shell with the virtual environment activated.
    We use the user's shell (defaulting to bash) and run a command to source the activation script.
    """
    shell = os.environ.get("SHELL", "/bin/bash")
    print("Launching an interactive shell with the virtual environment activated...")
    # Use "-i" for interactive; the command sources the activation script
    os.execlp(shell, shell, "-i", "-c", f"source {activation_script} && exec {shell} -i")

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
    
    # Define the directory for the virtual environment
    venv_dir = os.path.expanduser("~/pypippark/deps")
    os.makedirs(venv_dir, exist_ok=True)
    
    # Create (or reuse) the virtual environment.
    activation_script = create_or_get_venv(venv_dir)
    
    # Update ~/.bashrc with the venv's bin directory.
    update_bashrc(os.path.join(venv_dir, "bin"))
    
    # Install the requested packages.
    install_packages(venv_dir, packages)
    
    # If running interactively, automatically launch a new shell with the venv activated.
    if sys.stdin.isatty():
        activate_shell(activation_script)
    else:
        print("Installation complete.")
        print(f"To activate the virtual environment manually, run:\n  source {activation_script}")

if __name__ == "__main__":
    main()
