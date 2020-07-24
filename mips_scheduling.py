#!/usr/bin/env python3

"""Main function to invoke the two MIPS Pipline algorithm simulators.
"""

import argparse
import logging

import algorithms

FORMAT = '[%(levelname)s][%(funcName)s][%(lineno)d]: %(message)s'
logging.basicConfig(level=args.log_level, format=FORMAT)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--scoreboard', action='store_true', default=False,
                    help='Run the scoreboard algorithm')
parser.add_argument('-t', '--tomasulo', action='store_true', default=False,
                    help='Run the tomasulo algorithm')
parser.add_argument('-f', '--filename', type=str,
                    help='Run the tomasulo algorithm')
parser.add_argument('-l', '--log_level', type=str, default='WARNING', choices=['DEBUG', 'INFO', 'WARNING'],
                    help='Run the scoreboard algorithm')

def main():
    args = parser.parse_args()

    log = logging.getLogger(__name__)

    if args.scoreboard:
        if args.filename:
            filename = args.filename
        else:
            filename = 'scoreboard_input.txt'

        architecure = algorithms.Setup(filename)
        architecure.setup_scoreboard()
        architecure.run()

        print('_'*18 + ' SCOREBOARD TABLE ' + '_'*18)
        print('Instruction\t\tIS\tRD\tEX\tWB')
        for instruction in scoreboard.instr:
            print(str(instruction.print_inst()))

    elif args.tomasulo:
        if args.filename:
            filename = args.filename
        else:
            filename = 'tomasulo_input.txt'

        architecure = algorithms.Setup(filename)
        architecure.setup_tomasulo()
        architecure.run()

        print('_'*18 + ' TOMASULO TABLE ' + '_'*18)
        print('Instruction\t\tIS\tEX\tWB\tCM')
        for instruction in architecure.algorithm.instructions:
            print(str(instruction.print_inst()))

    else:
        log.critical('No algorithim provided.\n')
        parser.print_help()
        exit()

    print( '_'*55 )
    print('\nFP REGISTERS')
    for reg in architecure.algorithm.registers:
        if 'F' in reg:
            print (str(reg) + ':\t' + str(architecure.algorithm.registers[reg]))

    print( '_'*55 )
    print('\nMEMORY')
    for mem in architecure.algorithm.memory:
        print(str(mem) + ':\t'+ str(architecure.algorithm.memory[mem]))

if __name__ == '__main__':
    main()

