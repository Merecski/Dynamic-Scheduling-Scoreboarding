#!/usr/bin/env python3

"""
Main function to invoke the two MIPS Pipline algorithm simulators.
"""

import argparse
import logging

FORMAT = '[%(levelname)s][%(funcName)s][%(lineno)d]: %(message)s'

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--scoreboard', action='store_true', default=False, \
                    help='Run the scoreboard algorithm')
parser.add_argument('-t', '--tomasulo', action='store_true', default=False, \
                    help='Run the tomasulo algorithm')
parser.add_argument('-l', '--log_level', type=str, default='WARNING', choices=['DEBUG', 'INFO', 'WARNING'], \
                    help='Run the scoreboard algorithm')

if __name__ == '__main__':
    args = parser.parse_args()
    
    logging.basicConfig(level=args.log_level, format=FORMAT)
    log = logging.getLogger(__name__)
    log.debug('Debug enabled')

    if args.scoreboard:
        import scoreboard
        filename = 'scoreboard_input.txt'
        alg = scoreboard.Setup(filename)
        alg.split_file()
        alg.run()

        # print('_'*18 + ' SCOREBOARD TABLE ' + '_'*18)
        # print('Instruction\t\tIS\tRD\tEX\tWB')
        # for instruction in scoreboard.instr:
            # print(str(instruction.print_inst()))

        # print('_'*55)
        # print('\nMEMORY')
        # for mem in memory:
            # print(str(mem) + ':\t'+ str(memory[mem]))

        # print('_'*55)
        # print('\nFP REGISTERS')
        # for reg in registers:
            # if 'F' in reg:
                # print(str(reg) + ':\t' + str(registers[reg]))

    if args.tomasulo:
        import tomasulo
        filename = 'tomasulo_input.txt'
        alg = tomasulo.Setup(filename)
        alg.split_file()
        alg.run()

    print('_'*18 + ' TOMASULO TABLE ' + '_'*18)
    print('Instruction\t\tIS\tEX\tWB\tCM')
    for instruction in alg.algorithm.instructions:
        print(str(instruction.print_inst()))

    print( '_'*55 )
    print('\nFP REGISTERS')
    for reg in alg.algorithm.registers:
        if 'F' in reg:
            print (str(reg) + ':\t' + str(alg.algorithm.registers[reg]))

    print( '_'*55 )
    print('\nMEMORY')
    for mem in alg.algorithm.memory:
        print(str(mem) + ':\t'+ str(alg.algorithm.memory[mem]))


