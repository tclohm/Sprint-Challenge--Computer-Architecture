"""CPU functionality."""

import sys

# halted instruction
HLT = 0b00000001 # 1 bytes
# Set the value of a register to an integer. Load Immediately
LDI = 0b10000010 # 130 bytes
# Print numeric value stored in the given register.
PRN = 0b01000111 # 71 bytes
# Multiply the values in two registers together and store the result in registerA.
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
# Stack Pointer
SP = 7
CALL = 0b01010000
RET = 0b00010001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.register[SP] = 0xF4
        self.halted = False
        # self.sp = 7
        # dictionary of functions that can be indexed by opcode value
        # fetch the instruction in RAM, use that value to look up the handler function in tha branch table
        # then call it
        self.dispatch_table = {}
        self.dispatch_table[HLT] = self.hlt
        self.dispatch_table[LDI] = self.ldi
        self.dispatch_table[PRN] = self.prn
        self.dispatch_table[ADD] = self.add
        self.dispatch_table[MUL] = self.mul
        self.dispatch_table[PUSH] = self.push
        self.dispatch_table[POP] = self.pop
        self.dispatch_table[CALL] = self.call
        self.dispatch_table[RET] = self.ret
        


    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            # 0b10000010, # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b01000111, # PRN R0
            # 0b00000000,
            # 0b00000001, # HLT
        ]

        try:
            with open(f"examples/{file}", "r") as file:
                for line in file:
                    comment = line.split("#")
                    str_content = comment[0].strip()

                    if str_content == "":
                        continue
                    # Convert binary string to integer
                    byte = int(str_content, 2)

                    program.append(byte)
        except FileNotFoundError:
            print("\033[1m" + f"{sys.argv[0]} {file} " + "\033[0m:" + " Not Found. Please make sure you are spelling it correctly.")
            exit(1)

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        # Memory Address Register, holds the memory address we're reading or writing
        if 0 <= MAR <= 255:
            return self.ram[MAR]
        else:
            return f"{MAR} invalid address"


    def ram_write(self, MAR, MDR):
        # Memory Data Register, holds the value to write or the value just read
        if 0 <= MAR <= 255:
            self.ram[MAR] = MDR
        else:
            return f"{MAR} invalid address"

    def hlt(self, *args):
        self.halted = True
        print("🧮 Program Halted")

    def ldi(self, reg_a=None, reg_b=None):
        self.register[reg_a] = reg_b

    def prn(self, reg_a=None, reg_b=None):
        print(self.register[reg_a])

    def add(self, reg_a=None, reg_b=None):
        self.alu("ADD", reg_a, reg_b)

    def mul(self, reg_a=None, reg_b=None):
        self.alu("MUL", reg_a, reg_b)

    def push(self, reg_a=None, reg_b=None):
        self.register[SP] -= 1
        value = self.register[reg_a]
        self.ram_write(self.register[SP], value)
        

    def pop(self, reg_a=None, reg_b=None):
        if self.register[SP] == 0xF4:
            return "Stack is empty"
        value = self.ram_read(self.register[SP])
        self.register[reg_a] = value
        self.register[SP] += 1

    def ret(self):
        return_address = self.register[SP]
        self.pc = self.ram_read(return_address)
        self.register[SP] += 1

    def call(self, reg_a):
        # Call a subroutine at address stored in register
        # push address of instruction after call onto stack
        # decrement the stack pointer
        self.register[SP] -= 1
        self.ram_write(self.register[SP], self.pc + 2)
        self.pc = self.register[reg_a]

    
        

    def run(self):
        """Run the CPU."""

        while not self.halted:
            # Instruction Register, contains a copy of the currently executing instruction
            IR = self.ram_read(self.pc)

            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)

            if IR == RET:
                self.dispatch_table[IR]()
            elif IR == CALL:
                self.dispatch_table[IR](reg_a)
            elif IR in self.dispatch_table:
                self.dispatch_table[IR](reg_a, reg_b)
                # shift the instruction register right shift by 6, add 1
                self.pc += (IR >> 6) + 1
            else:
                print(f"Cannot read instruction, \033[1m{IR}\033[0m, at address \033[1m{self.pc}\033[0m")
                self.halted = True
