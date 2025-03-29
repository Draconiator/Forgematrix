import unittest
from em_core import Emulator
from em_parser import parse_and_load_program

class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.em = Emulator(None, ram_size=64)
    
    def test_memory_ops(self):
        code = [
            "STORE 10 255",
            "LOAD 10",
            "ADD 10 10 11"
        ]
        parse_and_load_program(self.em, code)
        self.em.step()  # STORE
        self.assertEqual(self.em.ram[10], 255)
        
        self.em.step()  # LOAD
        self.assertEqual(self.em.ram[0], 255)  # Verify display update
        
        self.em.step()  # ADD
        self.assertEqual(self.em.ram[11], (255 + 255) & 0xFF)

    def test_bitwise_ops(self):
        code = [
            "STORE 20 0b1010",
            "STORE 21 0b1100",
            "XOR 20 21 22"
        ]
        parse_and_load_program(self.em, code)
        while self.em.running:
            self.em.step()
        self.assertEqual(self.em.ram[22], 0b0110)

    def test_scratchpad(self):
        code = [
            "SCRATCH_STORE 2 100",
            "SCRATCH_COPY 10 2"
        ]
        parse_and_load_program(self.em, code)
        self.em.ram[10] = 50
        self.em.step()
        self.assertEqual(self.em.scratchpad[2], 100)
        self.em.step()
        self.assertEqual(self.em.scratchpad[2], 50)

if __name__ == '__main__':
    unittest.main()