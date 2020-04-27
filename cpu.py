"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Create memory
        self.ram =  [0] * 256 # length and the index will stop at 255

        # Created Registers
        self.reg = [0] * 8  # returns 8 zeros and stores values (0-7)

        self.pc = 0 # Program counter, the index (address) of the current instruction

        self.SP = 7 # R7 is reserved
        self.reg[self.SP] = 0xF4
        self.running = True

        self.flag = 0

        # Instructions
        self.LDI = 0b10000010
        # self.MUL = 0b10100010
        self.PRN = 0b01000111
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.HLT = 0b00000001
        self.CALL = 0b1010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        

        # Turning the branch table into a dictionary to be able to update easier
        self.branchtable = {
            self.LDI: self.ldi,
            # self.MUL: self.multiply,
            self.PRN: self.prn,
            self.PUSH: self.push,
            self.POP: self.pop,
            self.HLT: self.halt,
            self.CALL: self.call,
            self.RET: self.ret,
            self.JMP: self.jump,
            self.JEQ: self.jump_equals,
            self.JNE: self.jump_not_equals
        }
        

    def load(self, program_filename):
        """Load a program into memory."""

        address = 0

        with open(program_filename) as f:  # opens file
            for line in f: # reads file line by line
                line = line.split('#') # turns the line into int instead of string
                line = line[0].strip() #list
                if line == '':
                    continue
                self.ram[address] = int(line, base=2) #turns the line into <int> instead of string store the address in memory

                address +=1 #add one and goes to the next

    # MAR contains the address that is being read or written to. 
    # ram_read() should accept the address (MAR) to read and return the value stored #there.
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDR contains the data that was read or the data to write. 
    # ram_write() should accept a value(MDR) to write, and the address (MAR) to write it to.
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    # Branch Table for the instruction object
    def ldi(self, operand_a=None, operand_b=None):        
        register_num = operand_a #self.ram_read(self.pc + 1) # operand_a (address)
        value = operand_b #self.ram_read(self.pc + 2) # operand_b (value)
        self.reg[register_num] = value # adds the value to the register
       
        self.pc += 3

    # def compare(self, operand_a=None, operand_b=None):
    #     num_reg_a = self.ram_read(self.pc + 1)
    #     num_reg_b = self.ram_read(self.pc + 2)
    #     self.alu(0b10100111, num_reg_a, num_reg_b)
    #     self.pc += 3

    def prn(self, operand_a=None, operand_b=None):
        register_num = operand_a #self.ram_read(self.pc + 1) # operand_a (address)
        value = self.reg[register_num]
        print(value)
        self.pc += 2
    
    def push(self, operand_a=None, operand_b=None):
        # decrement the stack pointer (initializes @ F4, will then go to F3)
        self.reg[self.SP] -= 1

        #copy value from register into memory
        register_num = operand_a #self.ram[self.pc + 1]
        value = self.reg[register_num] # this is what i want to push

        stack_postion = self.reg[self.SP] # index into memory
        self.ram[stack_postion] = value # stores the value on the stack
        
        # then increments the PC/program counter
        self.pc += 2
    
    def pop(self, operand_a=None, operand_b=None):
        # current stack pointer position
        stack_postion = self.reg[self.SP]

        # get current value from memory(RAM) from stack pointer
        value = self.ram[stack_postion]

        # add the value to the register
        register_num = operand_a #self.ram[self.pc + 1]
        self.reg[register_num] = value
        # Increment the stack pointer position
        self.reg[self.SP] += 1
        
        # increment the Program Counter
        self.pc += 2
    
    def call(self, operand_a=None, operand_b=None):
        # Get the address after the call so know where to return
        return_address = self.pc + 2

        #push on the stack using stack pointer
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = return_address

        # Set the PC to the value in the given register
        register_num = self.ram[self.pc + 1]
        destination_address = self.reg[register_num]

        # Sets the progam counter to the destination address
        self.pc = destination_address

    def ret(self, operand_a=None, operand_b=None):
        # pop return address from top of the stack
        return_address = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

        #set the pc so it knows where to return to
        self.pc = return_address
    
    # Jump to the address stored in the given register.
    # Set the PC to the address stored in the given register.
    def jump(self, operand_a=None, operand_b=None):
        self.pc = self.reg[operand_a]
    
    # If equal flag is set (true), jump to the address stored in the given register.
    def jump_equals(self, operand_a=None, operand_b=None):
        # Jump to the address stored in the given register.
        # Set the PC to the address stored in the given register.
        if self.flag & 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    # If E flag is clear (false, 0), jump to the address stored in the given register
    def jump_not_equals(self, operand_a=None, operand_b=None):
        if self.flag != 0b00000001:
            self.pc = self.reg[operand_a]
        else:   
            self.pc += 2

    def halt(self, operand_a=None, operand_b=None):
        self.running = False
    


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 0b10100000: #ADD
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010: #Subtract
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 0b10100001: #Divide
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 0b10100011: #Multiply
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 0b10100111: #Compare
            # if reg a is less than reg b <
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            # if reg a is greater than reg b >
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            # if reg a is equal than reg b ==
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001 
            #set flag back to zero
            else:
                self.flag = 0b00000000 
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self, LABEL=str()):
        
        print(f"{LABEL} TRACE --> PC: %02i | RAM: %03i %03i %03i | Register: " % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02i" % self.reg[i], end='')

        print(" | Stack:", end='')
        
        for i in range(240, 244):
            print(" %02i" % self.ram_read(i), end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            
            # Stores the result in "Instruction Register" from the memory (RAM) address from the program
            IR = self.ram[self.pc]
            
            register_a = self.ram_read(self.pc + 1)
            register_b = self.ram_read(self.pc + 2)

            # Checks the alu to see if 1 or 0, bit shifts left 6 places 
            use_alu = (IR & 0b00100000) >> 5
            # If the alu is used 
            if use_alu:
                # in the alu the instruction register
                # then move to the specified function to be run
                self.alu(IR, register_a, register_b)
                #increment the program counter after
                self.pc += 3
                self.trace()
            # as the branchtable moves down the branchtable object, it will "get" the instruction key,
            # then move to the specified function to be run
            elif self.branchtable.get(IR):
                self.trace()
                self.branchtable[IR](register_a, register_b)
            else:
                print('Unknown instruction' )
                self.trace("End")
                self.running = False