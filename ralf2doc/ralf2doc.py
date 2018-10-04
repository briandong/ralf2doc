#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a script generates register docs based on ralf file '

__author__ = "Bo DONG"

import sys, os
import re

def func():
    return "Hello World!"

# Field defines an atomic set of consecutive bits.
# Fields are concatenated into registers.
class Field:
    def __init__(self, name, info='', bits=1, access='rw', reset='0', offset='0', path=''):
        self.name = name
        self.info = info
        self.bits = bits
        self.access = access
        self.reset = reset
        self.offset = offset
        self.path = path

# Register defines a concatenation of fields.
# Registers are used in register files and blocks.
class Register:
    def __init__(self, name, info='', bytes=4, leftright=False, offset='0', path='', fields=[]):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.fields = fields

# Register files defines a collection of consecutive registers.
# Register files are used in blocks.
class Regfile:
    def __init__(self, name, info='', registers=[]):
        self.name = name
        self.info = info
        self.registers = registers

# Memory defines a region of consecutive addressable locations.
# Memories are used in blocks.
class Memory:
    def __init__(self, name, info='', bits=0, size='0', access='rw', offset='0', path=''):
        self.name = name
        self.info = info
        self.bits = bits
        self.size = size
        # may have k(2^10)|M(2^20)|G(2^30). total size = bits * size
        self.access = access
        self.offset = offset
        self.path = path

# Virtual register defines a concatenation of virfields fields.
# Virtual registers are used in blocks.
class Vregister:
    def __init__(self, name, info='', bytes=4, leftright=False, offset='0', path='', fields=[]):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.fields = fields

# Block defines a set of registers and memories.
class Block:
    def __init__(self, name, info='', bytes=0, endian='little', offset='0', path='', registers=[], vregisters=[], regfiles=[], memories=[]):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.endian = endian
        self.offset = offset
        self.path = path
        self.registers = registers
        self.vregisters = vregisters
        self.regfiles = regfiles
        self.memories = memories

# System defines a design composed of blocks or subsystems.
class System:
    def __init__(self, name, info='', bytes=0, endian='little', offset='0', path='', blocks=[], systems=[]):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.endian = endian
        self.offset = offset
        self.path = path
        self.blocks = blocks
        self.systems = systems


def main():
    if len(sys.argv) != 3:
        print("Usage: {} <RALF_FILE> <TOP_MODULE>".format(os.path.basename(__file__)))
    else:
        ralf = sys.argv[1]
        top = sys.argv[2]

        if not os.path.isfile(ralf):
            print("{} is not a valid file".format(ralf))
        else:
            hier = [] # hierachy list
            with open(ralf) as f:
                for nu, l in enumerate(f):
                    l = l.strip()
                    # end of definition
                    if re.search(r"^}", l):
                        print(hier.pop(-1))
                    # info
                    if re.search(r"^#", l):
                        match = re.search(r"^#(.*)", l)
                        hier[-1].info += match.group(1)
                    # bits
                    if re.search(r"^bits\s+(\d+)\s*;", l):
                        match = re.search(r"^bits\s+(\d+)\s*;", l)
                        hier[-1].bits = match.group(1)
                    # access
                    if re.search(r"^access\s+(\w+)\s*;", l):
                        match = re.search(r"^access\s+(\w+)\s*;", l)
                        hier[-1].access = match.group(1)
                    # reset
                    if re.search(r"^reset\s+(\S+)\s*;", l):
                        match = re.search(r"^reset\s+(\S+)\s*;", l)
                        hier[-1].reset = match.group(1)
                    # bytes
                    if re.search(r"^bytes\s+(\d+)\s*;", l):
                        match = re.search(r"^bytes\s+(\d+)\s*;", l)
                        hier[-1].bytes = match.group(1)
                    # endian
                    if re.search(r"^endian\s+(\S+)\s*;", l):
                        match = re.search(r"^endian\s+(\S+)\s*;", l)
                        hier[-1].endian = match.group(1)
                    # size
                    if re.search(r"^size\s+(\S+)\s*;", l):
                        match = re.search(r"^size\s+(\S+)\s*;", l)
                        hier[-1].size = match.group(1)
                    # leftright
                    if re.search(r"^left_to_right\s*;", l):
                        match = re.search(r"^left_to_right\s*;", l)
                        hier[-1].leftright = True

                    # field
                    if re.search(r"^field", l):
                        # definition
                        if re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l): # name/path/offset
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier.append(Field(name=name, offset=offset, path=path))
                        elif re.search(r"^field\s+(\S+)\s+@(\S+)\s*{", l): # name/offset
                            match = re.search(r"^field\s+(\S+)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Field(name=name, offset=offset))
                        elif re.search(r"^field\s+(\S+)\s+\((.*)\)\s*{", l): # name/path
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Field(name=name, offset=offset))
                        elif re.search(r"^field\s+(\S+)\s*{", l): # name
                            match = re.search(r"^field\s+(\S+)\s*{", l)
                            name = match.group(1)
                            hier.append(Field(name=name))
                        # instance only
                        elif re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l): # name/path/offset
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier[-1].fields.append(Field(name=name, offset=offset, path=path))
                        elif re.search(r"^field\s+(\S+)\s+@(\S+)\s*;", l): # name/offset
                            match = re.search(r"^field\s+(\S+)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].fields.append(Field(name=name, offset=offset))
                        elif re.search(r"^field\s+(\S+)\s+\((.*)\)\s*;", l): # name/path
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].fields.append(Field(name=name, offset=offset))
                        elif re.search(r"^field\s+(\S+)\s*;", l): # name
                            match = re.search(r"^field\s+(\S+)\s*;", l)
                            name = match.group(1)
                            hier[-1].fields.append(Field(name=name))
                        else:
                            print("Error - unsupported field format in line {}: '{}'".format(nu, l))
                    # register
                    if re.search(r"^register", l):
                        # definition
                        if re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l): # name/path/offset
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier.append(Register(name=name, offset=offset, path=path))
                        elif re.search(r"^register\s+(\S+)\s+@(\S+)\s*{", l): # name/offset
                            match = re.search(r"^register\s+(\S+)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Register(name=name, offset=offset))
                        elif re.search(r"^register\s+(\S+)\s+\((.*)\)\s*{", l): # name/path
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Register(name=name, offset=offset))
                        elif re.search(r"^register\s+(\S+)\s*{", l): # name
                            match = re.search(r"^register\s+(\S+)\s*{", l)
                            name = match.group(1)
                            hier.append(Register(name=name))
                        # instance only
                        elif re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l): # name/path/offset
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier[-1].registers.append(Register(name=name, offset=offset, path=path))
                        elif re.search(r"^register\s+(\S+)\s+@(\S+)\s*;", l): # name/offset
                            match = re.search(r"^register\s+(\S+)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].registers.append(Register(name=name, offset=offset))
                        elif re.search(r"^register\s+(\S+)\s+\((.*)\)\s*;", l): # name/path
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].registers.append(Register(name=name, offset=offset))
                        elif re.search(r"^register\s+(\S+)\s*;", l): # name
                            match = re.search(r"^register\s+(\S+)\s*;", l)
                            name = match.group(1)
                            hier[-1].registers.append(Register(name=name))
                        else:
                            print("Error - unsupported register format in line {}: '{}'".format(nu, l))
                    # memory
                    if re.search(r"^memory", l):
                        # definition
                        if re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l): # name/path/offset
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier.append(Memory(name=name, offset=offset, path=path))
                        elif re.search(r"^memory\s+(\S+)\s+@(\S+)\s*{", l): # name/offset
                            match = re.search(r"^memory\s+(\S+)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Memory(name=name, offset=offset))
                        elif re.search(r"^memory\s+(\S+)\s+\((.*)\)\s*{", l): # name/path
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Memory(name=name, offset=offset))
                        elif re.search(r"^memory\s+(\S+)\s*{", l): # name
                            match = re.search(r"^memory\s+(\S+)\s*{", l)
                            name = match.group(1)
                            hier.append(Memory(name=name))
                        # instance only
                        elif re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l): # name/path/offset
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier[-1].memories.append(Memory(name=name, offset=offset, path=path))
                        elif re.search(r"^memory\s+(\S+)\s+@(\S+)\s*;", l): # name/offset
                            match = re.search(r"^memory\s+(\S+)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].memories.append(Memory(name=name, offset=offset))
                        elif re.search(r"^memory\s+(\S+)\s+\((.*)\)\s*;", l): # name/path
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].memories.append(Memory(name=name, offset=offset))
                        elif re.search(r"^memory\s+(\S+)\s*;", l): # name
                            match = re.search(r"^memory\s+(\S+)\s*;", l)
                            name = match.group(1)
                            hier[-1].memories.append(Memory(name=name))
                        else:
                            print("Error - unsupported memory format in line {}: '{}'".format(nu, l))
                    # block
                    if re.search(r"^block", l):
                        # definition
                        if re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l): # name/path/offset
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier.append(Block(name=name, offset=offset, path=path))
                        elif re.search(r"^block\s+(\S+)\s+@(\S+)\s*{", l): # name/offset
                            match = re.search(r"^block\s+(\S+)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Block(name=name, offset=offset))
                        elif re.search(r"^block\s+(\S+)\s+\((.*)\)\s*{", l): # name/path
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(Block(name=name, offset=offset))
                        elif re.search(r"^block\s+(\S+)\s*{", l): # name
                            match = re.search(r"^block\s+(\S+)\s*{", l)
                            name = match.group(1)
                            hier.append(Block(name=name))
                        # instance only
                        elif re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l): # name/path/offset
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier[-1].blocks.append(Block(name=name, offset=offset, path=path))
                        elif re.search(r"^block\s+(\S+)\s+@(\S+)\s*;", l): # name/offset
                            match = re.search(r"^block\s+(\S+)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].blocks.append(Block(name=name, offset=offset))
                        elif re.search(r"^block\s+(\S+)\s+\((.*)\)\s*;", l): # name/path
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].blocks.append(Block(name=name, offset=offset))
                        elif re.search(r"^block\s+(\S+)\s*;", l): # name
                            match = re.search(r"^block\s+(\S+)\s*;", l)
                            name = match.group(1)
                            hier[-1].blocks.append(Block(name=name))
                        else:
                            print("Error - unsupported block format in line {}: '{}'".format(nu, l))
                    # system
                    if re.search(r"^system", l):
                        # definition
                        if re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l): # name/path/offset
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier.append(System(name=name, offset=offset, path=path))
                        elif re.search(r"^system\s+(\S+)\s+@(\S+)\s*{", l): # name/offset
                            match = re.search(r"^system\s+(\S+)\s+@(\S+)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(System(name=name, offset=offset))
                        elif re.search(r"^system\s+(\S+)\s+\((.*)\)\s*{", l): # name/path
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)\s*{", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier.append(System(name=name, offset=offset))
                        elif re.search(r"^system\s+(\S+)\s*{", l): # name
                            match = re.search(r"^system\s+(\S+)\s*{", l)
                            name = match.group(1)
                            hier.append(System(name=name))
                        # instance only
                        elif re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l): # name/path/offset
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                            hier[-1].systems.append(System(name=name, offset=offset, path=path))
                        elif re.search(r"^system\s+(\S+)\s+@(\S+)\s*;", l): # name/offset
                            match = re.search(r"^system\s+(\S+)\s+@(\S+)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].systems.append(System(name=name, offset=offset))
                        elif re.search(r"^system\s+(\S+)\s+\((.*)\)\s*;", l): # name/path
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)\s*;", l)
                            name = match.group(1)
                            offset = match.group(2)
                            hier[-1].systems.append(System(name=name, offset=offset))
                        elif re.search(r"^system\s+(\S+)\s*;", l): # name
                            match = re.search(r"^system\s+(\S+)\s*;", l)
                            name = match.group(1)
                            hier[-1].systems.append(System(name=name))
                        else:
                            print("Error - unsupported system format in line {}: '{}'".format(nu, l))


# Only run the following code when this file is the main file being run
if __name__=='__main__':
    main()
