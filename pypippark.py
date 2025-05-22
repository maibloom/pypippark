#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.\n")
    print("This script creates (or reuses) a virtual environment in a folder called 'deps'")
    print("located in the same directory as this script. It automatically upgrades pip,")
    print("installs the specified packages, and if run from an interactive terminal,")
    print("launches a new shell with the environment activated.")
    print("\nTo manually activate the environment later, run:")
    print("  source ./deps/bin/activate\n")

def update_bashrc(venv_bin_path):
    """
    Append the virtual environment's bin directory to ~/.bashrc if not already present.
    This makes executables installed in the venv available in future sessions.
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
                print("Added the virtual environment's bin directory to your ~/.bashrc.")
            else:
                print("Your ~/.bashrc already includes the virtual environment's bin directory.")
        else:
            print("~/.bashrc file not found.")
    except Exception as e:
        print("Error updating ~/.bashrc:", e)

def create_or_get_venv(venv_dir):
    """Create the virtual environment at venv_dir if it doesn’t already exist."""
    activate_script = os.path.join(venv_dir, "bin", "activate")
    if not os.path.exists(activate_script):
        print("Creating virtual environment at:", venv_dir)
        venv.create(venv_dir, with_pip=True)
    else:
        print("Using existing virtual environment at:", venv_dir)
    return activate_script

def update_pip(venv_dir):
    """Automatically check for and upgrade pip in the virtual environment."""
    pip_executable = os.path.join(venv_dir, "bin", "pip")
    print("Automatically checking for pip updates...")
    try:
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
        print("pip has been updated successfully.")
    except subprocess.CalledProcessError:
        print("Warning: Failed to update pip. Continuing with the existing version.")

def install_packages(venv_dir, packages):
    """Install the given packages using the virtual environment's pip."""
    pip_executable = os.path.join(venv_dir, "bin", "pip")
    command = [pip_executable, "install"] + packages
    print("Installing packages:", packages)
    result = subprocess.run(command)
    if result.returncode != 0:
        print("Error occurred during package installation.")
        sys.exit(result.returncode)
    print("Packages installed successfully.")

def activate_shell(activation_script):
    """
    Automatically launch an interactive shell with the virtual environment activated.
    We determine the user's shell (defaulting to bash) and then source the activation script.
    """
    shell = os.environ.get("SHELL", "/bin/bash")
    print("Launching an interactive shell with the virtual environment activated...")
    os.execlp(shell, shell, "-i", "-c", f"source {activation_script} && exec {shell} -i")

def main():
    # Display help if requested.
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()
        sys.exit(0)

    # Retrieve package names from the arguments, or prompt the user.
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = input("Enter package name(s) (space separated): ").split()

    if not packages:
        print("No packages specified. Exiting.")
        sys.exit(1)

    # Define the dependency folder relative to the location of this script.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, "deps")
    try:
        os.makedirs(venv_dir, exist_ok=True)
    except PermissionError as e:
        print(f"Permission denied: Unable to create directory '{venv_dir}': {e}")
        sys.exit(1)

    # Create (or reuse) the virtual environment.
    activation_script = create_or_get_venv(venv_dir)

    # Automatically update pip within the virtual environment.
    update_pip(venv_dir)

    # Update the user's ~/.bashrc to include the venv's bin directory.
    update_bashrc(os.path.join(venv_dir, "bin"))

    # Install the requested packages.
    install_packages(venv_dir, packages)

    # Launch an interactive shell with the environment activated.
    if sys.stdin.isatty():
        activate_shell(activation_script)
    else:
        print("Installation complete.")
        print(f"To activate your virtual environment manually, run:\n  source {activation_script}")

if __name__ == "__main__":
    main()
