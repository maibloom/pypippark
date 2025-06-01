# pypippark

PyPipPark functions as an organized haven for Python pip dependencies, efficiently gathering and managing an extensive range of Python libraries in a dedicated location, which provides developers with a streamlined and permanently accessible solution to optimize their workflow. 

---
## Theory

The Theory is to install any dependency in a dedicated location of your system and run it from that specific place only.

> [!CAUTION]
> As Pypippark installs packages inside ```/``` directory, make sure it has free space to install and use heavier dependencies.

---
## Installation

### Method 1: With OmniPkg Package Manager 

1. [Install OmniPkg Package Manager](https://github.com/maibloom/omnipkg-app)

2. Install pypippark:

```
omnipkg put install pypippark
```

### Method 2: using git

you can git this project and run the bash script file:

```
sudo pacman -S python-pip

git clone https://www.github.com/maibloom/pypippark/

cd pypippark

chmod +x *

sudo bash install.sh
```