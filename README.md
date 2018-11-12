
[TOC]

# Introduction

This script generates target register docs based on ralf file(s).

# Docs Generated

The generated docs include:

* Register table (in CSV)
* Register define header file (in Verilog)

# Usage

```
$ ./ralf2doc/ralf2doc.py -h
Usage: ralf2doc.py TARGET OUT_DIR RALF_FILE <RALF_FILE...>
```

Note: TARGET is the top level name you want in RALF_FILE