"""
Basic class to ease the creattion of MIPS algorithms
"""


import algorithms.scoreboard
dir(algorithms.scoreboard)

class Setup:
    """Software defined MIPS instruction properties
    
    Args:
        text_file (str): Location of input file
        instr (list): Every instruction in input file
        functional_unit (Reference to class): Fucntional unit class
        instruction_functions (Reference to dictionary): Instruction functions
        reorder_buffer (Reference to class): Reorder Buffer class
    """
    def __init__(self, txt_file):
        self.text_file = txt_file
        self.instr = []
        self.functional_unit = None
        self.instruction_functions = None
        self.reorder_buffer = None

    def setup_scoreboard(self):
        from .scoreboard import scoreboard
        
        self.algorithm = scoreboard.Scoreboard()
        self.functional_unit = scoreboard.FunctionalUnit
        self.instruction_functions = scoreboard.inst_funcs
        self.split_file()
        for instruction in self.instr:
            #split up every line in file to FU or Instruction
            self.split_scoreboard_line(instruction)

    def setup_tomasulo(self):
        from .tomasulo import tomasulo
        
        self.algorithm = tomasulo.Tomasulo()
        self.functional_unit = tomasulo.FunctionalUnit
        self.instruction_functions = tomasulo.inst_funcs
        self.reorder_buffer = tomasulo.rebuffer
        self.split_file()
        for instruction in self.instr:
            #split up every line in file to FU or Instruction
            self.split_tomasulo_line(instruction)
   
    def split_scoreboard_line(self, line):
        #determines if the current line is a command for a functional unit or instruction
        if line[0] == '.':
            self.split_fu(line)
        else:
            self.split_inst(line)
            
    def split_tomasulo_line(self, line):
        #determines if the current line is a command for a functional unit or instruction
        if line[0] == '#':
            return
        elif line[0] == '.':
            self.split_fu(line)
        elif line[0] == '$':
            self.split_rob(line)
        else:
            self.split_inst(line)

    def split_inst(self, line):
        #Splits instruction and append into instruction objects
        line = line.split()

        #Striping out op code to properly setup instruction
        line[0] = line[0].lstrip('.')
        key = line[0]
        inst_func = self.instruction_functions[key]
        instruction = inst_func(' '.join(line))

        #Creating a List of object type Instruction with it's own personal variables
        self.algorithm.instructions.append(instruction)

    def split_fu(self, line):
        #splits functional unit and append objects on a variable loop
        line = line.strip('.').split()
        f_unit = line[0]
        clock = line[2]
        for i in range(0,int(line[1])):
            #list of object type Functional Units with own variables
            #appending FU for specified number
            self.algorithm.units.append(self.functional_unit(f_unit, int(clock)))

    def split_rob(self, line):
        line = line.strip('$')
        for i in range(0,int(line)):
            self.algorithm.buffer.append(self.reorder_buffer())

    def split_file(self):
        #reading lines out from file then sending lines off for further spliting
        try:
            with open(self.text_file,"r") as input:
                self.instr = [line.strip() for line in input]
        except FileNotFoundError:
            from os import getcwd
            log.error(f'File"{self.text_file}" was not found in "{getcwd()}"')
            log.error('Exiting...')
            exit()

    def run(self):
        while not self.algorithm.complete():
            self.algorithm.tick()

