```markdown
# Forgematrix Emulator

A retro-inspired emulator for a custom 2-bit processor architecture with 4x4 LED display, perfect for minimalist programming challenges and educational purposes.

![Emulator Screenshot](https://via.placeholder.com/800x500.png?text=Forgematrix+Emulator+UI) *UI preview (placeholder)*

## Features

- 🖥️ 4x4 pixel display with coordinate system
- 💾 Configurable RAM (32-256 bytes)
- 📦 8-byte persistent scratchpad memory
- ⚡ 120Hz emulation speed
- 📝 Integrated code editor with syntax highlighting
- 🔧 Full instruction set including:
  - Display control (SET/CLEAR/SETALL/SETNONE)
  - Memory operations (STORE/LOAD/ADD/SUB)
  - Bitwise operations (AND/OR/XOR/NOT/SHL/SHR)
  - Flow control (JUMP/JUMPIF/LOOP)
  - Scratchpad operations
  - Timing control (WAIT)
- 📊 Real-time memory visualization
- ⏯️ Step-through debugging

## Installation

1. Clone repository:

git clone https://github.com/yourusername/forgematrix-emulator.git
cd forgematrix-emulator


2. Install dependencies:

pip install PyQt5


3. Run emulator:

python main.py


## Basic Usage

1. Write program in the editor:

EP 0       ; Entry point at address 0
SETALL     ; Light up all pixels
WAIT 30    ; Wait 0.25s (30 cycles @ 120Hz)
SETNONE    ; Turn off all pixels
LOOP       ; Repeat forever


2. Click **Run** to execute
3. Use **Step** for debugging
4. **Reset** to clear state

## Example Programs

### Blink Pattern

EP 0
SET 0 0, 1 1, 2 2, 3 3
WAIT 60
CLEAR 0 0, 1 1, 2 2, 3 3
WAIT 60
LOOP


### Memory Calculator

EP 0
STORE 10 15    ; Store 15 in RAM[10]
STORE 11 30    ; Store 30 in RAM[11]
ADD 10 11 12   ; RAM[12] = 15+30
SCRATCH_COPY 12 0 ; Save result to scratchpad


## Documentation

Full instruction set documentation available in the emulator's Help menu:
- Display control
- Memory operations
- Arithmetic/logic operations
- Program flow control
- Scratchpad operations
- Bitwise operations

## Testing

Run unit tests:

python -m unittest test_emulator.py


## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

## License

[MIT](https://choosealicense.com/licenses/mit/)

