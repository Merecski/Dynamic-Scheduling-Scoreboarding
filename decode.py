#########################################################
#                                                       #
#    EECE 552 Computer Design Project 1                 #
#    Authors: Eugene Merecki                            #
#    Description: MIPS Scoreboarding Algorithm          #
#    Futher details in README.txt File                  #
#                                                       #
#########################################################

import re

class Instruction:
    def __init__(self, repr, op, dst, src1, src2):
        self.issued = self.read = self.executed = self.written = -1
        self.op = op          # instruction operation
        self.fi = dst         # destination register
        self.fj = src1        # source register
        self.fk = src2        # source register
        self.repr = repr      # string representation or instruction

    def print_inst(self):
        #pre-scripted function to print instructions out
        return "%-24s%-8d%-8d%-8d%-8d" % \
        (self.repr, self.issued, self.read, self.execute, self.written)

    def clean(self):
        self.issued = self.read = self.executed = self.written = -1


def split_instruction(instruction):
    """
    Inital spliting of command procesure
    splits where ',' exist
    removes all empty entities in list
    """
    inst = re.split(',| ', instruction)
    return list(filter(None, inst))

def __load(inst):
    """
    Taking op code and finding corresponding FU type from dictionary
    looking for memory to load from
    destination register stripped
    return object with assigned variables
    """
    inst_split = split_instruction(inst)
    op = functional_units[inst_split[0]]
    fi = inst_split[1]
    fk = re.search('\((.*)\)', inst_split[2]).group(1)
    return Instruction(inst, op, fi, None, fk)

def __store(inst):
    inst_split = split_instruction(inst)
    op = functional_units[inst_split[0]]
    fi = inst_split[1]
    mem = re.sub('[()]', '', inst_split[2]).split('$')
    #Adjust register if $1
    fk = int(mem[0]) + int(mem[1])*17
    return Instruction(inst, op, fk, None, fi)

def __branch(inst):
    inst_split = split_instruction(inst)
    op = functional_units[inst_split[0]]
    #destination register
    fi = inst_split[1]
    #source 1 register
    fj = inst_split[2]
    #source 2 register
    fk = inst_split[3]
    #return object with assigned variables
    return Instruction(inst, op, fi, fj, fk)

def __arithmetic(inst):
    inst_split = split_instruction(inst)
    op = functional_units[inst_split[0]]
    fi = inst_split[1]
    fj = inst_split[2]
    fk = inst_split[3]
    return Instruction(inst, op, fi, fj, fk)


instructions = {
    #Variable function names to point op code to correct spliting method
    #for loading instructions
    'L.D':        __load,
    'S.D':        __store,
    'BEQ':        __branch,
    'BNE':        __branch,
    'ADD':        __arithmetic,
    'ADDI':        __arithmetic,
    'SUB':        __arithmetic,
    'SUBI':        __arithmetic,
    'ADD.D':    __arithmetic,
    'SUB.D':    __arithmetic,
    'MULT.D':    __arithmetic,
    'DIV.D':    __arithmetic,
    }

functional_units = {
    #Corresponding Functional Unit types and Instructions
    'L.D':        'integer',
    'S.D':        'integer',
    'BEQ':        'integer',
    'BNE':        'integer',
    'ADD':        'integer',
    'ADDI':        'integer',
    'SUBI':        'integer',
    'ADD.D':    'add',
    'SUB.D':    'add',
    'MULT.D':    'mult',
    'DIV.D':    'div',
}

