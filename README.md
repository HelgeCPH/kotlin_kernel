# Kotlin Kernel

This is a small Jupyter kernel wrapping the Kotlin language.

The only reason for it's existence is, that I could not get [ligee's Kotlin kernel](https://github.com/ligee/kotlin-jupyter) (is it the official Kotlin kernel) to work. That could be build and installed but was always crashing as soon as I created a new notebook.



## Installation

To install the `kotlin_kernel` from PyPi:

```bash
pip install kotlin_kernel
python -m kotlin_kernel.install
```

To work on this code directly, you may want to:

```bash
git clone git@github.com:HelgeCPH/kotlin_kernel.git
cd kotlin_kernel
pip install .
python -m kotlin_kernel.install
```

## Dependencies

This kernel requires that you have the Kotlin CLI tools installed on your computer. Currently, I only tested this kernel on MacOS, where I installed Kotlin and `kotlinc-jvm` via [homebrew](https://brew.sh).

Anyway's, this kernel should work on any system on which `kotlinc-jvm` is installed and added to the PATH.

The reason for this dependency is that this kernel is a really slim wrapper around the Kotlin REPL via `peexpect`.

## Using the Kotlin Kernel

**Notebook**: The *New* menu in the notebook should show an option for an `Kotlin` notebook.

**Console frontends**: To use it with the console frontends, add `--kernel kotlin` to their command line arguments.

That should be it...




## TODO:

  * I am planning to add support for a configuration file, so that a `classpath` for the `kotlinc-jvm` session can be set.
  * I started investigating integration of the [Kotlin language server protocol implementation](https://github.com/fwcd/KotlinLanguageServer) for code completion.
