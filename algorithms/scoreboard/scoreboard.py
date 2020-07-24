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

from .fu_scoreboard import FunctionalUnit
from .decode_scoreboard import instructions as inst_funcs

FORMAT = '[%(levelname)s][%(funcName)s][%(lineno)d]: %(message)s'
LOG_LEVEL = logging.DEBUG
log = logging.getLogger(__name__)


class Scoreboard:
    def __init__(self):
        self.units = []
        self.instructions = []
        self.memory = hardware.memory
        self.registers = hardware.registers
        self.register_status = {}
        self.pc = 0
        self.clock = 1

    def can_issue(self, instruction, fu):
        #check FU for WAW hazards
        #check FU for avalible functional unit
        #ignore empty instructions
        if instruction == None:
            return False
        else:
            #Checking for matching FU types, Whether matching FU type is busy,
            # and write destination is not busy
            return instruction.op == fu.type and not fu.busy and not \
                (instruction.fi in self.register_status)

    def issue(self, instruction, fu):
        """
        Run issue function in the FU
        update register status to avoid hazards
        update internal instruction issued clock variable
        Reference point for when FU started
        """
        fu.issue(instruction, self.register_status)
        self.register_status[instruction.fi] = fu
        self.instructions[self.pc].issued = self.clock
        fu.inst_count = self.pc

    def can_read(self, fu):
        # check for RAW hazards by reading rj and rk flags
        # print str(fu.type) + ' Busy? ' + str(fu.busy)
        return fu.busy and fu.rj and fu.rk

    def read(self, fu):
        """
        update FU with read procedure
        update instruction when it read
        """
        fu.read(self.memory, self.registers)
        self.instructions[fu.inst_count].read = self.clock

    def can_execute(self, fu):
        #can execute if registers have been read and FU has issued
        return (not fu.rj and not fu.rk) and fu.issued()

    def execute(self, fu):
        #count down clock cycles of FU until finished
        #update instructions execution clock
        fu.execute()
        if fu.clk == 0:
            self.instructions[fu.inst_count].execute = self.clock


    def can_write(self, fu):
        can_write_back = False
        for f in self.units:
            #Checking all other FU ifor writing errors
            can_write_back = (f.fj != fu.fi or not f.rj) and (f.fk != fu.fi or not f.rk)\
                 and (fu.fi != None and fu.fi != None and fu.fk != None)

            if not can_write_back:
                break
        return can_write_back

    def write(self, fu):
        value = fu.write(self.units)

        if fu.fi not in self.registers and not fu.is_branch:
            self.memory[fu.fi] = self.registers[fu.fk]
        elif not fu.is_branch:
            self.registers[fu.fi] = value

        self.instructions[fu.inst_count].written = self.clock

        #    BRANCH PROCEDURE HERE    #
        # Checking if the Branch flag is set for the FU
        # If so, engange in procedures
        if fu.bf:
            # the difference between PC of the branch and how far back it is branching to
            branch_offest = fu.inst_count - int(fu.fi)
            j = 1
            # reset the PC to immediately after the branch
            self.pc = fu.inst_count + 1

            # Instruction inseretion algorithm
            # until the offest reaches the branch
            while self.pc != branch_offest:
                inst_func = inst_funcs[self.instructions[branch_offest].repr.split()[0]]
                instruction = inst_func(' '.join(self.instructions[branch_offest].repr.split()))
                # continuously inserts new instructions
                # into the instruction list
                temp = self.instructions[branch_offest]
                self.instructions.insert(fu.inst_count + j, instruction)
                branch_offest += 1
                j += 1

            for fu2 in self.units:
                # clearing all FUs that proceded the current one
                if fu.inst_count < fu2.inst_count:
                    # Only occurs if branch is taken
                    del self.register_status[fu2.fi]
                    fu2.clear()
            # Cleaning up
            del self.register_status[fu.fj]
            # finally clearing branch's FU
            fu.clear()

        elif(fu.repr[0][0] == 'B'):
            # Format of branch is different
            # meant to clean up but ran out of time
            del self.register_status[fu.fj]
            fu.clear()
        else:
            # clear out the result register status
            del self.register_status[fu.fi]
            # This is for all non-branch instr
            fu.clear()

    def complete(self):
        # checking if all the instructions have been completed
        # Requires no busy FUs
        done_executing = True
        out_of_insts = not self.has_remaining_insts()
        if out_of_insts:
            for fu in self.units:
                if fu.busy:
                    done_executing = False
                    break
        return out_of_insts and done_executing

    def has_remaining_insts(self):
        # If the PC is higher that the number of instructions
        # program is finished scoreboaring
        return self.pc < len(self.instructions)

    def tick(self):
        # function is looped, simulating the 'tick' of a cpu
        # assumes all functions are not in lock initally
        log.debug('Scoreboard tick')
        if logging.getLevelName(log.getEffectiveLevel()) == 'DEBUG':
            time.sleep(0.1)

        for fu in self.units:
            fu.lock = False

        if self.has_remaining_insts():
            # checking if there are any instructions left before assuming next
            next_instruction = self.instructions[self.pc]
        else:
            # If there are no remaning instrs, set to None
            next_instruction = None

        for fu in self.units:
            # For loop to check and update current state of every functional unit
            log.debug('%s == %s', str(fu.repr), str(fu.lock))

            if self.can_issue(next_instruction, fu):
                #print 'issued'
                self.issue(next_instruction, fu)
                self.pc += 1
                fu.lock = True
            elif self.can_read(fu):
                #print 'read'
                self.read(fu)
                fu.lock = True
            elif self.can_execute(fu):
                #print 'execute'
                self.execute(fu)
                fu.lock = True
            elif fu.issued():
                log.debug('Cant do anything')
                    # the functional unit is in use but can't do anything
                fu.lock = True
            #print fu.lock

        for fu in self.units:
            #Cycling through every functional unit checking if prepared for write
            #print 'about to check for write, am I in lock? ' + str(fu.lock)
            if not fu.lock and self.can_write(fu):
                #FU must be unlocked and meet flag requirements to not be locked.
                self.write(fu)

        self.clock += 1
