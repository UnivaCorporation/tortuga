# Tortuga Example Kit

This is an example kit layout that can be used as a basis for writing your own Tortuga kit.

## Prequisites

In order to create and build a kit, you must have the following installed:

- Python 3.4+
- [tortuga-core](https://github.com/UnivaCorporation/tortuga)

## Quickstart

### 1. Edit kit.json

Set the name, version, iteration, and description for your kit.

- Names must be all lowercase, no spaces, and can only use underscores for separating words. Our recommendation is to use a singe lowercase word.
- Versions are required, and must follow semantic versioning (https://semver.org/)
- Iterations are a single integer, if you don't know what to put here, use '0'.

### 2. Rename the kit directory

Under **tortuga_kits**, rename the kit directory name as follows:

**<kit_name>_<kit_version>**

For example, if your kit name is **mykit** and your kit version is **1.2.0** the directory would be named as follows:

**mykit_1_2_0**

Notes on kit directory naming:

- Since the kit directory is a python package, it must be named in accordance with python packaging requirements, which is why we change the version numbers to use underscores.
- Since it is possible for multiple versions of the kit to be installed simultaneously, having the python package names versioned is important.
- The top-level *tortuga_kits* directory is a python3 namespace, and must not contain an *\_\_init\_\_.py* file.

### 3. Implement kit installer methods

Edit the **kit.py** file and implement the action methods as required for your kit.

### 4. Create your components

Each kit must have at least 1 component. See the example component to see how to create your own.

### 5 Build your kit

To build your kit, run the **build-kit** utility, which is included as part of the **tortuga-core** python package (see prerequisites above).
