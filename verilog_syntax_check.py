import re
import sys


def find_ports(file_content):
    """Find all input/output ports declared in the module."""
    ports = re.findall(r'\b(input|output)\b\s+(?:\[.*?\]\s+)?(\w+)', file_content)
    return {port for _, port in ports}


def find_logic_usage(file_content):
    """Find all variables used in logical operations."""
    usage = re.findall(r'\b(\w+)\b\s*(?:=|<=|==|!=|&|\||\^|~|\+|-|\*|/|%)', file_content)
    return set(usage)


def check_port_usage(file_content):
    """Check if all ports are logically used."""
    ports = find_ports(file_content)
    logic_usage = find_logic_usage(file_content)

    unused_ports = ports - logic_usage
    if unused_ports:
        print(f"Warning: The following ports are declared but not used in logic: {unused_ports}")


def find_blocks(file_content, pattern):
    """Find all blocks matching a specific pattern."""
    return re.findall(pattern, file_content, re.DOTALL)


def check_non_blocking_in_comb(always_block):
    """Check for non-blocking assignments in always @(*) blocks."""
    errors = []
    for line in always_block.splitlines():
        if '<=' in line:  # Non-blocking assignment
            errors.append(line.strip())
    return errors


def check_blocking_in_seq(always_block):
    """Check for blocking assignments in always @(posedge) blocks."""
    errors = []
    for line in always_block.splitlines():
        if '=' in line and '<=' not in line:  # Blocking assignment
            errors.append(line.strip())
    return errors


def find_assigned_variables(always_block):
    """Find all variables assigned in an always block."""
    return set(re.findall(r'(\b\w+\b)\s*(?:<=|=)', always_block))


def find_declared_regs(file_content):
    """Find all variables declared as reg."""
    return set(re.findall(r'\breg\b\s+([\w\[\]:]+)', file_content))


def match_begin_end(always_block):
    """Check if begin and end are properly matched in an always block."""
    begin_count = always_block.count('begin')
    end_count = always_block.count('end')
    return begin_count == end_count


def analyze_always_blocks(file_content):
    """Analyze always blocks for correctness."""
    comb_pattern = r'always\s*@\(\*\)\s*(begin.*?end|[^;]*;)'
    seq_pattern = r'always\s*@\(posedge.*?\)\s*(begin.*?end|[^;]*;)'

    comb_blocks = find_blocks(file_content, comb_pattern)
    seq_blocks = find_blocks(file_content, seq_pattern)

    declared_regs = find_declared_regs(file_content)

    comb_errors = 0
    seq_errors = 0
    reg_errors = 0
    begin_end_errors = 0

    for i, block in enumerate(comb_blocks, 1):
        if 'begin' in block and not match_begin_end(block):
            print(f"Error: Mismatched begin-end in always @(*) block #{i}.")
            begin_end_errors += 1

        errors = check_non_blocking_in_comb(block)
        if errors:
            print(f"Error: Non-blocking assignment(s) found in always @(*) block #{i}:")
            for err in errors:
                print(f"  - {err}")
            comb_errors += len(errors)

        assigned_vars = find_assigned_variables(block)
        undefined_vars = assigned_vars - declared_regs
        if undefined_vars:
            print(f"Error: Variables assigned in always @(*) block #{i} are not declared as reg: {undefined_vars}")
            reg_errors += len(undefined_vars)

    for i, block in enumerate(seq_blocks, 1):
        if 'begin' in block and not match_begin_end(block):
            print(f"Error: Mismatched begin-end in always @(posedge) block #{i}.")
            begin_end_errors += 1

        errors = check_blocking_in_seq(block)
        if errors:
            print(f"Error: Blocking assignment(s) found in always @(posedge) block #{i}:")
            for err in errors:
                print(f"  - {err}")
            seq_errors += len(errors)

        assigned_vars = find_assigned_variables(block)
        undefined_vars = assigned_vars - declared_regs
        if undefined_vars:
            print(f"Error: Variables assigned in always @(posedge) block #{i} are not declared as reg: {undefined_vars}")
            reg_errors += len(undefined_vars)

    print("\nSummary:")
    print(f"  - Combinational always blocks checked: {len(comb_blocks)}")
    print(f"  - Sequential always blocks checked: {len(seq_blocks)}")
    print(f"  - Errors in always @(*) blocks: {comb_errors}")
    print(f"  - Errors in always @(posedge) blocks: {seq_errors}")
    print(f"  - Undeclared reg errors: {reg_errors}")
    print(f"  - Mismatched begin-end errors: {begin_end_errors}")


def check_module_endmodule(file_content):
    """Check if module and endmodule are properly matched."""
    module_count = len(re.findall(r'\bmodule\b', file_content))
    endmodule_count = len(re.findall(r'\bendmodule\b', file_content))
    
    if module_count != endmodule_count:
        print(f"Error: Mismatched module and endmodule statements.")
        print(f"  - Number of module: {module_count}")
        print(f"  - Number of endmodule: {endmodule_count}")
    else:
        print("Info: module and endmodule statements are properly matched.")


def run_verilog_syntax_check(filename):
    """Run syntax checks on the given Verilog file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            file_content = file.read()

        print(f"Checking Verilog syntax for {filename}...\n")

        check_port_usage(file_content)
        check_module_endmodule(file_content)
        analyze_always_blocks(file_content)

        print("\nSyntax check completed.")
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}. Please check the file encoding.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verilog_syntax_checker.py <verilog_file>")
        sys.exit(1)

    verilog_file = sys.argv[1]
    run_verilog_syntax_check(verilog_file)
