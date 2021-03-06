#!/usr/bin/env python
# -*- coding: utf-8 -*-

' this script defines ralf classes '

__author__ = "Bo DONG"

import sys, os
import re

# Field defines an atomic set of consecutive bits.
# Fields are concatenated into registers.
class Field:
    def __init__(self, name, info='', bits=1, access='rw', reset='0', offset=0, path='', level=0):
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
{indent}Field:    {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Bits:   {bits}
{indent}  Access: {access}
{indent}  Reset:  {reset}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent='  '*self.level, 
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
    def csv(self):
        s = '''
{indent}Field, Info, Offset,  Bits, Access, Reset, Path, Level
{indent}  {name}, {info}, {offset}, {bits}, {access}, {reset}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
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
    def vhdr(self):
        return ''

# Register defines a concatenation of fields.
# Registers are used in register files and blocks.
class Register:
    def __init__(self, name, info='', bytes=4, leftright=False, offset="'h0", path='', subs=[], 
        fname='', addr='0', level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.subs = subs
        self.fname = fname # full name
        self.addr = addr   # absolute address
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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )
        os = 0
        for i in self.subs:
            i.level = self.level + 1
            i.offset = os
            os += i.bits
            s += str(i)
        return s
    def csv(self):
        s = '''
{indent}Register, Info, Offset,  Bytes, LtoR, Path, Level
{indent}  {name}, {info}, {offset}, {bytes}, {leftright}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )

        s += '''
{indent}Field, Info, Offset, Bits, Access, Reset, Path, Level '''.format(
            indent=' , '*(self.level+1), 
            )

        os = 0
        for i in self.subs:
            i.level = self.level + 1
            i.offset = os
            os += i.bits
        
        for i in reversed(self.subs):
            s += '''
{indent}  {name}, {info}, {offset}, {bits}, {access}, {reset}, {path}, {level} '''.format(
                indent=' , '*i.level, 
                name=i.name,
                info=i.info,
                offset=str(i.offset),
                bits=str(i.bits),
                access=i.access,
                reset=i.reset,
                path=i.path,
                level=str(i.level),
                )

        s += '\n'
        return s
    def vhdr(self):
        s = '''`define {} {}
'''.format(self.fname, self.addr)
        return s

# Register files defines a collection of consecutive registers.
# Register files are used in blocks.
class Regfile:
    def __init__(self, name, info='', offset="'h0", path='', subs=[], fname='', addr='0', level=0):
        self.name = name
        self.info = info
        self.offset = offset
        self.path = path
        self.subs = subs
        self.fname = fname # full name
        self.addr = addr   # absolute address
        self.level = level
    def __str__(self):
        s = '''
{indent}RegFile:  {name}
{indent}  Info:   {info}
{indent}  Offset: {offset}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += str(i)
        return s
    def csv(self):
        s = '''
{indent}RegFile, Info, Offset, Path, Level
{indent}  {name}, {info}, {offset}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += i.csv()
        return s
    def vhdr(self):
        s = '''//--------------------
// RegFile Hearders: {}, Offset: {}
//--------------------
'''.format(self.fname, self.addr)
        for i in self.subs:
            i.fname = self.fname+'_'+i.name.upper()
            addr_prefix, addr_value = hex_proc(self.addr)
            _sub_prefix, sub_value = hex_proc(i.offset)
            i.addr = addr_prefix + format(addr_value + sub_value, 'x')
            s += i.vhdr()
        return s

# Memory defines a region of consecutive addressable locations.
# Memories are used in blocks.
class Memory:
    def __init__(self, name, info='', bits=0, size='0', access='rw', offset="'h0", path='', level=0):
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
{indent}  Bits:   {bits}
{indent}  Size:   {size}
{indent}  Access: {access}
{indent}  Path:   {path}
{indent}  Level:  {level}
        '''.format(
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bits=self.bits, 
            size=self.size, 
            access=self.access, 
            path=self.path,
            level=self.level,
            )
        return s
    def csv(self):
        s = '''
{indent}Memory, Info, Offset,  Bits, Size, Access, Path, Level
{indent}  {name}, {info}, {offset}, {bits}, {size}, {access}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bits=self.bits, 
            size=self.size, 
            access=self.access, 
            path=self.path,
            level=self.level,
            )
        return s
    def vhdr(self):
        return ''

# Virtual register defines a concatenation of fields.
# Virtual registers are used in blocks.
class Vregister:
    def __init__(self, name, info='', bytes=4, leftright=False, offset="'h0", path='', subs=[], 
        fname='', addr='0', level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.leftright = leftright
        self.offset = offset
        self.path = path
        self.subs = subs
        self.fname = fname # full name
        self.addr = addr   # absolute address
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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )
        os = 0
        for i in self.subs:
            i.level = self.level + 1
            i.offset = os
            os += i.bits
            s += str(i)
        return s
    def csv(self):
        s = '''
{indent}V_Reg, Info, Offset,  Bytes, LtoR, Path, Level
{indent}  {name}, {info}, {offset}, {bytes}, {leftright}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            leftright=self.leftright,
            path=self.path,
            level=self.level,
            )

        s += '''
{indent}Field, Info, Offset, Bits, Access, Reset, Path, Level '''.format(
            indent=' , '*(self.level+1), 
            )

        os = 0
        for i in self.subs:
            i.level = self.level + 1
            i.offset = os
            os += i.bits

        for i in reversed(self.subs):
            s += '''
{indent}  {name}, {info}, {offset}, {bits}, {access}, {reset}, {path}, {level} '''.format(
                indent=' , '*i.level, 
                name=i.name,
                info=i.info,
                offset=str(i.offset),
                bits=str(i.bits),
                access=i.access,
                reset=i.reset,
                path=i.path,
                level=str(i.level),
                )

        s += '\n'
        return s
    def vhdr(self):
        s = '''`define {} {}
'''.format(self.fname, self.addr)
        return s

# Block defines a set of registers and memories.
class Block:
    def __init__(self, name, info='', bytes=0, endian='little', offset="'h0", path='', 
        subs=[], fname='', addr='0', level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.endian = endian
        self.offset = offset
        self.path = path
        self.subs = subs
        self.fname = fname # full name
        self.addr = addr   # absolute address
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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += str(i)
        return s
    def csv(self):
        s = '''
{indent}Block, Info, Offset,  Bytes, Endian, Path, Level
{indent}  {name}, {info}, {offset}, {bytes}, {endian}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += i.csv()
        return s
    def vhdr(self):
        s = '''//--------------------
// Block Hearders: {}, Offset: {}
//--------------------
'''.format(self.fname, self.addr)
        for i in self.subs:
            i.fname = self.fname+'_'+i.name.upper()
            addr_prefix, addr_value = hex_proc(self.addr)
            _sub_prefix, sub_value = hex_proc(i.offset)
            i.addr = addr_prefix + format(addr_value + sub_value, 'x')
            s += i.vhdr()
        return s


# System defines a design composed of blocks or subsystems.
class System:
    def __init__(self, name, info='', bytes=0, endian='little', offset="'h0", path='', 
        subs=[], fname='', addr='0', level=0):
        self.name = name
        self.info = info
        self.bytes = bytes
        self.endian = endian
        self.offset = offset
        self.path = path
        self.subs = subs
        self.fname = fname # full name
        self.addr = addr   # absolute address
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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += str(i)
        return s
    def csv(self):
        s = '''
{indent}System, Info, Offset,  Bytes, Endian, Path, Level
{indent}  {name}, {info}, {offset}, {bytes}, {endian}, {path}, {level}
        '''.format(
            indent=' , '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for i in self.subs:
            i.level = self.level + 1
            s += i.csv()
        return s
    def vhdr(self):
        s = '''//--------------------
// System Hearders: {}, Offset: {}
//--------------------
'''.format(self.fname, self.addr)
        for i in self.subs:
            i.fname = self.fname+'_'+i.name.upper()
            addr_prefix, addr_value = hex_proc(self.addr)
            _sub_prefix, sub_value = hex_proc(i.offset)
            i.addr = addr_prefix + format(addr_value + sub_value, 'x')
            s += i.vhdr()
        return s


# hex processing
# returns a string prefix and an integer value
def hex_proc(hex_str):
    prefix, value = '', 0
    hex_str = hex_str.replace('_', '') # remove '_'
    if re.search(r"(.*('h|0x|0X))(\w+)", hex_str): # start w. 'h|0x|0X
        match = re.search(r"(.*('h|0x|0X))(\w+)", hex_str)
        prefix = match.group(1)
        value = int(match.group(3), 16)
    else: # w.o. prefix
        value = int(hex_str, 16)

    return (prefix, value)
