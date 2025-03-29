def step(emulator):
    if emulator.delay > 0:
        emulator.delay -= 1
        if emulator.delay == 0:
            emulator.active_delay = 0  # Reset when done
        return
        
    if emulator.pc >= emulator.ram_size:
        emulator.running = False
        emulator.error = "Program counter out of range"
        return
        
    opcode = emulator.ram[emulator.pc]
    
    if opcode == 0:
        emulator.running = False
        return

    elif opcode == emulator.SET:
        current_pc = emulator.pc + 1  # Points to count byte
        if current_pc >= emulator.ram_size:
            emulator.error = "Missing count in SET"
            emulator.running = False
            return
        count = emulator.ram[current_pc]
        current_pc += 1  # Now points to first pair
        error = None
        for _ in range(count):
            if current_pc + 1 >= emulator.ram_size:
                error = "Incomplete pair in SET"
                break
            x = emulator.ram[current_pc]
            y = emulator.ram[current_pc + 1]
            if not (0 <= x < 4 and 0 <= y < 4):
                error = f"Invalid SET coordinates ({x}, {y})"
                break
            emulator.display.update_pixel(x, y, True)
            current_pc += 2
        if error:
            emulator.error = error
            emulator.running = False
        else:
            emulator.pc = current_pc
        
    elif opcode == emulator.CLEAR:
        current_pc = emulator.pc + 1  # Points to count byte
        if current_pc >= emulator.ram_size:
            emulator.error = "Missing count in CLEAR"
            emulator.running = False
            return
        count = emulator.ram[current_pc]
        current_pc += 1  # Now points to first pair
        error = None
        for _ in range(count):
            if current_pc + 1 >= emulator.ram_size:
                error = "Incomplete pair in CLEAR"
                break
            x = emulator.ram[current_pc]
            y = emulator.ram[current_pc + 1]
            if not (0 <= x < 4 and 0 <= y < 4):
                error = f"Invalid CLEAR coordinates ({x}, {y})"
                break
            emulator.display.update_pixel(x, y, False)
            current_pc += 2
        if error:
            emulator.error = error
            emulator.running = False
        else:
            emulator.pc = current_pc
        
    elif opcode == emulator.WAIT:
        if emulator.pc + 1 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        cycles = emulator.ram[emulator.pc + 1]
        emulator.delay = cycles
        emulator.active_delay = cycles
        emulator.pc += 2
        
    elif opcode == emulator.LOOP:
        emulator.pc = emulator.entry_point

    elif opcode == emulator.SETALL:
        for y in range(4):
            for x in range(4):
                emulator.display.update_pixel(x, y, True)
        emulator.pc += 1
        
    elif opcode == emulator.SETNONE:
        for y in range(4):
            for x in range(4):
                emulator.display.update_pixel(x, y, False)
        emulator.pc += 1
        
    elif opcode == emulator.STORE:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        addr = emulator.ram[emulator.pc + 1]
        value = emulator.ram[emulator.pc + 2]
        
        if 0 <= addr < emulator.ram_size:
            emulator.ram[addr] = value
        else:
            emulator.running = False
            emulator.error = f"Invalid RAM address: {addr}"
            return
            
        emulator.pc += 3
        
    elif opcode == emulator.LOAD:
        if emulator.pc + 1 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        addr = emulator.ram[emulator.pc + 1]
        
        if 0 <= addr < emulator.ram_size:
            emulator.display.update_pixel(0, 0, emulator.ram[addr] > 0)
        else:
            emulator.running = False
            emulator.error = f"Invalid RAM address: {addr}"
            return
            
        emulator.pc += 2
        
    elif opcode == emulator.JUMP:
        if emulator.pc + 1 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        addr = emulator.ram[emulator.pc + 1]
        
        if 0 <= addr < emulator.ram_size:
            emulator.pc = addr
        else:
            emulator.running = False
            emulator.error = f"Invalid jump address: {addr}"
            return

    elif opcode == emulator.ADD:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr1 = emulator.ram[emulator.pc + 1]
        addr2 = emulator.ram[emulator.pc + 2]
        addr_result = emulator.ram[emulator.pc + 3]

        if 0 <= addr1 < emulator.ram_size and 0 <= addr2 < emulator.ram_size and 0 <= addr_result < emulator.ram_size:
            emulator.ram[addr_result] = (emulator.ram[addr1] + emulator.ram[addr2]) & 0xFF
        else:
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return

        emulator.pc += 4
            
    elif opcode == emulator.JUMPIF:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        addr = emulator.ram[emulator.pc + 1]
        ram_addr = emulator.ram[emulator.pc + 2]
        
        if not (0 <= addr < emulator.ram_size and 0 <= ram_addr < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid jump address or RAM address"
            return
            
        if emulator.ram[ram_addr] > 0:
            emulator.pc = addr
        else:
            emulator.pc += 3
            
    elif opcode == emulator.SCRATCH_STORE:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        scratch_addr = emulator.ram[emulator.pc + 1]
        value = emulator.ram[emulator.pc + 2]
        
        if 0 <= scratch_addr < emulator.scratchpad_size:
            emulator.scratchpad[scratch_addr] = value
            emulator.save_scratchpad()
        else:
            emulator.running = False
            emulator.error = f"Invalid scratchpad address: {scratch_addr}"
            return
            
        emulator.pc += 3
        
    elif opcode == emulator.SCRATCH_LOAD:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        scratch_addr = emulator.ram[emulator.pc + 1]
        ram_addr = emulator.ram[emulator.pc + 2]
        
        if not (0 <= scratch_addr < emulator.scratchpad_size and 0 <= ram_addr < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid scratchpad or RAM address"
            return
            
        emulator.ram[ram_addr] = emulator.scratchpad[scratch_addr]
        
        emulator.pc += 3
        
    elif opcode == emulator.SCRATCH_ADD:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        scratch_addr1 = emulator.ram[emulator.pc + 1]
        scratch_addr2 = emulator.ram[emulator.pc + 2]
        scratch_result = emulator.ram[emulator.pc + 3]
        
        valid_addresses = (0 <= scratch_addr1 < emulator.scratchpad_size and 
                         0 <= scratch_addr2 < emulator.scratchpad_size and 
                         0 <= scratch_result < emulator.scratchpad_size)
        
        if not valid_addresses:
            emulator.running = False
            emulator.error = "Invalid scratchpad address"
            return
            
        emulator.scratchpad[scratch_result] = (emulator.scratchpad[scratch_addr1] + emulator.scratchpad[scratch_addr2]) & 0xFF
        emulator.save_scratchpad()
        
        emulator.pc += 4
        
    elif opcode == emulator.SCRATCH_COPY:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        ram_addr = emulator.ram[emulator.pc + 1]
        scratch_addr = emulator.ram[emulator.pc + 2]
        
        if not (0 <= ram_addr < emulator.ram_size and 0 <= scratch_addr < emulator.scratchpad_size):
            emulator.running = False
            emulator.error = "Invalid RAM or scratchpad address"
            return
            
        emulator.scratchpad[scratch_addr] = emulator.ram[ram_addr]
        emulator.save_scratchpad()
        
        emulator.pc += 3
        
    elif opcode == emulator.SCRATCH_JUMPIF:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
            
        addr = emulator.ram[emulator.pc + 1]
        scratch_addr = emulator.ram[emulator.pc + 2]
        
        if not (0 <= addr < emulator.ram_size and 0 <= scratch_addr < emulator.scratchpad_size):
            emulator.running = False
            emulator.error = "Invalid jump address or scratchpad address"
            return
            
        if emulator.scratchpad[scratch_addr] > 0:
            emulator.pc = addr
        else:
            emulator.pc += 3

    elif opcode == emulator.AND:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr1 = emulator.ram[emulator.pc + 1]
        addr2 = emulator.ram[emulator.pc + 2]
        addr_result = emulator.ram[emulator.pc + 3]
        if not (0 <= addr1 < emulator.ram_size and 0 <= addr2 < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr1] & emulator.ram[addr2]) & 0xFF
        emulator.pc += 4

    elif opcode == emulator.OR:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr1 = emulator.ram[emulator.pc + 1]
        addr2 = emulator.ram[emulator.pc + 2]
        addr_result = emulator.ram[emulator.pc + 3]
        if not (0 <= addr1 < emulator.ram_size and 0 <= addr2 < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr1] | emulator.ram[addr2]) & 0xFF
        emulator.pc += 4

    elif opcode == emulator.XOR:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr1 = emulator.ram[emulator.pc + 1]
        addr2 = emulator.ram[emulator.pc + 2]
        addr_result = emulator.ram[emulator.pc + 3]
        if not (0 <= addr1 < emulator.ram_size and 0 <= addr2 < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr1] ^ emulator.ram[addr2]) & 0xFF
        emulator.pc += 4

    elif opcode == emulator.NOT:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr = emulator.ram[emulator.pc + 1]
        addr_result = emulator.ram[emulator.pc + 2]
        if not (0 <= addr < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (~emulator.ram[addr]) & 0xFF
        emulator.pc += 3

    elif opcode == emulator.SUB:
        if emulator.pc + 3 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr1 = emulator.ram[emulator.pc + 1]
        addr2 = emulator.ram[emulator.pc + 2]
        addr_result = emulator.ram[emulator.pc + 3]
        if not (0 <= addr1 < emulator.ram_size and 0 <= addr2 < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr1] - emulator.ram[addr2]) & 0xFF
        emulator.pc += 4

    elif opcode == emulator.SHL:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr = emulator.ram[emulator.pc + 1]
        addr_result = emulator.ram[emulator.pc + 2]
        if not (0 <= addr < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr] << 1) & 0xFF
        emulator.pc += 3

    elif opcode == emulator.SHR:
        if emulator.pc + 2 >= emulator.ram_size:
            emulator.running = False
            emulator.error = "Instruction arguments out of range"
            return
        addr = emulator.ram[emulator.pc + 1]
        addr_result = emulator.ram[emulator.pc + 2]
        if not (0 <= addr < emulator.ram_size and 0 <= addr_result < emulator.ram_size):
            emulator.running = False
            emulator.error = "Invalid RAM address"
            return
        emulator.ram[addr_result] = (emulator.ram[addr] >> 1) & 0xFF
        emulator.pc += 3
            
    else:
        emulator.running = False
        emulator.error = f"Unknown opcode: {opcode}"