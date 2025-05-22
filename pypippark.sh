#!/usr/bin/env bash

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  echo "Usage: pypippark <<EOF"
  echo "package1 package2 ..."
  echo "EOF"
  echo
  echo "This script installs Python packages into a custom directory and updates PYTHONPATH."
  exit 0
fi

read -p "Enter the Python package name(s) to install: " package_names

install_dir="$HOME/pypippark/deps"
mkdir -p "$install_dir"

export_line="export PYTHONPATH=\"$install_dir:\$PYTHONPATH\""

if ! grep -Fxq "$export_line" ~/.bashrc; then
  echo "$export_line" >> ~/.bashrc
  echo "Added PYTHONPATH to ~/.bashrc"
else
  echo "PYTHONPATH already set in ~/.bashrc"
fi

echo "Please run 'source ~/.bashrc' or open a new terminal session to apply changes."

pip install --target="$install_dir" $package_names

