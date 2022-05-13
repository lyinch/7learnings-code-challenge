# Environment setup

It is best to run the notebook in a virtual environment.

```
 virtualenv venv
 source venv/bin/activate
 pip install -r requirements.txt
 ```

Note that this requires the `virtualenv` package to be installed.

When opening the Jupyter notebook in vscode it's possible that the kernel doesn't automatically use the associated interpreter of the virtual environment. For this, the following is required:

```
(venv) % ipython kernel install --user --name=7learnings
```
https://anbasile.github.io/posts/2017-06-25-jupyter-venv/


The project uses Python version 3.9.12 which can also automatically be set with `.python-version` and the `pyenv` package.

The path to the gcloud credentials is hard-coded for this challenge if the env variable `GOOGLE_APPLICATION_CREDENTIALS` is not present.

Note that the `requirements.txt` is different from the provided environment. The provided stack doesn't run on a macbook with an M1 chip. There were some attempts to get it working by only changing the least amount of package versions, but this turned out to be futile. Therefore, I setup a completely new environment and froze it. The attempts to change the initial requirements can be found at the end of this readme.

# Challenge

## Your Challenge README

Include the following items in your `README`:

* Description of the problem, solution and how-to run the solution.
* Reasoning behind your technical choices. Trade-offs you might have made, anything you left out, or what you might do differently if you were to spend additional time on the project.
* Link to the hosted application where applicable.



# Attempts to install requirements on apple silicon
The following sections describe problems during installation and runtime of the environment. As it turns out these changes are not enough, and I recreated the environment from scratch.

## broken packages on M1 macbook during installation
Some packages might give trouble when setting up the environment on an M1 macbook with Python 3.10.1. I wanted to keep the environment as close as possible to the original, which is why I selectively tried to upgrade the failing packages to the closest working version.

### google-cloud-bigquery 

```
ERROR: Could not find a version that satisfies the requirement google-cloud-bigquery==2.8.0 (from versions: 0.20.0, 0.21.0, 0.22.0, 0.22.1, 0.23.0, 0.24.0, 0.25.0, 0.26.0, 0.27.0, 0.28.0, 0.29.0, 0.30.0, 0.31.0, 0.32.0, 1.0.0, 1.1.0, 1.2.0, 1.3.0, 1.4.0, 1.5.0, 1.5.1, 1.5.2, 1.6.0, 1.6.1, 1.6.2, 1.7.0, 1.7.2, 1.8.0, 1.8.1, 1.8.2, 1.9.0, 1.9.1, 1.10.0, 1.10.1, 1.11.1, 1.11.2, 1.11.3, 1.11.4, 1.12.0, 1.12.1, 1.12.2, 1.13.0, 1.13.1, 1.14.0, 1.14.1, 1.15.0, 1.15.1, 1.16.0, 1.16.1, 1.17.0, 1.17.1, 1.18.0, 1.18.1, 1.19.0, 1.19.1, 1.20.0, 1.21.0, 1.22.0, 1.23.0, 1.23.1, 1.24.0, 1.25.0, 1.26.0, 1.26.1, 1.27.2, 1.28.0, 1.28.1, 2.0.0, 2.1.0, 2.2.0, 2.3.1, 2.4.0, 2.5.0, 2.6.0, 2.6.1, 2.30.0, 2.30.1, 2.31.0, 2.32.0, 2.33.0, 2.34.0, 2.34.1, 2.34.2, 2.34.3, 3.0.0b1, 3.0.0, 3.0.1, 3.1.0)
ERROR: No matching distribution found for google-cloud-bigquery==2.8.0
```

As it turns out, this package doesn't support Python >=3.10. Solution: Downgrade Python to e.g. 3.9.12 with `pyenv`:

```
pyenv install 3.9.12
pyenv local 3.9.12
```

### pyarrow

Installation produces a very long error, the relevant line:
```
clang: error: the clang compiler does not support 'faltivec', please use -maltivec and include altivec.h explicitly
```

Apache Arrow wants to install some SIMD vectorization which is probably not available on arm64. The first version to support the M1 is 5.0.0 as per the changelog: https://arrow.apache.org/release/5.0.0.html and issue 12122. 

Solution: Changed `requirements.txt` to pin the version to `5.0.0`. I am not sure how backwards compatible major version upgrades are, but it solves the compilation problem.

### grpcio

This package throws a surprising error, as it doesn't look like an issue with arm64 but probably a difference between gcc and clang. 


```
third_party/zlib/gzlib.c:252:9: error: implicit declaration of function 'lseek' is invalid in C99 [-Werror,-Wimplicit-function-declaration]
              LSEEK(state->fd, 0, SEEK_END);  /* so gzoffset() is correct */
```

The man page for `feature_test_macros` seems to confirm this: https://man7.org/linux/man-pages/man7/feature_test_macros.7.html :

> This macro is implicitly defined by gcc(1) when invoked with, for example, the -std=c99 or -ansi flag.

Version 1.36.0 apparently fixes this bug: https://github.com/grpc/grpc/releases/tag/v1.36.0
> Fix implicit declaration error in zlib + macOS. (#24979)

However, I still get the same compilation error. The earliest working minor version is 1.39.0 which fixes this bug (again) https://github.com/grpc/grpc/releases/tag/v1.39.0: 
> Fix zlib unistd.h import problem. (#26374)

Therefore, the solution is to upgrade the dependency to 1.39.0


### numpy
Same problem as with pyarrow, `-faltivec` is required but not supported on M1. A bunch of clang errors are thrown. Changelog of `1.20.3` https://numpy.org/doc/stable/release/1.20.3-notes.html :
> #18923: BLD: remove unnecessary flag -faltivec on macOS

However, this version didn't solve the problem and introduced a new compiler error:

```
     AssertionError
      
      ########### EXT COMPILER OPTIMIZATION ###########
      Platform      :
        Architecture: aarch64
        Compiler    : clang
      
      CPU baseline  :
        Requested   : 'min'
        Enabled     : NEON NEON_FP16 NEON_VFPV4 ASIMD
        Flags       : none
        Extra checks: none
      
      CPU dispatch  :
        Requested   : 'max -xop -fma4'
        Enabled     : ASIMDHP ASIMDDP
        Generated   :
                    :
        ASIMDHP     : NEON NEON_FP16 NEON_VFPV4 ASIMD
        Flags       : -march=armv8.2-a+fp16
        Extra checks: none
        Detect      : ASIMD ASIMDHP
                    : numpy/core/src/umath/_umath_tests.dispatch.c
```

This hints at some low-level optimisation routine to compile for the target architecture which fails. Version 1.21.0 seems to fix this https://numpy.org/doc/stable/release/1.21.0-notes.html : 
> With the release of macOS 11.3, several different issues that numpy was encountering when using Accelerate Framework’s implementation of BLAS and LAPACK should be resolved. This change enables the Accelerate Framework as an option on macOS. 


Upgrading to version 1.21.0 fixed this.

### nbformat
The pinned version is yanked:
```
WARNING: The candidate selected for download or install is a yanked version: 'nbformat' candidate (version 5.1.2 at https://files.pythonhosted.org/packages/13/1d/59cbc5a6b627ba3b4c0ec5ccc82a9002e58b324e2620a4929b81f1f8d309/nbformat-5.1.2-py3-none-any.whl#sha256=3949fdc8f5fa0b1afca16fb307546e78494fa7a7bceff880df8168eafda0e7ac (from https://pypi.org/simple/nbformat/) (requires-python:>=3.5))
Reason for being yanked: Name generation process created inappropriate id values
```

This is not an issue as inappropriate words don't break any code: https://github.com/jupyter/nbformat/pull/217


## runtime issues on macos M1
After changing the pinned package versions some incompatibilities occurred during runtime.

### bigquery
There is a version mismatch between bigquery and numpy:
```
ValueError: numpy.ndarray size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

As it turns out, bigquery also pinned the numpy version and changed it to 1.21.2 with this PR: https://github.com/googleapis/python-bigquery/pull/899 . It got merged the 24.08.21, therefore a release later than this is required.

Upgrading numpy to 1.21.2 and bigquery to 2.25.0 however apparently leads to a very difficult dependency graph and installing the requirements literally takes hours. Stopped here and created a new environment from scratch by installing the dependencies manually with the latest available version.