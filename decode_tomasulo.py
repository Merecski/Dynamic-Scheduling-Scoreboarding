#########################################################
#							#
#	EECE 552 Computer Design Project 1		#
#	Authors: Eugene Merecki, Sarah Prechtl		#
#	Description: MIPS Scoreboarding Algorithm	#
#	Futher details in README.txt File		#
#							#
#########################################################

import re

class Instruction:
	def __init__(self, repr, op, dst, src1, src2):
		self.issued = self.commit = self.executed = self.written = -1
		self.tag = None
		self.op = op          # instruction operation	
		self.fi = dst         # destination register
		self.fj = src1        # source register
		self.fk = src2        # source register
		self.di = self.dj = self.dk = None #For common data bus
		self.repr = repr      # string representation or instruction

	def print_inst(self):					#pre-scripted function to print instructions out
		return "%-24s%-8d%-8d%-8d" % \
		(self.repr, self.issued, self.written, self.commit)

	def clean(self):
		self.issued = self.executed = self.written = self.commit = -1


def split_instruction(instruction):				#Inital spliting of command procesure
	inst = re.split(',| ', instruction)			#splits where ',' exist
	return list(filter(None, inst))				#removes all empty entities in list

def __load(inst):
	inst_split = split_instruction(inst)
	op = functional_units[inst_split[0]]			#Taking op code and finding corresponding FU type from dictionary
	fi = inst_split[1]					#destination register stripped
	fk = re.search('\((.*)\)', inst_split[2]).group(1)	#looking for memory to load from
	return Instruction(inst, op, fi, None, fk)		#return object with assigned variables

def __store(inst):
	inst_split = split_instruction(inst)
	op = functional_units[inst_split[0]]
	fi = inst_split[1]
	mem = re.sub('[()]', '', inst_split[2]).split('$')
	fk = int(mem[0]) + int(mem[1])*17			#Adjust memory if $1
	return Instruction(inst, op, fk, None, fi)

def __branch(inst):
	inst_split = split_instruction(inst)
	op = functional_units[inst_split[0]]
	fi = inst_split[1]				#destination register
	fj = inst_split[2]				#source 1 register
	fk = inst_split[3]				#source 2 register
	return Instruction(inst, op, fi, fj, fk)	#return object with assigned variables

def __arithmetic(inst):
	inst_split = split_instruction(inst)
	op = functional_units[inst_split[0]]
	fi = inst_split[1]
	fj = inst_split[2]
	fk = inst_split[3]
	return Instruction(inst, op, fi, fj, fk)


instructions = {			#Variable function names to point op code to correct spliting method
	'L.D':		__load,		#for loading instructions
	'S.D':		__store,	#for storing instructions
	'BEQ':		__branch,	#for any branches that create branches
	'BNE':		__branch,	
	'ADD':		__arithmetic,	#Any arithmetic related instructions
	'ADDI':		__arithmetic,
	'SUB':		__arithmetic,
	'SUBI':		__arithmetic,
	'ADD.D':	__arithmetic,
	'SUB.D':	__arithmetic,
	'MULT.D':	__arithmetic,
	'DIV.D':	__arithmetic,
	}

functional_units = {			#Corresponding Functional Unit types and Instructions
	'L.D':		'integer',	#All instructions with type integer
	'S.D':		'integer',
	'BEQ':		'integer',
	'BNE':		'integer',
	'ADD':		'integer',
	'ADDI':		'integer',
	'SUBI':		'integer',
	'ADD.D':	'add',		#All instructions with type add
	'SUB.D':	'add',
	'MULT.D':	'mult',		#All instructions with type mult
	'DIV.D':	'div',		#All instructions with type div
}

