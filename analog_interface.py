import pandas as pd
from collections import defaultdict
import sys


def read_excel_data(input_file):
    """
    从 Excel 文件中读取数据并返回 DataFrame
    跳过标题行，从第 2 行开始读取。
    """
    df = pd.read_excel(input_file, skiprows=1, header=None, names=["PortName", "Direction", "Type", "FromTo"])
    return df


def process_data(df):
    """
    根据规则处理数据，生成 Verilog 的端口定义，同时统计生成的端口信息
    """
    # 定义方向映射
    direction_map = {"CA": "output", "AC": "input", "RA": "output", "AR": "input"}

    # 过滤掉 "pad" 类型的行
    ungenerated_ports = df[df["Type"] == "pad"]  # 未生成的端口记录
    df = df[df["Type"] != "pad"]

    # 存储处理后的信号
    ports = defaultdict(list)

    # 统计生成的端口数
    stats = {"input": 0, "output": 0}

    # 处理每一行数据
    for _, row in df.iterrows():
        port_name = row["PortName"]
        direction = direction_map.get(row["FromTo"], "input")  # 默认方向为 input
        if "<" in port_name:
            # 提取位宽信息并标准化
            base_name, range_part = port_name.split("<")
            range_part = range_part.strip(">")
            if ":" in range_part:
                start, end = map(int, range_part.split(":"))
            else:
                start = end = int(range_part)
            ports[(base_name, direction)].append((start, end))
        else:
            # 无位宽信息
            ports[(port_name, direction)].append(None)

    # 合并位宽并统计
    verilog_ports = []
    for (base_name, direction), ranges in ports.items():
        if all(r is None for r in ranges):
            # 无位宽信息
            verilog_ports.append(f"{direction} {base_name}")
        else:
            # 合并位宽
            min_bit = min(r[1] for r in ranges if r is not None)
            max_bit = max(r[0] for r in ranges if r is not None)
            verilog_ports.append(f"{direction} [{max_bit}:{min_bit}] {base_name}")

        # 更新统计
        stats[direction] += 1

    return verilog_ports, stats, ungenerated_ports


def generate_verilog_file(verilog_ports, output_file):
    """
    根据处理后的端口定义，生成 Verilog 文件
    """
    verilog_code = "module generated_ports (\n"
    verilog_code += "    " + ",\n    ".join(verilog_ports) + "\n"
    verilog_code += ");\n\nendmodule"

    # 写入 Verilog 文件
    with open(output_file, "w") as f:
        f.write(verilog_code)
    print(f"Verilog file generated: {output_file}")


if __name__ == "__main__":
    # 从命令行接收输入文件名
    if len(sys.argv) != 2:
        print("Usage: python analog_interface.py <ExcelFileName>")
        sys.exit(1)

    input_file = sys.argv[1]  # 从命令行获取 Excel 文件名
    output_file = "generated_ports.v"  # 输出的 Verilog 文件名

    try:
        # 读取数据
        df = read_excel_data(input_file)

        # 处理数据，生成 Verilog 端口定义
        verilog_ports, stats, ungenerated_ports = process_data(df)

        # 生成 Verilog 文件
        generate_verilog_file(verilog_ports, output_file)

        # Display statistics
        print("\n===== Port Generation Summary =====")
        print(f"Number of input ports generated: {stats['input']}")
        print(f"Number of output ports generated: {stats['output']}")
        print(f"Number of ports not generated: {len(ungenerated_ports)}")
        if not ungenerated_ports.empty:
            print("\nDetails of ports not generated:")
            print(ungenerated_ports[["PortName", "Type"]].to_string(index=False))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
