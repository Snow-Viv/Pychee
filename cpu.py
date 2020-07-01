import random


class C8cpu:

    def __init__(self):
        self.opcode = 0x0000
        self.memory = [0] * 0xFFF
        self.V      = [0] * 16

        self.index      = 0
        self.pc     = 0x200

        self.stack  = [0] * 16
        self.sp     = 0

        self.gfx    = [[0] * 64 for _ in range(32)]

        self.running = True     # Used to terminate operation when infinite loop occurs
        self.cycle = 0

    # Definitions for all the opcodes
    def execute_opcode(self):
        """
        read current address, increment program counter,
        then perform opcode instructions
        """

        opcode_lookup = {
            0x0: self.clear_return,
            0x1: self.jump,
            0x2: self.subroutine,
            0x3: self.skip_if_equal,
            0x4: self.skip_if_not_equal,
            0x5: self.skip_if_register_equal,
            0x6: self.mov_val_to_reg,
            0x7: self.add_val_to_reg,
            0x8: self.execute_eights_opcode,
            0x9: self.skip_if_register_not_equal,
            0xA: self.set_i,
            0xB: self.jump_plus,
            0xC: self.random_number_gen,
            0xD: self.draw,
            0xE: self.not_handled,
            0xF: self.execute_f_opcode
        }

        self.opcode = (self.memory[self.pc] << 8) + self.memory[self.pc+1]
        self.pc += 2
        first_nibble = (self.opcode & 0xF000) >> 12
        opcode_lookup.get(first_nibble)()
        self.cycle += 1

    def not_handled(self):
        print(f"opcode 0x{format(self.opcode, '01X')} not handled yet")

    def unknown_opcode(self):
        print(f"opcode {format(self.opcode, '01X')} is not a legal opcode")

    def clear_return(self):                             # 0x00E0 & 0x00EE
        """
        0x00E0
        clears the screen

        0x00EE
        jumps to address read from top of the stack
        """
        if self.opcode == 0x00E0:
            self.gfx = [[0] * 64 for _ in range(32)]

        elif self.opcode == 0x00EE:
            self.sp -= 1
            self.pc = self.stack[self.sp]

    def jump(self):                                     # 0x1NNN
        """
        0x1NNN
        jumps to the instruction at address NNN
        """

        if self.pc - 2 == self.opcode & 0x0FFF:
            self.running = False
        self.pc = self.opcode & 0x0FFF

    def subroutine(self):                               # 0x2NNN
        """
        0x2NNN
        jumps to a subroutine at address NNN,
        adds current address to the stack
        """
        self.stack[self.sp] = self.pc
        self.sp += 1
        self.pc = self.opcode & 0x0FFF

    def skip_if_equal(self):                            # 0x3XNN
        """
        0x3XNN
        skips the next instruction if vX is equal to NN
        """
        register = self.V[(self.opcode & 0x0F00) >> 8]
        value = self.opcode & 0x00FF
        if register == value:
            self.pc += 2

    def skip_if_not_equal(self):                        # 0x4XNN
        """
        0x4XNN
        skips the next instruction if vX is not equal to NN
        """
        register = self.V[(self.opcode & 0x0F00) >> 8]
        value = self.opcode & 0x00FF
        if register != value:
            self.pc += 2

    def skip_if_register_equal(self):                   # 0x5XY0
        """
        0x5XY0
        skips the next instruction if vX is equal to vY
        """
        x = self.V[(self.opcode & 0x0F00) >> 8]
        y = self.V[(self.opcode & 0x00F0) >> 4]

        if x == y:
            self.pc += 2

    def mov_val_to_reg(self):                           # 0x6XNN
        """
        0x6XNN
        moves the value NN into vX
        """
        register = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.V[register] = value

    def add_val_to_reg(self):                           # 0x7XNN
        """
        0x7XNN
        adds the value NN to vX
        """
        register = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.V[register] += value
        self.V[register] %= 256

    def execute_eights_opcode(self):                    # 0x8xxx
        """
        0x8xxx
        """
        eights_lookup = {
            0x0: self.copy_reg_to_reg,
            0x1: self.bitwise_or,
            0x2: self.bitwise_and,
            0x3: self.bitwise_xor,
            0x4: self.add_reg_to_reg,
            0x5: self.sub_y_from_x,
            0x6: self.shift_right,
            0x7: self.sub_x_from_y,
            0xE: self.shift_left
        }
        last_nibble = self.opcode & 0x000F
        eights_lookup.get(last_nibble, self.unknown_opcode)()

    def copy_reg_to_reg(self):                          # 0x8XY0
        """
        0x8XY0
        copies value of vY into vX
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.V[x] = self.V[y]

    def bitwise_or(self):                               # 0x8XY1
        """
        0x8XY1
        performs a bitwise OR with vX and vY, then stores result in vX
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.V[x] |= self.V[y]

    def bitwise_and(self):                              # 0x8XY2
        """
        0x8XY2
        performs a bitwise AND with vX and vY, then stores result in vX
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.V[x] &= self.V[y]

    def bitwise_xor(self):                              # 0x8XY3
        """
        0x8XY3
        performs a bitwise XOR with vX and vY, then stores result in vX
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.V[x] ^= self.V[y]

    def add_reg_to_reg(self):  # 0x8XY4
        """
        8XY4
        Adds registers vX and vY, then stores result in vX.
        Will also set vF to 1 if the result overflows
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        result = self.V[x] + self.V[y]

        self.V[0xF] = 1 if result > 256 else 0
        self.V[x] = result % 256

    def sub_y_from_x(self):                             # 0x8XY5
        """
        8XY5
        Subtracts vY from vX, then stores result in vX.
        Will also set vF to 0 if the result underflows
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        result = self.V[x] - self.V[y]

        self.V[0xF] = 1 if result > 0 else 0
        self.V[x]   = result % 256

    def shift_right(self):                             # 0x8XY6
        """
        0x8XY6
        Stores LSB of vX in vF, then shifts vX once right
        """
        x = (self.opcode & 0x0F00) >> 8

        self.V[0xF] = self.V[x] & 1
        self.V[x] = self.V[x] >> 1

    def sub_x_from_y(self):                             # 0x8XY7
        """
        8XY7
        Subtracts vX from vY, then stores result in vX.
        Will also set vF to 0 if the result underflows
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        result = self.V[y] - self.V[x]

        self.V[0xF] = 1 if result > 0 else 0
        self.V[x]   = result % 256

    def shift_left(self):                             # 0x8XYE
        """
        0x8XYE
        Stores MSB of vX in vF, then bitshifts vX once left
        """
        x = (self.opcode & 0x0F00) >> 8

        self.V[0xF] = (self.V[x] & 0b10000000) >> 7
        self.V[x] = self.V[x] << 1

    def skip_if_register_not_equal(self):               # 0x9XY0
        """
        0x9XY0
        skips the next instruction if vX is not equal to vY
        """
        x = self.V[(self.opcode & 0x0F00) >> 8]
        y = self.V[(self.opcode & 0x00F0) >> 4]

        if x != y:
            self.pc += 2

    def set_i(self):                                    # 0xANNN
        """
        0xANNN
        sets register I to NNN
        """
        self.index = self.opcode & 0x0FFF

    def jump_plus(self):                                # 0xBNNN
        """
        0xBNNN
        sets the program counter to v0 + NNN
        """
        self.pc = self.V[0] + (self.opcode & 0x0FFF)

    def random_number_gen(self):                        # 0xCXNN
        """
        0xCXNN
        Generates a random number, then ands it with NN.
        Stores result in vX
        """
        register = (self.opcode & 0x0F00) >> 8
        mask = self.opcode & 0x00FF
        self.V[register] = random.randint(0, 255) & mask

    def draw(self):                                     # 0xDXYN
        """
        0xDXYN
        Draws a sprite with a height of N pixels at coordinate (vX), (vY).
        Sprite is 8 pixels wide and located at address I,
        each byte representing a row of pixels.
        Sets VF to 1 if any pixels are flipped,
        or to 0 if all pixels are not flipped.

        """
        reg_x = (self.opcode & 0x0F00) >> 8
        reg_y = (self.opcode & 0x00F0) >> 4
        x_offset = self.V[reg_x]
        y_offset = self.V[reg_y]
        height = self.opcode & 0x000F
        flag = 0

        for h in range(height):
            y = (h + y_offset) % 32
            sprite = self.memory[self.index + h]

            for w in range(8):
                x = (w + x_offset) % 64
                pixel = (sprite & 0b10000000) >> 7
                sprite <<= 1

                if pixel == 1:
                    if self.gfx[y][x] == 1:
                        flag = 1
                    self.gfx[y][x] = 1
                else:
                    self.gfx[y][x] = 0

                if flag == 1:
                    self.V[0xF] = 1
                elif flag == 0:
                    self.V[0xF] = 0

    def execute_f_opcode(self):                    # 0xFxxx
        """
        0xFxxx
        """
        f_lookup = {
            0x07: self.not_handled,
            0x0A: self.not_handled,
            0x15: self.not_handled,
            0x18: self.not_handled,
            0x1E: self.add_reg_to_i,
            0x29: self.set_font,
            0x33: self.not_handled,
            0x55: self.not_handled,
            0x65: self.not_handled
        }
        last_byte = self.opcode & 0x00FF
        f_lookup.get(last_byte, self.unknown_opcode)()

    def add_reg_to_i(self):                         # 0xFX1E
        """
        0xFX1E
        Adds vX to I, VF is not affected
        """
        register = (self.opcode & 0x0F00) >> 8
        self.index = (self.V[register] + self.index) % 0xFF

    def set_font(self):                             # 0xFX29
        """
        0xFX29
        Sets I to the location of the sprite for the character X.
        Located in the first 0x50 bytes of memory
        """
        character = (self.opcode & 0x0F00) >> 8
        self.index = character * 5

    # Opcode Definitions end here

    def load_rom(self, filename, offset=0x200):
        with open(filename, 'rb') as f:
            for i, b in enumerate(f.read()):
                self.memory[i + offset] = b

    def printmem(self, width=16):
        """
        Prints out the current state of the memory in a neatly formatted table
        """
        for i, b in enumerate(self.memory):
            if i % width == 0:
                print("0x"+format(i,"X").rjust(4,"0"), end=" | ")
            print(format(b, '02x'), end=" ")
            if i % width == width - 1:
                print("")


if __name__ == '__main__':
    print("This file does nothing on it's own, try Pychee.py instead")