import sys
import os

results = []
try:
    import multipart
    results.append("python-multipart: INSTALLED")
except ImportError:
    results.append("python-multipart: MISSING")

try:
    import xlsxwriter
    results.append("xlsxwriter: INSTALLED")
except ImportError:
    results.append("xlsxwriter: MISSING")

with open("deps_output.txt", "w") as f:
    f.write("\n".join(results))
