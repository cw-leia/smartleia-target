[![Build Status](https://travis-ci.com/cw-leia/smartleia_target.svg?branch=master)](https://travis-ci.com/cw-leia/smartleia_target)

# SmartLeia-target

This repository holds the source of the python package used to drive the LEIA
smart card reader target. With it, you will be able to drive the LEIA-target-applet.

The documentation dedicated to the SmartLeia package can be found [here](https://github.com/cw-leia/smartleia-doc),
please check it to have details about the basic usage and the API for advanced
development features.

## Dependencies

You can install the requirements of the package using:

```sh
pip install requirements.txt
```

## Installation of smartleia-target

### From git

You may need to use the last version of python builtin's setuptools to install
smartleia from git

```sh
python3 -m pip install --upgrade pip setuptools wheel
```

```sh
git clone https://github.com/cw-leia/smartleia_target
cd smartleia_target
python3 -m pip install .
`````

### From pipy

```sh
python3 -m pip install smartleia_target
```
