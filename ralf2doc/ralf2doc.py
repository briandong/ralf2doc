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
    def __init__(self, name, info='', bits=1, access='rw', reset='0', offset='0', path='', level=0):
        self.name = name
        self.info = info
        self.bits = bits
        self.access = access
        self.reset = reset
        self.offset = offset
        self.path = path
        self.level = level
    def __str__(self):
        s = '''
{indent}Field: {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bits:   {bits}
{indent}  Access: {access}
{indent}  Reset:  {reset}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bits=self.bits, 
            access=self.access, 
            reset=self.reset, 
            path=self.path,
            level=self.level,
            )
        return s
    #def __repr__(self):
    #    return self.__str__()

# Register defines a concatenation of fields.
# Registers are used in register files and blocks.
class Register:
    def __init__(self, name, info='', bytes=4, leftright=False, offset='0', path='', fields=[], level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.fields = fields
        self.level = level
    def __str__(self):
        s = '''
{indent}Register: {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bytes:  {bytes}
{indent}  LtoR:   {leftright}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )
        for f in self.fields:
            s += str(f)
        return s

# Register files defines a collection of consecutive registers.
# Register files are used in blocks.
class Regfile:
    def __init__(self, name, info='', offset='0', path='', registers=[], level=0):
        self.name = name
        self.info = info
        self.offset = offset
        self.path = path
        self.registers = registers
        self.level = level
    def __str__(self):
        s = '''
{indent}RegFile:  {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            path=self.path,
            level=self.level,
            )
        for r in self.registers:
            s += str(r)
        return s

# Memory defines a region of consecutive addressable locations.
# Memories are used in blocks.
class Memory:
    def __init__(self, name, info='', bits=0, size='0', access='rw', offset='0', path='', level=0):
        self.name = name
        self.info = info
        self.bits = bits
        self.size = size
        # may have k(2^10)|M(2^20)|G(2^30). total size = bits * size
        self.access = access
        self.offset = offset
        self.path = path
        self.level = level
    def __str__(self):
        s = '''
{indent}Memory:   {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            path=self.path,
            level=self.level,
            )
        return s

# Virtual register defines a concatenation of virfields fields.
# Virtual registers are used in blocks.
class Vregister:
    def __init__(self, name, info='', bytes=4, leftright=False, offset='0', path='', fields=[], level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.fields = fields
        self.level = level
    def __str__(self):
        s = '''
{indent}V_Reg:    {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bytes:  {bytes}
{indent}  LtoR:   {leftright}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )
        for f in self.fields:
            s += str(f)
        return s

# Block defines a set of registers and memories.
class Block:
    def __init__(self, name, info='', bytes=0, endian='little', offset='0', path='', 
        registers=[], vregisters=[], regfiles=[], memories=[], level=0):
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
        self.level = level
    def __str__(self):
        s = '''
{indent}Block:    {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bytes:  {bytes}
{indent}  Endian: {endian}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for r in self.registers:
            s += str(r)
        for v in self.vregisters:
            s += str(v)
        for f in self.regfiles:
            s += str(f)
        for m in self.memories:
            s += str(m)
        return s

# System defines a design composed of blocks or subsystems.
class System:
    def __init__(self, name, info='', bytes=0, endian='little', offset='0', path='', 
        blocks=[], systems=[], level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.endian = endian
        self.offset = offset
        self.path = path
        self.blocks = blocks
        self.systems = systems
        self.level = level
    def __str__(self):
        s = '''
{indent}System:   {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bytes:  {bytes}
{indent}  Endian: {endian}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent=' '*2*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for b in self.blocks:
            s += str(b)
        for s in self.systems:
            s += str(s)
        return s

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <RALF_FILE> <TARGET>".format(os.path.basename(__file__)))
    else:
        ralf = sys.argv[1]
        target = sys.argv[2]

        if not os.path.isfile(ralf):
            print("{} is not a valid file".format(ralf))
        else:
            hier = [] # hierachy list
            defs = [] # define list
            with open(ralf) as f:
                for nu, l in enumerate(f):
                    l = l.strip()
                    level = len(hier)
                    # end of definition
                    if re.search(r"^}", l):
                        item = hier.pop(-1)
                        if item.name == target:
                            print(item)
                    # info
                    if re.search(r"^#\s*(.*)", l):
                        match = re.search(r"^#\s*(.*)", l)
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
                        name, path, offset = '', '', '0'
                        if re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)", l): # name/path/offset
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)\s+@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^field\s+(\S+)\s+@(\S+)", l): # name/offset
                            match = re.search(r"^field\s+(\S+)\s+@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^field\s+(\S+)\s+\((.*)\)", l): # name/path
                            match = re.search(r"^field\s+(\S+)\s+\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^field\s+(\S+)", l): # name
                            match = re.search(r"^field\s+(\S+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported field format in line {}: '{}'".format(nu, l))

                        field = Field(level=level, name=name, offset=offset, path=path)

                        if not level: # top level
                            defs.append(field)
                        else: # sub level
                            hier[-1].fields.append(field)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(field)

                    # register
                    if re.search(r"^register", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)", l): # name/path/offset
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)\s+@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^register\s+(\S+)\s+@(\S+)", l): # name/offset
                            match = re.search(r"^register\s+(\S+)\s+@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^register\s+(\S+)\s+\((.*)\)", l): # name/path
                            match = re.search(r"^register\s+(\S+)\s+\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^register\s+(\S+)", l): # name
                            match = re.search(r"^register\s+(\S+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported register format in line {}: '{}'".format(nu, l))

                        register = Register(level=level, name=name, offset=offset, path=path)

                        if not level: # top level
                            defs.append(register)
                        else: # sub level
                            hier[-1].registers.append(register)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(register) 

                    # memory
                    if re.search(r"^memory", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)", l): # name/path/offset
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)\s+@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^memory\s+(\S+)\s+@(\S+)", l): # name/offset
                            match = re.search(r"^memory\s+(\S+)\s+@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^memory\s+(\S+)\s+\((.*)\)", l): # name/path
                            match = re.search(r"^memory\s+(\S+)\s+\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^memory\s+(\S+)", l): # name
                            match = re.search(r"^memory\s+(\S+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported memory format in line {}: '{}'".format(nu, l))

                        memory = Memory(level=level, name=name, offset=offset, path=path)

                        if not level: # top level
                            defs.append(memory)
                        else: # sub level
                            hier[-1].memories.append(memory)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(memory) 

                    # block
                    if re.search(r"^block", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)", l): # name/path/offset
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)\s+@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^block\s+(\S+)\s+@(\S+)", l): # name/offset
                            match = re.search(r"^block\s+(\S+)\s+@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^block\s+(\S+)\s+\((.*)\)", l): # name/path
                            match = re.search(r"^block\s+(\S+)\s+\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^block\s+(\S+)", l): # name
                            match = re.search(r"^block\s+(\S+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported block format in line {}: '{}'".format(nu, l))

                        block = Block(level=level, name=name, offset=offset, path=path)

                        if not level: # top level
                            defs.append(block)
                        else: # sub level
                            hier[-1].blocks.append(block)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(block) 

                    # system
                    if re.search(r"^system", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)", l): # name/path/offset
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)\s+@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^system\s+(\S+)\s+@(\S+)", l): # name/offset
                            match = re.search(r"^system\s+(\S+)\s+@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^system\s+(\S+)\s+\((.*)\)", l): # name/path
                            match = re.search(r"^system\s+(\S+)\s+\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^system\s+(\S+)", l): # name
                            match = re.search(r"^system\s+(\S+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported system format in line {}: '{}'".format(nu, l))

                        system = System(level=level, name=name, offset=offset, path=path)

                        if not level: # top level
                            defs.append(system)
                        else: # sub level
                            hier[-1].systems.append(system)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(system) 


# Only run the following code when this file is the main file being run
if __name__=='__main__':
    main()
