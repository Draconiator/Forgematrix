import os
import pickle
from em_constants import (
    SET, CLEAR, WAIT, LOOP, STORE, LOAD, JUMP, JUMPIF, ADD, SETALL, SETNONE,
    SCRATCH_STORE, SCRATCH_LOAD, SCRATCH_ADD, SCRATCH_COPY, SCRATCH_JUMPIF,
    AND, OR, XOR, NOT, SUB, SHL, SHR
)
from em_parser import parse_and_load_program
from em_instructions import step as execute_step
from em_storage import save_scratchpad, load_scratchpad

class Emulator:
    def __init__(self, display, ram_size=64):  # Add ram_size parameter
        self.pc = 0
        self.delay = 0
        self.display = display
        self.running = False
        self.ram_size = ram_size  # Use parameter
        self.ram = bytearray(self.ram_size)
        self.scratchpad_size = 8
        self.scratchpad = bytearray(self.scratchpad_size)
        self.error = None
        self.load_scratchpad()
        self.entry_point = 0
        self.active_delay = 0

    def parse_and_load_program(self, code):
        return parse_and_load_program(self, code)

    def step(self):
        execute_step(self)

    def save_scratchpad(self):
        save_scratchpad(self)

    def load_scratchpad(self):
        load_scratchpad(self)

    def reset(self):
        self.pc = self.entry_point
        self.delay = 0
        self.ram = bytearray(self.ram_size)
        self.display.clear_all()
        self.running = False
        self.error = None
        self.pc_to_line = {}

    # Assign constants from em_constants
    SET = SET
    CLEAR = CLEAR
    WAIT = WAIT
    LOOP = LOOP
    STORE = STORE
    LOAD = LOAD
    JUMP = JUMP
    JUMPIF = JUMPIF
    ADD = ADD
    SETALL = SETALL
    SETNONE = SETNONE
    SCRATCH_STORE = SCRATCH_STORE
    SCRATCH_LOAD = SCRATCH_LOAD
    SCRATCH_ADD = SCRATCH_ADD
    SCRATCH_COPY = SCRATCH_COPY
    SCRATCH_JUMPIF = SCRATCH_JUMPIF
    AND = AND
    OR = OR
    XOR = XOR
    NOT = NOT
    SUB = SUB
    SHL = SHL
    SHR = SHR