import io
import os
import struct
import numpy as np
from os.path import join, splitext

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile

"""File list header:

Name offset: 2b
Data type: 2b
Data offset: 4b
Data size: 4b
"""

def ui_open():
    file = askopenfilename(title='Open a ARC file...')
    return file 

def read_null_str(f):
    r_str = ""
    while 1:
        back_offset = f.tell()
        try:
            r_char = struct.unpack("c", f.read(1))[0].decode("utf8")
        except:
            f.seek(back_offset)
            temp_char = struct.unpack("<H", f.read(2))[0]
            r_char = chr(temp_char)
        if ord(r_char) == 0:
            return r_str
        else:
            r_str += r_char   

fpath = ui_open()
fname, fext = os.path.splitext(fpath)
fbasename = os.path.basename(fname)
fdir = os.path.dirname(fname)

with io.open(fpath, mode="rb") as src:
    src.seek(8, io.SEEK_SET)
    header_size = int.from_bytes(src.read(4), 'little')
    data_section = int.from_bytes(src.read(4), 'little')
    src.seek(16, io.SEEK_CUR)

    #Reading file info
    src.seek(8, io.SEEK_CUR)
    num_items = int.from_bytes(src.read(4), 'little')-1

    print(f"{num_items} items detected")

    data = []
    for i in range(num_items):
        entry = {}
        entry["name_off"] = int.from_bytes(src.read(2), 'little')
        entry["type"] = int.from_bytes(src.read(2), 'little')
        entry["off"] = int.from_bytes(src.read(4), 'little')
        entry["size"] = int.from_bytes(src.read(4), 'little')
        data.append(entry)

    src.seek(1, io.SEEK_CUR)

    item_name = []
    for i in range(num_items):
        item_name.append(read_null_str(src))

    destdir = fdir + "/" + fbasename
    os.makedirs(destdir)

    for i in range(num_items):
        if data[i]['type'] == 0:
            print(destdir + "/" + item_name[i])
            with io.open(destdir + "/" + item_name[i], mode="wb") as dst:
                src.seek(data[i]['off'], io.SEEK_SET)
                dst.write(src.read(data[i]['size']))
