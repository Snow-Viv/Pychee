from cpu import C8cpu
from screen import C8screen
import pygame
import sys
import logging


# LOG SETTINGS #################################################################


logname         = 'Pychee.log'  # filename to save log to
clear_last_log  = True          # whether or not to delete previous log contents
log_everything  = True          # will log every cycle if True
target_opcode   = 0x8006        # opcode to log
target_mask     = 0xF00F        # ignores nibbles in 0 places

# GENERAL SETTINGS #############################################################

font            = 'font.bin'
rom             = 'ROMs/test_opcode.ch8'
clock           = 60
fps             = 30
scale           = 6

# Logging ######################################################################


def log(cpu):
    if log_everything or cpu.opcode & target_mask == target_opcode:
        logging.debug(
            f"\n\n"
            f"Cycle:           {cpu.cycle}\n"
            f"Opcode:          {format(cpu.opcode, '04X')}\n"
            f"program counter: {format(cpu.pc - 2, '04X')}\n"
            f"Registers:        0   1   2   3   4   5 "
            f"  6   7   8   9   A   B   C   D   E   F\n                 "
            f"{' '.join(format(v, '03d') for v in cpu.V)}\n"
            f"Stack Pointer:   {cpu.sp}\n"
            f"stack:           "
            f"{' '.join(format(s, '03d') for s in cpu.stack)}\n"
            f"I: {cpu.index}\n"
            f"========================================"
            f"========================================"
        )  # I've no idea how else to format this, its probably terrible

# Main Program #################################################################


def main():

    # log setup
    logging.basicConfig(filename=logname, filemode='w', level=logging.DEBUG)

    # Initialize Screen, parameter is scale multiplier
    screen = C8screen(scale)

    # Initialize CPU
    cpu = C8cpu()
    cpu.load_rom(font, 0x0)
    cpu.load_rom(rom)

    clock_update  = pygame.USEREVENT+1
    screen_update = pygame.USEREVENT+2
    pygame.time.set_timer(clock_update, 1000//clock)
    pygame.time.set_timer(screen_update, 1000//fps)

    while True:

        for event in pygame.event.get():
            if event.type == clock_update:
                if cpu.running:
                    cpu.execute_opcode()
                    log(cpu)

            if event.type == screen_update:
                screen.update(cpu.gfx)

            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    main()