#!/usr/bin/env python
# -*- coding: utf-8 -*-

' this script generates register docs based on ralf file '

__author__ = "Bo DONG"

import sys, os
import re
import copy

from ralf_class import *

def func():
    return "Hello World!"

def main():
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print("Usage: {} TARGET OUT_DIR RALF_FILE <RALF_FILE...>".format(os.path.basename(__file__)))
    else:
        target = sys.argv[1]
        out_dir = sys.argv[2]
        ralf_list = sys.argv[3:]

        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        # csv file
        csv = "{}/{}.csv".format(out_dir, target)
        # vhdr files
        vhdr = "{}/{}_defs.v".format(out_dir, target) # full edition
        vhdr_s = "{}/{}_defs_slim.v".format(out_dir, target) # slim edition

        hier = [] # hierachy list
        defs = [] # define list
        for ralf in ralf_list:
            if not os.path.isfile(ralf):
                print("{} is not a valid file".format(ralf))
            else:
                with open(ralf) as f:
                    in_doc = False
                    for nu, l in enumerate(f):
                        l = l.strip()
                        level = len(hier)
                        # end of definition
                        if re.search(r"^}", l):
                            if in_doc: # in doc
                                in_doc = False
                            else:
                                item = hier.pop(-1)
                                # add to defs if top level
                                if level == 1:
                                    defs.append(item)
                                # print 
                                if item.name == target:
                                    # output screen
                                    print(item)
                                    # generate csv file
                                    if csv:
                                        with open(csv, 'w') as c:
                                            c.write(item.csv())
                                    # generate vhdr files
                                    if vhdr:
                                        item.fname = item.name.upper()
                                        item.addr = item.offset
                                        # full edition
                                        with open(vhdr, 'w') as v:
                                            v.write(item.vhdr())
                                        # slim edition
                                        with open(vhdr_s, 'w') as vs:
                                            with open(vhdr) as v:
                                                for l in v:
                                                    l = l.replace('_REGMODEL', '')
                                                    l = l.replace('ADDR_MAP', 'AMAP')
                                                    l = l.replace('CPU0', 'MC')
                                                    vs.write(l)
                        elif in_doc:
                            hier[-1].info += l.replace(',', ';')
                        # info
                        elif re.search(r"^#\s*(.*)", l):
                            if len(hier):
                                match = re.search(r"^#\s*(.*)", l)
                                hier[-1].info += match.group(1).replace(',', ';')
                        # doc
                        elif re.search(r"^doc\s*{", l):
                            if len(hier):
                                match = re.search(r"^doc\s*{(.*)", l)
                                hier[-1].info += match.group(1).replace(',', ';')
                                in_doc = True
                        # bits
                        elif re.search(r"^bits\s+(\d+)\s*;", l):
                            match = re.search(r"^bits\s+(\d+)\s*;", l)
                            hier[-1].bits = int(match.group(1))
                        # access
                        elif re.search(r"^access\s+(\w+)\s*;", l):
                            match = re.search(r"^access\s+(\w+)\s*;", l)
                            hier[-1].access = match.group(1)
                        # reset
                        elif re.search(r"^reset\s+(\S+)\s*;", l):
                            match = re.search(r"^reset\s+(\S+)\s*;", l)
                            hier[-1].reset = match.group(1)
                        # hard reset
                        elif re.search(r"^hard_reset\s+(\S+)\s*;", l):
                            match = re.search(r"^hard_reset\s+(\S+)\s*;", l)
                            hier[-1].reset = match.group(1)
                        # bytes
                        elif re.search(r"^bytes\s+(\d+)\s*;", l):
                            match = re.search(r"^bytes\s+(\d+)\s*;", l)
                            hier[-1].bytes = match.group(1)
                        # endian
                        elif re.search(r"^endian\s+(\w+)\s*;", l):
                            match = re.search(r"^endian\s+(\w+)\s*;", l)
                            hier[-1].endian = match.group(1)
                        # size
                        elif re.search(r"^size\s+(\w+)\s*;", l):
                            match = re.search(r"^size\s+(\w+)\s*;", l)
                            hier[-1].size = match.group(1)
                        # leftright
                        elif re.search(r"^left_to_right\s*;", l):
                            match = re.search(r"^left_to_right\s*;", l)
                            hier[-1].leftright = True

                        # field
                        elif re.search(r"^field", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^field\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^field\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                incr = 0
                                if re.search(r"^field\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l): # path/offset
                                    match = re.search(r"^field\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                    incr = match.group(5)
                                elif re.search(r"^field\s+(\w+)\s*\[(\d+)\]\s*@(\S+)\s*\+\s*(\S+);", l): # offset
                                    match = re.search(r"^field\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)", l)
                                    offset = match.group(3)
                                    incr = match.group(4)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                _incr_prefix, incr_value = hex_proc(incr)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    field = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Field" in str(type(d)):
                                            field = copy.deepcopy(d)
                                            break
                                    if not field:
                                        print("Error {}:'{}' - Cannot find definition".format(nu, l))

                                    field.level, field.name, field.offset, field.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(field)
                                    oset_value += incr_value
                                    oset = oset_prefix + format(oset_value, 'x')
                            else: # non array
                                if re.search(r"^field\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^field\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^field\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                    match = re.search(r"^field\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    offset = match.group(2)
                                elif re.search(r"^field\s+(\w+)\s*\((.*)\)", l): # name/path
                                    match = re.search(r"^field\s+(\w+)\s*\((.*)\)", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                elif re.search(r"^field\s+(\w+)", l): # name
                                    match = re.search(r"^field\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                field = Field(level=level, name=name, offset=offset, path=path)

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Field" in str(type(d)):
                                            field = copy.deepcopy(d)
                                            field.level, field.offset, field.path = level, offset, path
                                            break
                                    hier[-1].subs.append(field)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(field)

                        # register
                        elif re.search(r"^register", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^register\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^register\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                if re.search(r"^register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # path/offset
                                    match = re.search(r"^register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                elif re.search(r"^register\s+(\w+)\s*\[(\d+)\]\s*@\s*(\S+)\s*[{;]", l): # offset
                                    match = re.search(r"^register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    offset = match.group(3)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    register = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Register" in str(type(d)):
                                            register = copy.deepcopy(d)
                                            break
                                    register.level, register.name, register.offset, register.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(register)
                                    oset_value += register.bytes
                                    oset = oset_prefix + format(oset_value, 'x')

                            else: # non array
                                if re.search(r"^register\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^register\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^register\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                    match = re.search(r"^register\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    offset = match.group(2)
                                elif re.search(r"^register\s+(\w+)\s*\((.*)\)", l): # name/path
                                    match = re.search(r"^register\s+(\w+)\s*\((.*)\)", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                elif re.search(r"^register\s+(\w+)", l): # name
                                    match = re.search(r"^register\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                register = Register(level=level, name=name, offset=offset, path=path, subs=[])

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Register" in str(type(d)):
                                            register = copy.deepcopy(d)
                                            register.level, register.offset, register.path = level, offset, path
                                            break
                                    hier[-1].subs.append(register)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(register) 

                        # regfile
                        elif re.search(r"^regfile", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                incr = 0
                                if re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l): # path/offset
                                    match = re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                    incr = match.group(5)
                                elif re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]\s*@(\S+)\s*\+\s*(\S+);", l): # offset
                                    match = re.search(r"^regfile\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)", l)
                                    offset = match.group(3)
                                    incr = match.group(4)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                _incr_prefix, incr_value = hex_proc(incr)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    regfile = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Regfile" in str(type(d)):
                                            regfile = copy.deepcopy(d)
                                            break
                                    if not regfile:
                                        print("Error {}:'{}' - Cannot find definition".format(nu, l))

                                    regfile.level, regfile.name, regfile.offset, regfile.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(regfile)
                                    oset_value += incr_value
                                    oset = oset_prefix + format(oset_value, 'x')
                            else: # non array
                                if re.search(r"^regfile\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^regfile\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^regfile\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                    match = re.search(r"^regfile\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    offset = match.group(2)
                                elif re.search(r"^regfile\s+(\w+)\s*\((.*)\)", l): # name/path
                                    match = re.search(r"^regfile\s+(\w+)\s*\((.*)\)", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                elif re.search(r"^regfile\s+(\w+)", l): # name
                                    match = re.search(r"^regfile\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                regfile = Regfile(level=level, name=name, offset=offset, path=path, subs=[])

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Regfile" in str(type(d)):
                                            regfile = copy.deepcopy(d)
                                            regfile.level, regfile.offset, regfile.path = level, offset, path
                                            break
                                    hier[-1].subs.append(regfile)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(regfile) 

                        # virtual register
                        elif re.search(r"^virtual register", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                incr = 0
                                if re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l): # path/offset
                                    match = re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                    incr = match.group(5)
                                elif re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]\s*@(\S+)\s*\+\s*(\S+);", l): # offset
                                    match = re.search(r"^virtual register\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)", l)
                                    offset = match.group(3)
                                    incr = match.group(4)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                _incr_prefix, incr_value = hex_proc(incr)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    v_reg = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Vregister" in str(type(d)):
                                            v_reg = copy.deepcopy(d)
                                            break
                                    if not v_reg:
                                        print("Error {}:'{}' - Cannot find definition".format(nu, l))

                                    v_reg.level, v_reg.name, v_reg.offset, v_reg.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(v_reg)
                                    oset_value += incr_value
                                    oset = oset_prefix + format(oset_value, 'x')
                            else: # non array
                                if re.search(r"^virtual register\s+(\w+)\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^virtual register\s+(\w+)\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^virtual register\s+(\w+)", l): # name
                                    match = re.search(r"^virtual register\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                vregister = Vregister(level=level, name=name, offset=offset, path=path, subs=[])

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Vregister" in str(type(d)):
                                            vregister = copy.deepcopy(d)
                                            vregister.level, vregister.offset, vregister.path = level, offset, path
                                            break
                                    hier[-1].subs.append(vregister)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(vregister) 

                        # memory
                        elif re.search(r"^memory", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^memory\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                match = re.search(r"^memory\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                name = match.group(1)
                                path = match.group(2)
                                offset = match.group(3)
                            elif re.search(r"^memory\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                match = re.search(r"^memory\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                name = match.group(1)
                                offset = match.group(2)
                            elif re.search(r"^memory\s+(\w+)\s*\((.*)\)", l): # name/path
                                match = re.search(r"^memory\s+(\w+)\s*\((.*)\)", l)
                                name = match.group(1)
                                path = match.group(2)
                            elif re.search(r"^memory\s+(\w+)", l): # name
                                match = re.search(r"^memory\s+(\w+)", l)
                                name = match.group(1)
                            else:
                                print("Error {}:'{}' - Unsupported format".format(nu, l))

                            memory = Memory(level=level, name=name, offset=offset, path=path)

                            if level: # sub level
                                # find from define list
                                for d in defs:
                                    if d.name == name and "Memory" in str(type(d)):
                                        memory = copy.deepcopy(d)
                                        memory.level, memory.offset, memory.path = level, offset, path
                                        break
                                hier[-1].subs.append(memory)

                            if re.search(r"{\s*$", l): # new description
                                hier.append(memory) 

                        # block
                        elif re.search(r"^block", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^block\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^block\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                incr = 0
                                if re.search(r"^block\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l): # path/offset
                                    match = re.search(r"^block\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                    incr = match.group(5)
                                elif re.search(r"^block\s+(\w+)\s*\[(\d+)\]\s*@(\S+)\s*\+\s*(\S+);", l): # offset
                                    match = re.search(r"^block\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)", l)
                                    offset = match.group(3)
                                    incr = match.group(4)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                _incr_prefix, incr_value = hex_proc(incr)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    block = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Block" in str(type(d)):
                                            block = copy.deepcopy(d)
                                            break
                                    if not block:
                                        print("Error {}:'{}' - Cannot find definition".format(nu, l))

                                    block.level, block.name, block.offset, block.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(block)
                                    oset_value += incr_value
                                    oset = oset_prefix + format(oset_value, 'x')

                            else: # non array
                                if re.search(r"^block\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^block\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^block\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                    match = re.search(r"^block\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    offset = match.group(2)
                                elif re.search(r"^block\s+(\w+)\s*\((.*)\)", l): # name/path
                                    match = re.search(r"^block\s+(\w+)\s*\((.*)\)", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                elif re.search(r"^block\s+(\w+)", l): # name
                                    match = re.search(r"^block\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                block = Block(level=level, name=name, offset=offset, path=path, 
                                    subs=[])

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "Block" in str(type(d)):
                                            block = copy.deepcopy(d)
                                            block.level, block.offset, block.path = level, offset, path
                                            break
                                    hier[-1].subs.append(block)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(block) 

                        # system
                        elif re.search(r"^system", l):
                            name, path, offset = '', '', "'h0"
                            if re.search(r"^system\s+(\w+)\s*\[(\d+)\]", l): # array
                                match = re.search(r"^system\s+(\w+)\s*\[(\d+)\]", l)
                                name = match.group(1)
                                size = match.group(2)
                                incr = 0
                                if re.search(r"^system\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l): # path/offset
                                    match = re.search(r"^system\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)\s*\+\s*(\S+);", l)
                                    path = match.group(3)
                                    offset = match.group(4)
                                    incr = match.group(5)
                                elif re.search(r"^system\s+(\w+)\s*\[(\d+)\]\s*@(\S+)\s*\+\s*(\S+);", l): # offset
                                    match = re.search(r"^system\s+(\w+)\s*\[(\d+)\]\s*\((.*)\)\s*@(\S+)", l)
                                    offset = match.group(3)
                                    incr = match.group(4)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))
                                
                                oset_prefix, oset_value = hex_proc(offset)
                                _incr_prefix, incr_value = hex_proc(incr)
                                oset = oset_prefix + format(oset_value, 'x')

                                for i in range(int(size)):
                                    name_i = "{}_{}".format(name, i)
                                    path_i = path.replace("%d", str(i))
                                    system = None
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "System" in str(type(d)):
                                            system = copy.deepcopy(d)
                                            break
                                    if not system:
                                        print("Error {}:'{}' - Cannot find definition".format(nu, l))

                                    system.level, system.name, system.offset, system.path = level, name_i, oset, path_i
                                    hier[-1].subs.append(system)
                                    oset_value += incr_value
                                    oset = oset_prefix + format(oset_value, 'x')

                            else: # non array
                                if re.search(r"^system\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l): # name/path/offset
                                    match = re.search(r"^system\s+(\w+)\s*\((.*)\)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                    offset = match.group(3)
                                elif re.search(r"^system\s+(\w+)\s*@\s*(\S+)\s*[{;]", l): # name/offset
                                    match = re.search(r"^system\s+(\w+)\s*@\s*(\S+)\s*[{;]", l)
                                    name = match.group(1)
                                    offset = match.group(2)
                                elif re.search(r"^system\s+(\w+)\s*\((.*)\)", l): # name/path
                                    match = re.search(r"^system\s+(\w+)\s*\((.*)\)", l)
                                    name = match.group(1)
                                    path = match.group(2)
                                elif re.search(r"^system\s+(\w+)", l): # name
                                    match = re.search(r"^system\s+(\w+)", l)
                                    name = match.group(1)
                                else:
                                    print("Error {}:'{}' - Unsupported format".format(nu, l))

                                system = System(level=level, name=name, offset=offset, path=path, 
                                    subs=[])

                                if level: # sub level
                                    # find from define list
                                    for d in defs:
                                        if d.name == name and "System" in str(type(d)):
                                            system = copy.deepcopy(d)
                                            system.level, system.offset, system.path = level, offset, path
                                            break
                                    hier[-1].subs.append(system)

                                if re.search(r"{\s*$", l): # new description
                                    hier.append(system) 


# Only run the following code when this file is the main file being run
if __name__=='__main__':
    main()
