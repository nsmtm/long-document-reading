#!/usr/bin/env python3
"""Compare two files byte for byte and report the result.

A file that arrives again under a new name is sometimes the same file
uploaded twice; the check is mechanical (sizes and hashes), so it is a
script rather than a reader's impression (proposal R-P05 of review run
20261118-12).

Usage: compare_bytes.py FILE1 FILE2
Exit code 0 when the files are byte-identical, 1 otherwise.
"""
import hashlib
import sys

a = open(sys.argv[1], "rb").read()
b = open(sys.argv[2], "rb").read()
print(f"file1: {sys.argv[1]}  {len(a)} bytes  md5 {hashlib.md5(a).hexdigest()}  sha256 {hashlib.sha256(a).hexdigest()}")
print(f"file2: {sys.argv[2]}  {len(b)} bytes  md5 {hashlib.md5(b).hexdigest()}  sha256 {hashlib.sha256(b).hexdigest()}")
if a == b:
    print("identical: yes")
    sys.exit(0)
first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
print(f"identical: no (first differing byte offset: {first})")
sys.exit(1)
