#!/usr/bin/env python3

import os
import subprocess
import sys

if sys.platform.startswith('win'):
    PathVar = os.environ.get('Path')
    Paths = PathVar.split(';')
    PATH = ''
    for candidatePath in Paths:
        if 'devkitARM' in candidatePath:
            PATH = candidatePath
            break
    if PATH == '':
        PATH = 'C://devkitPro//devkitARM//bin'
        if os.path.isdir(PATH) is False:
            print('Devkit not found, trying executables on PATH...')
            PATH = ''

    PREFIX = 'arm-none-eabi-'
    OBJDUMP = os.path.join(PATH, PREFIX + 'objdump')
    NM = os.path.join(PATH, PREFIX + 'nm')
    AS = os.path.join(PATH, PREFIX + 'as')

else:  # Linux, OSX, etc.
    if os.path.exists('/opt/devkitpro/devkitARM/bin/'):
        PREFIX = '/opt/devkitpro/devkitARM/bin/arm-none-eabi-'
    else:
        PREFIX = 'arm-none-eabi-'
    OBJDUMP = (PREFIX + 'objdump')
    if sys.platform.startswith('darwin'):
        NM = ('nm')
    else:
        NM = (PREFIX + 'nm')
    AS = (PREFIX + 'as')


def GetSymbols(args, subtract=0) -> {str: int}:
    if (len(args) > 0):
        outFile = args[1].strip()
    else:
        outFile = 'build/linked.o'
    out = subprocess.check_output([NM, outFile])
    lines = out.decode().split('\n')

    ret = {}
    for line in lines:
        parts = line.strip().split()

        if len(parts) < 3:
            continue

        if parts[1].lower() not in {'t', 'd'}:
            continue

        offset = int(parts[0], 16)
        ret[parts[2]] = offset - subtract
        if parts[1].lower() in {'t'}:
            ret[parts[2]] = ret[parts[2]] + 1

    return ret


def writeall(args):
    print("Generating linker script...")
    table = GetSymbols(args)

    if (len(args) > 0):
        ldFile = args[0].strip()
    else:
        ldFile = 'rom_gen.ld'

    if os.path.isfile(ldFile):
        offsetIni = open(ldFile, 'a')
    else:
        offsetIni = open(ldFile, 'w')

    offsetIni.truncate()
    offsetIni.write("\n/* begin autogenerated portion */\n\n")
    for key in sorted(table.keys()):
        offsetIni.write(key + ' = ' + hex(table[key]) + ';\n')
    offsetIni.close()


if __name__ == '__main__':
    if (len(sys.argv) > 0):
        args = sys.argv[1:]
    writeall(args)
