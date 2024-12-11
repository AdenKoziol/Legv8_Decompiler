import sys
import os

# Check if the correct number of command-line arguments is passed
if len(sys.argv) != 2:
    print("Usage: python disassembler.py <binary_file>")
    sys.exit(1)

# Get filename
filename = sys.argv[1]

# Check if file exists
if not os.path.isfile(filename):
    print(f"Error: {filename} not found.")
    sys.exit(1)

# All Legv8 instruction opcodes and corresponding names, types, and formats
instructions = {
    '10001011000': {"name": "ADD", "type": "R", "format": "ADD rd, rn, rm"},
    '1001000100': {"name": "ADDI", "type": "I", "format": "ADDI rd, rn, imm"},
    '10001010000': {"name": "AND", "type": "R", "format": "AND rd, rn, rm"},
    '1001001000': {"name": "ANDI", "type": "I", "format": "ANDI rd, rn, imm"},
    '000101': {"name": "B", "type": "B", "format": "B address"},
    '01010100': {"name": "Bcond", "type": "CB", "format": "B.cond address"},
    '100101': {"name": "BL", "type": "B", "format": "BL address"},
    '11010110000': {"name": "BR", "type": "R", "format": "BR rn"},
    '10110101': {"name": "CBNZ", "type": "CB", "format": "CBNZ rt, address"},
    '10110100': {"name": "CBZ", "type": "CB", "format": "CBZ rt, address"},
    '11001010000': {"name": "EOR", "type": "R", "format": "EOR rd, rn, rm"},
    '1101001000': {"name": "EORI", "type": "I", "format": "EORI rd, rn, imm"},
    '11111000010': {"name": "LDUR", "type": "D", "format": "LDUR rd, [rn, address]"},
    '11010011011': {"name": "LSL", "type": "R", "format": "LSL rd, rn, shamt"},
    '11010011010': {"name": "LSR", "type": "R", "format": "LSR rd, rn, shamt"},
    '10101010000': {"name": "ORR", "type": "R", "format": "ORR rd, rn, rm"},
    '1011001000': {"name": "ORRI", "type": "I", "format": "ORRI rd, rn, imm"},
    '11111000000': {"name": "STUR", "type": "D", "format": "STUR rd, [rn, address]"},
    '11001011000': {"name": "SUB", "type": "R", "format": "SUB rd, rn, rm"},
    '1101000100': {"name": "SUBI", "type": "I", "format": "SUBI rd, rn, imm"},
    '1111000100': {"name": "SUBIS", "type": "I", "format": "SUBIS rd, rn, imm"},
    '11101011000': {"name": "SUBS", "type": "R", "format": "SUBS rd, rn, rm"},
    '10011011000': {"name": "MUL", "type": "R", "format": "MUL rd, rn, rm"},
    '11111111101': {"name": "PRNT", "type": "R", "format": "PRNT rd"},
    '11111111100': {"name": "PRNL", "type": "R", "format": "PRNL"},
    '11111111110': {"name": "DUMP", "type": "R", "format": "DUMP"},
    '11111111111': {"name": "HALT", "type": "R", "format": "HALT"},
}

# All Legv8 instruction types and their corresponding formats aned elements
instruction_types = {
    'R': {'format': [[21, 0x7FF], [16, 0x1F], [10, 0x3F], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'rm', 'shamt', 'rn', 'rd'],},
    'I': {'format': [[22, 0x3FF], [10, 0xFFF], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'imm', 'rn', 'rd'],},
    'D': {'format': [[21, 0x7FF], [12, 0x1FF], [10, 0x3], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'address', 'op', 'rn', 'rd'],},
    'B': {'format': [[26, 0x3F], [0, 0x3FFFFFF]],
          'elements': ['opcode', 'address'],},
    'CB': {'format': [[24, 0xFF], [5, 0x7FFFF], [0, 0x1F]],
           'elements': ['opcode', 'address', 'rt'],},
    'IW': {'format': [[21, 0x7FF], [5, 0xFFFF], [0, 0x1F]],
           'elements': ['opcode', 'imm', 'rd'],}
}

# All conditionals for B.cond
conditional_codes = {
    0b0000: 'EQ',
    0b0001: 'NE',
    0b0010: 'HS',
    0b0011: 'LO',
    0b0100: 'MI',
    0b0101: 'PL',
    0b0110: 'VS',
    0b0111: 'VC',
    0b1000: 'HI',
    0b1001: 'LS',
    0b1010: 'GE',
    0b1011: 'LT',
    0b1100: 'GT',
    0b1101: 'LE',
}

# Converts val to twos complement
def twos_complement(val, bit_length):
    if val & (1 << (bit_length - 1)):
        return val - (1 << bit_length)
    return val

# Converts a binary instruction to a machine instruction
def decode_machine_instruction(instruction, machine_code):
    format_type = instruction['type'] 
    format_details = instruction_types[format_type]['format']
    bit_fields = instruction_types[format_type]['elements']
    output_template = instruction["format"]
    
    for j, (shift, mask) in enumerate(format_details):
        key = bit_fields[j]
        value = (int(machine_code, 2) >> shift) & mask
        
        if instruction['name'] == "Bcond" and key in ["rt", "address"]:
            if key == "rt":
                output_value = conditional_codes.get(value, "UNKNOWN")
                key = "cond"
            else:
                output_value = hex(value)
        elif key in ["imm", "address"]:
            if key == "imm" and format_type == "I" or key == "address" and format_type == "D":
                if(format_type == "I"):
                    value = twos_complement(value, 12)
                else:
                    value = twos_complement(value, 9)
                output_value = "#" + str(value)
            else:
                output_value = hex(value) if format_type in ["B", "CB"] else "#" + str(value)
        elif key == "shamt" and instruction['name'] in ["LSL", "LSR"]:
            output_value = "#" + str(value)
        else:
            register = value
            output_value = {30: "LR", 29: "FP", 28: "SP"}.get(register, f"X{register}")
        
        output_template = output_template.replace(key, output_value)
    
    return output_template

try:
    with open(filename, "rb") as file:
        data = file.read()
        binary_machine_code = ''.join(format(byte, '08b') for byte in data)
        binary_code_segment = [binary_machine_code[i:i+32] for i in range(0, len(binary_machine_code), 32)]
        
except Exception as e:
    print(f"Error reading the binary file: {e}")
    sys.exit(1)

instruction_number = 0
for binary_instruction in binary_code_segment:
    instruction_number += 1
    decoded = None
    for opcode, instruction in instructions.items():
        if binary_instruction.startswith(opcode):
            decoded = decode_machine_instruction(instruction, binary_instruction)
            break
    if decoded:
        print(f"{decoded}")
    else:
        print("Unknown Instruction")