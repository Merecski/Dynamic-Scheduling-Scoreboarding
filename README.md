# EECE 552 Computer Design MIPS Scoreboarding Algorithm Project

### Authors: Eugene Merecki

### Description: 

This program is coded with Python 2.7.12 and was tested on a VirtualBox of Ubuntu.
____________________________________________________________________________________

## Functional Unit:

To specify properties of a Functional Unit in the input file the line must begin with a period '.'
Immediately afterwards will be the type of FU (integer, add, mult, div).
The next two spaced integers will be the number of FUs being created then the length of its clock cycle
The format and an example are as follows:

Format: .[FU type] [number of FUs] [number of clock cycles]
Example: .integer 2 1
____________________________________________________________________________________

## MIPS Instructions:

Without a period, it will be assumed as an instruction.
The formatting of the instruction follows standard MIPS structure.
There are 32 Floating point registers. These are referenced with an 'F' then 0-31
Example: F15
There are 32 Integer registers. These are referenced with a '$' then 0-31
Example: $15

[OP code] [Destination register] [Source 1 register] [Source 2 Register]
ADD.D F3, F4, F3
ADD $5, $3, $2
___________________________________________________________________________________

## Branches:

Branches are are FULLY functional. They are not assuming either always taken or not always taken.
WARNING: endless loops will be created unless the instructions make sense.
Activating a branch will result in a loop of instructions being inserted into the existing list of instructions.
___________________________________________________________________________________

When creating the input file, there must NOT be any empty lines. 
Otherwise the program will not run because of a null instruction.

## Example Input File (with looping):
.integer 2 1
.mult 2 10
.add 4 2
.div 1 40
L.D F4, 10($0)
L.D F2, 0($0)
L.D F1, 9($0)
ADDI F2, F2, 1
MULT.D F3, F4, F2
DIV.D F1, F1, F1
DIV.D F10, F3, F3
ADD.D F3, F3, F3
ADD.D F2, F2, F1
BNE F2, F4, 4
MULT.D F5, F4, F4
SUB.D F6, F5, F4
S.D F3, 0($0)
S.D F4, 2($0)
S.D $5, 3($0)
