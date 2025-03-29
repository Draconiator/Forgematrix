def parse_and_load_program(emulator, code):
    """Parse program text and load directly into RAM"""
    emulator.error = None
    emulator.reset()
    emulator.pc_to_line = {}
    
    ram_ptr = 0  # Current position in RAM
    
    for line_num, line in enumerate(code, 1):
        line = line.strip().upper()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
            
        parts = line.split()
        cmd = parts[0]
        
        try:
            if cmd == "EP":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                entry_point = int(parts[1])
                if entry_point >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Entry point out of range"
                    return False
                
                # Set the entry point AND adjust the load position
                emulator.entry_point = entry_point
                emulator.entry_point = entry_point
                ram_ptr = entry_point
 
            elif cmd == "SET":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                params_str = ' '.join(parts[1:])
                pairs = []
                for pair in params_str.split(','):
                    pair = pair.strip()
                    if not pair:
                        continue
                    try:
                        x, y = pair.split()
                        pairs.append((int(x), int(y)))  # Fix extra parenthesis here
                    except:
                        emulator.error = f"Error on line {line_num}: Invalid pair '{pair}'"
                        return False
                if not pairs:
                    emulator.error = f"Error on line {line_num}: SET requires pairs"
                    return False
                required_bytes = 1 + 1 + 2 * len(pairs)  # opcode + count + pairs
                if ram_ptr + required_bytes > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.SET
                emulator.ram[ram_ptr + 1] = len(pairs)  # Write count
                ptr = ram_ptr + 2
                for x, y in pairs:
                    emulator.ram[ptr] = x
                    emulator.ram[ptr + 1] = y
                    ptr += 2
                ram_ptr += required_bytes

            elif cmd == "CLEAR":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                params_str = ' '.join(parts[1:])
                pairs = []
                for pair in params_str.split(','):
                    pair = pair.strip()
                    if not pair:
                        continue
                    try:
                        x, y = pair.split()
                        pairs.append((int(x), int(y)))  # Fix here too
                    except:
                        emulator.error = f"Error on line {line_num}: Invalid pair '{pair}'"
                        return False
                if not pairs:
                    emulator.error = f"Error on line {line_num}: CLEAR requires pairs"
                    return False
                required_bytes = 1 + 1 + 2 * len(pairs)  # opcode + count + pairs
                if ram_ptr + required_bytes > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.CLEAR
                emulator.ram[ram_ptr + 1] = len(pairs)  # Write count
                ptr = ram_ptr + 2
                for x, y in pairs:
                    emulator.ram[ptr] = x
                    emulator.ram[ptr + 1] = y
                    ptr += 2
                ram_ptr += required_bytes
                
            elif cmd == "WAIT":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 2 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.WAIT
                emulator.ram[ram_ptr + 1] = int(parts[1])  # cycles
                required_bytes = 2
                ram_ptr += 2
                
            elif cmd == "LOOP":
                emulator.pc = emulator.entry_point
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 1 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.LOOP
                required_bytes = 1
                ram_ptr += required_bytes
                
            elif cmd == "STORE":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                value = int(parts[2])
                
                if addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address {addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.STORE
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = value & 0xFF
                emulator.pc_to_line[current_address] = line_num
                required_bytes = 3
                ram_ptr += required_bytes
                
            elif cmd == "LOAD":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 2 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                
                if addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address {addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.LOAD
                emulator.ram[ram_ptr + 1] = addr
                required_bytes = 2
                ram_ptr += required_bytes
                
            elif cmd == "JUMP":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 2 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                
                if addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address {addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.JUMP
                emulator.ram[ram_ptr + 1] = addr
                required_bytes = 2
                ram_ptr += required_bytes
            
            elif cmd == "ADD":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr1 = int(parts[1])
                addr2 = int(parts[2])
                addr_result = int(parts[3])

                if addr1 >= emulator.ram_size or addr2 >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False

                emulator.ram[ram_ptr] = emulator.ADD
                emulator.ram[ram_ptr + 1] = addr1
                emulator.ram[ram_ptr + 2] = addr2
                emulator.ram[ram_ptr + 3] = addr_result
                required_bytes = 4
                ram_ptr += required_bytes
                
            elif cmd == "JUMPIF":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                ram_addr = int(parts[2])
                
                if addr >= emulator.ram_size or ram_addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.JUMPIF
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = ram_addr
                required_bytes = 3
                ram_ptr += required_bytes
                
            elif cmd == "SETALL":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 1 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.SETALL
                required_bytes = 1
                ram_ptr += required_bytes
                
            elif cmd == "SETNONE":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 1 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                emulator.ram[ram_ptr] = emulator.SETNONE
                required_bytes = 1
                ram_ptr += required_bytes
                
            elif cmd == "SCRATCH_STORE":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                scratch_addr = int(parts[1])
                value = int(parts[2])
                
                if scratch_addr >= emulator.scratchpad_size:
                    emulator.error = f"Error on line {line_num}: Scratchpad address {scratch_addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.SCRATCH_STORE
                emulator.ram[ram_ptr + 1] = scratch_addr
                emulator.ram[ram_ptr + 2] = value & 0xFF
                required_bytes = 3
                ram_ptr += required_bytes
                
            elif cmd == "SCRATCH_LOAD":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                scratch_addr = int(parts[1])
                ram_addr = int(parts[2])
                
                if scratch_addr >= emulator.scratchpad_size:
                    emulator.error = f"Error on line {line_num}: Scratchpad address {scratch_addr} out of range"
                    return False
                if ram_addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: RAM address {ram_addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.SCRATCH_LOAD
                emulator.ram[ram_ptr + 1] = scratch_addr
                emulator.ram[ram_ptr + 2] = ram_addr
                required_bytes = 3
                ram_ptr += required_bytes
                
            elif cmd == "SCRATCH_ADD":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                scratch_addr1 = int(parts[1])
                scratch_addr2 = int(parts[2])
                scratch_result = int(parts[3])
                
                if scratch_addr1 >= emulator.scratchpad_size or scratch_addr2 >= emulator.scratchpad_size or scratch_result >= emulator.scratchpad_size:
                    emulator.error = f"Error on line {line_num}: Scratchpad address out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.SCRATCH_ADD
                emulator.ram[ram_ptr + 1] = scratch_addr1
                emulator.ram[ram_ptr + 2] = scratch_addr2
                emulator.ram[ram_ptr + 3] = scratch_result
                required_bytes = 4
                ram_ptr += required_bytes
                
            elif cmd == "SCRATCH_COPY":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                required_bytes = 3
                if ram_ptr + required_bytes > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                ram_addr = int(parts[1])
                scratch_addr = int(parts[2])
    
                if ram_addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: RAM address {ram_addr} out of range"
                    return False
                if scratch_addr >= emulator.scratchpad_size:
                    emulator.error = f"Error on line {line_num}: Scratchpad address {scratch_addr} out of range"
                    return False
        
                emulator.ram[ram_ptr] = emulator.SCRATCH_COPY
                emulator.ram[ram_ptr + 1] = ram_addr
                emulator.ram[ram_ptr + 2] = scratch_addr
                ram_ptr += required_bytes
                
            elif cmd == "SCRATCH_JUMPIF":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                scratch_addr = int(parts[2])
                
                if addr >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Jump address {addr} out of range"
                    return False
                if scratch_addr >= emulator.scratchpad_size:
                    emulator.error = f"Error on line {line_num}: Scratchpad address {scratch_addr} out of range"
                    return False
                    
                emulator.ram[ram_ptr] = emulator.SCRATCH_JUMPIF
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = scratch_addr
                required_bytes = 3
                ram_ptr += required_bytes

            elif cmd == "AND":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr1 = int(parts[1])
                addr2 = int(parts[2])
                addr_result = int(parts[3])
                if addr1 >= emulator.ram_size or addr2 >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.AND
                emulator.ram[ram_ptr + 1] = addr1
                emulator.ram[ram_ptr + 2] = addr2
                emulator.ram[ram_ptr + 3] = addr_result
                required_bytes = 4
                ram_ptr += required_bytes

            elif cmd == "OR":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr1 = int(parts[1])
                addr2 = int(parts[2])
                addr_result = int(parts[3])
                if addr1 >= emulator.ram_size or addr2 >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.OR
                emulator.ram[ram_ptr + 1] = addr1
                emulator.ram[ram_ptr + 2] = addr2
                emulator.ram[ram_ptr + 3] = addr_result
                required_bytes = 4
                ram_ptr += required_bytes

            elif cmd == "XOR":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr1 = int(parts[1])
                addr2 = int(parts[2])
                addr_result = int(parts[3])
                if addr1 >= emulator.ram_size or addr2 >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.XOR
                emulator.ram[ram_ptr + 1] = addr1
                emulator.ram[ram_ptr + 2] = addr2
                emulator.ram[ram_ptr + 3] = addr_result
                required_bytes = 4
                ram_ptr += required_bytes

            elif cmd == "NOT":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                addr_result = int(parts[2])
                if addr >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.NOT
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = addr_result
                required_bytes = 3
                ram_ptr += required_bytes

            elif cmd == "SUB":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 4 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr1 = int(parts[1])
                addr2 = int(parts[2])
                addr_result = int(parts[3])
                if addr1 >= emulator.ram_size or addr2 >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.SUB
                emulator.ram[ram_ptr + 1] = addr1
                emulator.ram[ram_ptr + 2] = addr2
                emulator.ram[ram_ptr + 3] = addr_result
                required_bytes = 4
                ram_ptr += required_bytes

            elif cmd == "SHL":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                addr_result = int(parts[2])
                if addr >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.SHL
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = addr_result
                required_bytes = 3
                ram_ptr += required_bytes

            elif cmd == "SHR":
                current_address = ram_ptr
                emulator.pc_to_line[current_address] = line_num
                if ram_ptr + 3 > emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Not enough RAM"
                    return False
                addr = int(parts[1])
                addr_result = int(parts[2])
                if addr >= emulator.ram_size or addr_result >= emulator.ram_size:
                    emulator.error = f"Error on line {line_num}: Address out of range"
                    return False
                emulator.ram[ram_ptr] = emulator.SHR
                emulator.ram[ram_ptr + 1] = addr
                emulator.ram[ram_ptr + 2] = addr_result
                required_bytes = 3
                ram_ptr += required_bytes

                
            else:
                emulator.error = f"Error on line {line_num}: Unknown command '{cmd}'"
                return False
                
        except (IndexError, ValueError) as e:
            emulator.error = f"Error on line {line_num}: {e}"
            return False

    emulator.pc = emulator.entry_point        
    return True