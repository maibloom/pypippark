#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def print_usage():
    print("Usage: pypippark [package1 package2 ...]")
    print("If no package arguments are provided, you'll be prompted for them.\n")
    print("This script creates a virtual environment in a specified directory and")
    print("installs packages into it. After installing, you'll need to activate the")
    print("environment with:")
    print("  source ~/pypippark/deps/bin/activate\n")

def update_bashrc():
    """
    Append the virtual environment's bin directory to ~/.bashrc if not already present.
    This makes it easier to run executables from the venv in new terminals.
    """
    bashrc_path = os.path.expanduser("~/.bashrc")
    env_line = 'export PATH="$HOME/pypippark/deps/bin:$PATH"'
    lines = []
    if os.path.isfile(bashrc_path):
        with open(bashrc_path, "r") as file:
            lines = file.read().splitlines()
    if env_line not in lines:
        with open(bashrc_path, "a") as file:
            file.write("\n" + env_line + "\n")
        print("Added the virtual environment bin directory to your ~/.bashrc.")
    else:
        print("Your ~/.bashrc already includes the virtual environment bin directory in PATH.")

def create_or_get_venv(install_dir):
    """Create a virtual environment in install_dir if it doesn't exist yet."""
    activate_script = os.path.join(install_dir, "bin", "activate")
    if not os.path.exists(activate_script):
        print("Creating virtual environment at:", install_dir)
        venv.create(install_dir, with_pip=True)
    else:
        print("Using existing virtual environment at:", install_dir)

def install_packages(install_dir, packages):
    """Install the given packages using the venv's pip."""
    pip_executable = os.path.join(install_dir, "bin", "pip")
    command = [pip_executable, "install"] + packages
    print("Installing package(s):", packages)
    result = subprocess.run(command)
    if result.returncode != 0:
        print("Error occurred during package installation.")
        sys.exit(result.returncode)
    print("Packages installed successfully.")

def main():
    # Check for help argument.
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_usage()
        sys.exit(0)
    
    # Read package names from command-line arguments or prompt the user.
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = input("Enter the Python package name(s) to install (separated by space): ").split()
    
    if not packages:
        print("No packages specified. Exiting.")
        sys.exit(1)
    
    # Define the directory where the virtual environment will live.
    install_dir = os.path.expanduser("~/pypippark/deps")
    os.makedirs(install_dir, exist_ok=True)
    
    # Create (or reuse) the virtual environment.
    create_or_get_venv(install_dir)
    
    # Update ~/.bashrc to add the venv's bin directory to PATH.
    update_bashrc()
    
    # Inform the user how to activate the virtual environment manually.
    print("\nTo activate your environment manually, run:")
    print("  source {}/bin/activate\n".format(install_dir))
    print("New terminals will pick up the change if you restart them or source your ~/.bashrc\n")
    
    # Install the desired packages.
    install_packages(install_dir, packages)
    
    # As a Python script, we cannot modify the parent shell's environment.
    # Instead, we print a message so you know how to activate the environment.
    print("Installation complete.")
    print("To use the installed packages in your current session, please run:")
    print("  source ~/pypippark/deps/bin/activate")
    print("\nTip: You can add the following shell function to your ~/.bashrc for automatic activation:")
    print('''
pypippark() {
    /usr/local/bin/pypippark "$@"
    source ~/pypippark/deps/bin/activate
}
    ''')

if __name__ == "__main__":
    main()
