import yaml
import sys

def get_nested_value(data, keys):
    """递归获取嵌套的值"""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data

def main():
    # 检查参数
    if len(sys.argv) != 3:
        print("Usage: python read_yaml.py <yaml_file> <key_path>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    key_path = sys.argv[2]

    # 加载 YAML 文件
    try:
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File '{yaml_file}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file. {e}")
        sys.exit(1)

    # 获取嵌套值
    keys = key_path.split('.')
    value = get_nested_value(config, keys)

    if value is None:
        print(f"Error: Key path '{key_path}' not found.")
        sys.exit(1)

    # 输出结果
    print(value)

if __name__ == "__main__":
    main()