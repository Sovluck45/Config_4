import struct
import math
import xml.etree.ElementTree as ET

# Constants for command codes
LOAD_CONSTANT = 0x0
READ_MEMORY = 0x4
WRITE_MEMORY = 0x9
SQRT_OPERATION = 0x20


# Assembler
class Assembler:
    def assemble(self, source_code_path, binary_output_path, log_output_path):
        with open(source_code_path, 'r') as source_file:
            lines = source_file.readlines()

        binary_data = bytearray()
        log_data = []

        for line in lines:
            parts = line.strip().split()
            command = parts[0]
            args = list(map(int, parts[1:]))

            if command == "LOAD":
                binary_data.extend(self._encode_command(LOAD_CONSTANT, args))
                log_data.append(f"LOAD Constant={args[1]} Address={args[0]}")
            elif command == "READ":
                binary_data.extend(self._encode_command(READ_MEMORY, args))
                log_data.append(f"READ Address1={args[0]} Address2={args[1]}")
            elif command == "WRITE":
                binary_data.extend(self._encode_command(WRITE_MEMORY, args))
                log_data.append(f"WRITE Address1={args[0]} Address2={args[1]}")
            elif command == "SQRT":
                binary_data.extend(self._encode_command(SQRT_OPERATION, args))
                log_data.append(f"SQRT Address1={args[0]} Address2={args[1]}")

        with open(binary_output_path, 'wb') as binary_file:
            binary_file.write(binary_data)

        with open(log_output_path, 'w') as log_file:
            log_file.write('\n'.join(log_data))

    def _encode_command(self, command, args):
        if command == LOAD_CONSTANT:
            return struct.pack('<BHI', command, args[0], args[1])
        elif command in {READ_MEMORY, WRITE_MEMORY, SQRT_OPERATION}:
            return struct.pack('<BHH', command, args[0], args[1])


# Interpreter
class Interpreter:
    def interpret(self, binary_input_path, result_output_path, memory_range):
        with open(binary_input_path, 'rb') as binary_file:
            binary_data = binary_file.read()

        memory = [0] * 1024  # Initialize memory
        pc = 0  # Program counter

        while pc < len(binary_data):
            command = binary_data[pc]

            if command == LOAD_CONSTANT:
                _, addr, constant = struct.unpack('<BHI', binary_data[pc:pc + 7])
                memory[addr] = constant
                pc += 7
            elif command == READ_MEMORY:
                _, addr1, addr2 = struct.unpack('<BHH', binary_data[pc:pc + 5])
                memory[addr2] = memory[addr1]
                pc += 5
            elif command == WRITE_MEMORY:
                _, addr1, addr2 = struct.unpack('<BHH', binary_data[pc:pc + 5])
                memory[addr2] = memory[addr1]
                pc += 5
            elif command == SQRT_OPERATION:
                _, addr1, addr2 = struct.unpack('<BHH', binary_data[pc:pc + 5])
                memory[addr2] = int(math.sqrt(memory[addr1]))
                pc += 5

        self._write_results_to_xml(result_output_path, memory, memory_range)

    def _write_results_to_xml(self, result_output_path, memory, memory_range):
        root = ET.Element("MemoryDump")
        for i in range(memory_range[0], memory_range[1] + 1):
            cell = ET.SubElement(root, "Cell", Address=str(i))
            cell.text = str(memory[i])

        tree = ET.ElementTree(root)
        tree.write(result_output_path)


# Example usage
if __name__ == "__main__":
    assembler = Assembler()
    interpreter = Interpreter()

    # Assemble the source code
    assembler.assemble(
        source_code_path="source.txt",
        binary_output_path="program.bin",
        log_output_path="log.txt"
    )

    # Interpret the binary program
    interpreter.interpret(
        binary_input_path="program.bin",
        result_output_path="result.xml",
        memory_range=(0, 10)
    )
