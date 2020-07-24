#!/usr/bin/env python3

#########################################################
#                                                       #
#    EECE 552 Computer Design Project 1                 #
#    Authors: Eugene Merecki                            #
#    Description: MIPS Scoreboarding Algorithm          #
#    Futher details in README.txt File                  #
#                                                       #
#########################################################

import logging
import time

import hardware

from .fu_tomasulo import FunctionalUnit
from .decode_tomasulo import instructions as inst_funcs
from .rob import ReorderBuffer as rebuffer

FORMAT = '[%(levelname)s][%(funcName)s][%(lineno)d]: %(message)s'
LOG_LEVEL = logging.DEBUG
log = logging.getLogger(__name__)


class Tomasulo:
    def __init__(self):
        self.buffer = []
        self.units = []
        self.instructions = []
        self.memory = hardware.memory
        self.registers = hardware.registers
        self.register_status = {}
        self.cdb = {}
        self.pc = 0
        self.clock = 1

    def can_issue(self, instruction, fu):
        #check FU for WAW hazards
        #check FU for avalible functional unit
        #ignore empty instructions
        if instruction is None:
            return False
        else:
            #Checking for matching FU types, Whether matching FU type is busy,
            # and write destination is not busy
            return instruction.op == fu.type and not fu.busy and not self.buffer_full_check()

    def buffer_full_check(self):
        buffer_full = True
        for rb in self.buffer:
            if rb.busy == False:
                buffer_full = rb.busy
                return buffer_full
        return buffer_full

    def issue(self, instruction, fu):
        log.debug(instruction.print_inst())
        #Replacing expected register with CDB
        for rob in self.buffer:
            if instruction.fj == rob.fi:
                instruction.dj = rob.tag
            if instruction.fk == rob.fi:
                instruction.dk = rob.tag
            log.debug(str(instruction.fk) + ' =?= ' + str(rob.fi) + ' therefore ' + str(rob.tag))

        #Run issue function in the FU
        fu.issue(instruction, self.register_status)
        #update internal instruction issued clock variable
        self.instructions[self.pc].issued = self.clock
        #Reference point for when FU started
        fu.inst_count = self.pc
        for rb in self.buffer:
            if rb.busy != True:
                instruction.tag = rb.new_entry(fu, self.pc, instruction.dj, instruction.dk)
                return


    def can_read(self, instruction, fu):
        log.debug(str(fu.type) + ' ' + str(fu.rj) + ' ' +str(fu.rk))
        log.debug('Instruction:\t' + str(fu.fi))

        if not fu.busy:
            return False
        else:
            return fu.busy and fu.rj and fu.rk and ((fu.dj == None) or (fu.dj in self.cdb)) and ((fu.dk == None) or (fu.dk in self.cdb))


    def read(self, fu):
        #update FU with read procedure
        self.register_status[fu.fi] = fu
        fu.read(self.memory, self.registers, self.cdb)
        self.execute(fu)

    def can_execute(self, fu):
        #can execute if registers have been read and FU has issued
        return (not fu.rj and not fu.rk) and fu.issued()

    def execute(self, fu):
        #count down clock cycles of FU until finished
        fu.execute()

        if fu.clk == 0:
            #update instructions execution clock
            self.instructions[fu.inst_count].execute = self.clock


    def can_write(self, fu):

        can_write_back = (fu.fi != None and fu.fi != None and fu.fk != None)
        #for f in self.units:                    #Checking all other FU ifor writing errors
        #    can_write_back = (f.fj != fu.fi or not f.rj) and (f.fk != fu.fi or not f.rk)\
        #        and (fu.fi != None and fu.fi != None and fu.fk != None)
        #
        #    if not can_write_back:
        #        break
        return can_write_back

    def write(self, fu):
        value = fu.write(self.units)
        for rob in self.buffer:
            if rob.tag == self.instructions[fu.inst_count].tag:
                rob.wb_complete = True

        if fu.fi not in  self.registers and not fu.is_branch:
            #self.memory[fu.fi] =  self.registers[fu.fk]
            self.cdb[self.instructions[fu.inst_count].tag] =  self.registers[fu.fk]
        elif not fu.is_branch:
            # self.registers[fu.fi] = value
            self.cdb[self.instructions[fu.inst_count].tag] = value

        self.instructions[fu.inst_count].written = self.clock

        #    BRANCH PROCEDURE HERE    #
        #Checking if the Branch flag is set for the FU
        #If so, engange in procedures
        if fu.bf:
            #the difference between PC of the branch and how far back it is branching to
            branch_offest = fu.inst_count - int(fu.fi)
            j = 1
            #reset the PC to immediately after the branch
            self.pc = fu.inst_count + 1


            #Instruction inseretion algorithm
            while self.pc != branch_offest:
                # until the offest reaches the branch
                inst_func = inst_funcs[self.instructions[branch_offest].repr.split()[0]]
                instruction = inst_func(' '.join(self.instructions[branch_offest].repr.split()))
                temp = self.instructions[branch_offest]
                # continuously inserts new instructions
                # into the instruction list
                self.instructions.insert(fu.inst_count + j, instruction)
                branch_offest += 1
                j += 1

            for fu2 in self.units:
                #clearing all FUs that proceded the current one
                #Only occurs if branch is taken
                if fu.inst_count < fu2.inst_count:
                    del self.register_status[fu2.fi]
                    fu2.clear()
            del self.register_status[fu.fj]
            fu.clear()

        elif(fu.repr[0][0] == 'B') and (fu.fi in self_register_status):
            #Format of branch is different
            del self.register_status[fu.fj]
            fu.clear()
        elif fu.fi in self.register_status:
            del self.register_status[fu.fi]
        fu.clear()

    def commit(self):
        log.info('_'*60)
        for rob in self.buffer:
            if rob.tag != None: log.info(rob.printout())
            if not(rob.tag == None):
                for rob2 in self.buffer:
                    if (rob2.tag == rob.dj and rob2.wb_complete) or rob.dj == None:
                        rob.qj = True
                    if (rob2.tag == rob.dk and rob2.wb_complete) or rob.dk == None:
                        rob.qk = True
                if rob.qj and rob.qk:
                    rob.ready = True


        if self.buffer[0].ready and self.buffer[0].wb_complete:
            self.buffer[0].commit(self.memory,  self.registers)

            self.instructions[int(self.buffer[0].tag.split('.').pop())].commit = self.clock

            if self.buffer[0].tag.split('.')[0] != 'SD':
                if self.instructions[int(self.buffer[0].tag.split('.').pop())].fi not in  self.registers and self.instructions[int(self.buffer[0].tag.split('.').pop())].repr[0][0] != 'B':
                    self.memory[self.buffer[0].fi] = self.cdb[self.buffer[0].fk]
                elif self.instructions[int(self.buffer[0].tag.split('.').pop())].repr[0][0] != 'B':
                     self.registers[self.instructions[int(self.buffer[0].tag.split('.').pop())].fi] = self.cdb[self.buffer[0].tag]
            else:
                if self.instructions[int(self.buffer[0].tag.split('.').pop())].fi not in  self.registers and self.instructions[int(self.buffer[0].tag.split('.').pop())].repr[0][0] != 'B':
                    self.memory[self.buffer[0].fi] = self.cdb[self.buffer[0].dk]
                elif self.instructions[int(self.buffer[0].tag.split('.').pop())].repr[0][0] != 'B':
                     self.registers[self.instructions[int(self.buffer[0].tag.split('.').pop())].fi] = self.cdb[self.buffer[0].tag]

            del self.buffer[0]
            self.buffer.append(rebuffer())

        return

    def complete(self):
        #checking if all the instructions have been completed
        #Requires no busy FUs
        done_executing = True
        out_of_insts = not self.has_remaining_insts()
        if out_of_insts:
              for fu in self.units:
                   if fu.busy:
                      done_executing = False
                      break
              for rob in self.buffer:
                  if rob.tag != None:
                      done_executing = False
                      break
        return out_of_insts and done_executing

    def has_remaining_insts(self):
        # If the PC is higher that the number of instructions
        # program is finished scoreboaring
        return self.pc < len(self.instructions)

    def tick(self):
        #function is looped, simulating the 'tick' of a cpu
        for fu in self.units:
            #assumes all functions are not in lock initally
            fu.lock = False

        if self.has_remaining_insts():
            #checking if there are any instructions left before assuming next
            next_instruction = self.instructions[self.pc]
        else:
            #If there are no remaning instrs, set to None
            next_instruction = None

        for fu in self.units:
            #For loop to check and update current state of every functional unit
            if self.can_issue(next_instruction, fu):
                #print 'issued'
                self.issue(next_instruction, fu)
                self.pc += 1
                fu.lock = True
                next_instruction = None
            elif self.can_read(next_instruction, fu):
                #print 'read'
                self.read(fu)
                fu.lock = True
            elif self.can_execute(fu):
                #print 'execute'
                self.execute(fu)
                fu.lock = True
            elif fu.issued():
                #print ' cant do anything'
                    # the functional unit is in use but can't do anything
                fu.lock = True
            #print fu.lock

        self.commit()

        for fu in self.units:
            #Cycling through every functional unit checking if prepared for write
            log.debug('about to check for write, am I in lock? ' + str(fu.lock))
            if not fu.lock and self.can_write(fu):
                #FU must be unlocked and meet flag requirements to not be locked.
                self.write(fu)
                log.debug('writing this')

        self.clock += 1
