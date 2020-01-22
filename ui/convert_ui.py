# -a: ui file name
# -o: conveted ui filename
# -x: full path to pyside2-uic.exe

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a')
parser.add_argument('-o')
parser.add_argument('-x')
args = parser.parse_args()

os.system(args.x + " " + args.a + " -o " + args.o)

imp = "try:\n\tfrom PySide2.QtCore import QString\nexcept ImportError:\n\tQString = str"

with open("mainwindow.py", 'r') as f:
    contents = f.readlines()
    contents.insert(9, imp)

with open("mainwindow.py", 'w') as o:
    o.write("".join(contents))
