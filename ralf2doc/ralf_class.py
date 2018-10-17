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
        for f in self.fields:
            f.level = self.level + 1
            f.offset = os
            os += f.bits
            s += str(f)
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
        for f in self.fields:
            f.level = self.level + 1
            f.offset = os
            os += f.bits
        
        for f in reversed(self.fields):
            s += '''
{indent}  {name}, {info}, {offset}, {bits}, {access}, {reset}, {path}, {level} '''.format(
                indent=' , '*f.level, 
                name=f.name,
                info=f.info,
                offset=str(f.offset),
                bits=str(f.bits),
                access=f.access,
                reset=f.reset,
                path=f.path,
                level=str(f.level),
                )

        s += '\n'

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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            path=self.path,
            level=self.level,
            )
        for r in self.registers:
            r.level = self.level + 1
            s += str(r)
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
        for r in self.registers:
            r.level = self.level + 1
            s += r.csv()
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
        for f in self.fields:
            f.level = self.level + 1
            f.offset = os
            os += f.bits
            s += str(f)
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
        for f in self.fields:
            f.level = self.level + 1
            f.offset = os
            os += f.bits

        for f in reversed(self.fields):
            s += '''
{indent}  {name}, {info}, {offset}, {bits}, {access}, {reset}, {path}, {level} '''.format(
                indent=' , '*f.level, 
                name=f.name,
                info=f.info,
                offset=str(f.offset),
                bits=str(f.bits),
                access=f.access,
                reset=f.reset,
                path=f.path,
                level=str(f.level),
                )

        s += '\n'

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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for r in self.registers:
            r.level = self.level + 1
            s += str(r)
        for v in self.vregisters:
            v.level = self.level + 1
            s += str(v)
        for f in self.regfiles:
            f.level = self.level + 1
            s += str(f)
        for m in self.memories:
            m.level = self.level + 1
            s += str(m)
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
        for r in self.registers:
            r.level = self.level + 1
            s += r.csv()
        for v in self.vregisters:
            v.level = self.level + 1
            s += v.csv()
        for f in self.regfiles:
            f.level = self.level + 1
            s += f.csv()
        for m in self.memories:
            m.level = self.level + 1
            s += m.csv()
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
            indent='  '*self.level, 
            name=self.name, 
            info=self.info, 
            offset=self.offset, 
            bytes=self.bytes, 
            endian=self.endian,
            path=self.path,
            level=self.level,
            )
        for b in self.blocks:
            b.level = self.level + 1
            s += str(b)
        for y in self.systems:
            y.level = self.level + 1
            s += str(y)
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
        for b in self.blocks:
            b.level = self.level + 1
            s += b.csv()
        for y in self.systems:
            y.level = self.level + 1
            s += y.csv()
        return s
