#Refernce: https://www.cs.umd.edu/class/fall2001/cmsc411/projects/dynamic/example1.html

#########################################################
#							#
#	EECE 552 Computer Design Project 1		#
#	Authors: Eugene Merecki, Sarah Prechtl		#
#	Description: MIPS Scoreboarding Algorithm	#
#	Futher details in README.txt File		#
#							#
#########################################################

import re

class FunctionalUnit:

	def __init__(self, ftype, clk):
		self.type = ftype
		self.clk = clk
		self.default_clk = clk
		self.busy = False
		self.fi = self.fj = self.fk = None
		self.di = self.dj = self.dk = None
		self.qj = self.qk = None
		self.rj = self.rk = None     
		self.inst_count = -1
		self.repr = None
		self.dst_value = None
		self.src1_value = None
		self.scr2_value = None
		self.bf = False
		self.is_branch = False


	def issue(self, instruction, register_status):
		self.busy = True
		self.repr = instruction.repr.split()

		if instruction.repr.split()[0][0] is 'B':	#Checking if instruction is a branch of self programing purposes
			self.fi = instruction.fk
			self.fj = instruction.fi
			self.fk = instruction.fj
		else:
			self.fi = instruction.fi		#setting all the instruction Register dependencies 
			self.fj = instruction.fj		#to the FU's dependencies
			self.fk = instruction.fk
			
			self.dj = instruction.dj
			self.dk = instruction.dk
			#if instruction.dj == None:
			#	self.dj = instruction.fj
			#else:
			#	self.dj = instruction.dj
			#if instruction.dk == None:
			#	self.dk = instruction.fk
			#else:
			#	self.dk = instruction.dk
				
		if instruction.fj in register_status:			#checking for hazards and setting flags if so
			self.qj = register_status[instruction.fj]
		if instruction.fk in register_status:
			self.qk = register_status[instruction.fk]

		self.rj = not self.qj
		self.rk = not self.qk
		
	def issued(self):
		return self.busy and self.clk > 0	#if it is busy and clk isn't at 0, Fu must have been issued
		
	def clear(self):				#reseting all values back to initial vlaues
		self.clk = self.default_clk
		self.fi = self.fj = self.fk = None
		self.qj = self.qk = None	
		self.rj = self.rk = True	
		self.inst_pc = -1
		self.busy = False
		
	def read(self, mem, reg, cdb):
		#print self.fj
		self.runtime(mem, reg,cdb)		#function caled to run instruction operation
		self.rj = self.rk = False	#Set Read dependency flags to false

	
	def execute(self):
		self.clk -= 1		#everytime the function is called, it subtracts from remaining clk cycles
	
	def write(self, f_units):
		for f in f_units:		#updating hazards for the entire functional unit
			if f.qj == self:
				f.rj = True
				f.qj = None
			if f.qk == self:
				f.rk = True
				f.qk = None
		return self.dst_value
				
				
	def runtime(self, mem, reg,cdb):				#function to perform actual instruction
		command = command_list.get(self.repr[0])
		command(self, mem, reg, cdb)
		
#########################################################################
#	All of the Arithmetic and Branch Comparing operations		#
#	to update the registers and detect taken branches.		#
#	Follows similar procedure from decode with variable		#
#	functions are assigned to each opcode to execute.		#
#	These are executed in the background during the read stage.	#
#	However the value is stored and isn't written to memory		#
#	or a registered until the WRITE stage is called			#
#########################################################################

def __load(self, mem, reg, cdb):
		ld = re.sub('[()]', '', self.repr[2]).split('$')
		location = int(ld[0]) + int(ld[1])*17
		self.dst_value = float(mem[location])

def __store(self, mem, reg, cdb):
	return
def __beq(self, mem, reg):
	self.is_branch = True
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dj != None:
		self.src2_value = int(cdb[self.dk])
	else: 
		self.src2_value = int(reg[self.fk])
	if self.src1_value == self.src2_value:
		self.bf = True
	else:
		self.bf = False
def __bne(self, mem, reg):
	self.is_branch = True
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dj != None:
		self.src2_value = int(cdb[self.dk])
	else: 
		self.src2_value = int(reg[self.fk])
	if self.src1_value != self.src2_value:
		self.bf = True
	else:
		self.bf = False
def __add(sef, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = int(cdb[self.dk])
	else: 
		self.src2_value = int(reg[self.fk])
	self.dst_value = self.src1_value + self.src2_value
def __addi(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = int(self.dk)
	else: 
		self.src2_value = int(self.fk)
	self.dst_value = self.src1_value + self.src2_value
def __subi(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = int(self.dk)
	else: 
		self.src2_value = int(self.fk)
	self.dst_value = self.src1_value + self.src2_value
def __addd(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = int(cdb[self.dk])
	else: 
		self.src2_value = int(reg[self.fk])
	self.dst_value = self.src1_value + self.src2_value
def __subd(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = int(cdb[self.dk])
	else: 
		self.src2_value = int(reg[self.fk])
	self.dst_value = self.src1_value + self.src2_value
def __mult(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
		
	if self.dk != None:
		self.src2_value = float(cdb[self.dk])
	else: 
		self.src2_value = float(reg[self.fk])
	self.dst_value = self.src1_value * self.src2_value
def __div(self, mem, reg, cdb):
	if self.dj != None:
		self.src1_value = int(cdb[self.dj])
	else: 
		self.src1_value = int(reg[self.fj])
	if self.dk != None:
		self.src2_value = float(cdb[self.dk])
	else: 
		self.src2_value = float(reg[self.fk])
	self.dst_value = self.src1_value / self.src2_value

command_list = {
	'L.D':		__load,
	'S.D':		__store,
	'BEQ':		__beq,
	'BNE':		__bne,
	'ADD':		__add,
	'ADDI':		__addi,
	'SUBI':		__subi,
	'ADD.D':	__addd,
	'SUB.D':	__subd,
	'MULT.D':	__mult,
	'DIV.D':	__div,
}


