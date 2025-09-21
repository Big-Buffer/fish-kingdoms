import json


def parse_json_lines(file_path):
    """
    读取文件，逐行解析JSON数据
    :param file_path: 文件路径
    :return: 包含所有解析后JSON对象的列表
    """
    data_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json_obj = json.loads(line)
                        data_list.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"第 {line_number} 行JSON解析错误: {e}")
                        print(f"问题行内容: {line}")
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到")
        return []
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return []

    return data_list


def edit_json_data(data_list):
    """
    编辑JSON数据
    :param data_list: 原始数据列表
    :return: 编辑后的数据列表
    """
    edited_data = []

    for i, item in enumerate(data_list):
        # 创建数据副本，避免修改原始数据
        edited_item = item.copy()

        # 示例编辑操作1：为每个问题添加序号
        edited_item['q'] = f"{i + 1}. {item.get('q', '')}"

        # 示例编辑操作2：转换答案格式（A->对，B->错等）
        answer_mapping = {'A': '对', 'B': '错'}
        if 'ans' in edited_item and edited_item['ans'] in answer_mapping:
            edited_item['correct_answer'] = answer_mapping[edited_item['ans']]

        # 示例编辑操作4：重新组织选项格式
        if 'a' in edited_item and isinstance(edited_item['a'], list):
            edited_item['options'] = {
                'A': edited_item['a'][0] if len(edited_item['a']) > 0 else '',
                'B': edited_item['a'][1] if len(edited_item['a']) > 1 else ''
            }
            # 可以删除原始字段或保留
            del edited_item['a']

        edited_data.append(edited_item)

    return edited_data


def save_to_json_file(data_list, output_file_path, format='lines'):
    """
    将数据保存到JSON文件
    :param data_list: 要保存的数据列表
    :param output_file_path: 输出文件路径
    :param format: 保存格式 - 'lines'（每行一个JSON）或 'array'（JSON数组）
    """
    try:
        if format == 'lines':
            # 每行一个JSON对象
            with open(output_file_path, 'w', encoding='utf-8') as f:
                for item in data_list:
                    json_line = json.dumps(item, ensure_ascii=False)
                    f.write(json_line + '\n')
        else:
            # 保存为JSON数组
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)

        print(f"数据已成功保存到: {output_file_path}")
        print(f"保存了 {len(data_list)} 条记录")

    except Exception as e:
        print(f"保存文件时发生错误: {e}")


def custom_edit_function(data_list):
    """
    自定义编辑函数 - 根据实际需求修改这个函数
    :param data_list: 原始数据
    :return: 编辑后的数据
    """
    edited_data = []

    for item in data_list:
        # 在这里添加您的自定义编辑逻辑
        edited_item = item.copy()

        # 示例：修改问题格式
        if 'q' in edited_item:
            edited_item['question'] = edited_item['q']
            del edited_item['q']

        # 示例：修改答案格式
        if 'ans' in edited_item:
            edited_item['answer'] = '对' if edited_item.get('ans') == 'A' else '错'
            del edited_item['ans']

        del edited_item['a']

        edited_data.append(edited_item)

    return edited_data


def main():
    # 文件路径配置
    input_file_path = '202509.txt'  # 输入文件路径
    output_file_path = 'output.json'  # 输出文件路径

    # 1. 读取并解析文件
    print("正在读取文件...")
    original_data = parse_json_lines(input_file_path)

    if not original_data:
        print("没有读取到数据，程序退出")
        return

    print(f"成功读取 {len(original_data)} 条数据")

    # 2. 显示原始数据
    print("\n原始数据示例:")
    for i, item in enumerate(original_data[:3], 1):  # 显示前3条
        print(f"{i}. 问题: {item.get('q', 'N/A')}")
        print(f"   选项: {item.get('a', [])}")
        print(f"   答案: {item.get('ans', 'N/A')}")
        print()

    # 3. 编辑数据（使用默认编辑函数或自定义函数）
    print("正在编辑数据...")
    # edited_data = edit_json_data(original_data)  # 使用默认编辑函数
    edited_data = custom_edit_function(original_data)  # 使用自定义编辑函数

    # 4. 显示编辑后的数据
    print("\n编辑后的数据示例:")
    for i, item in enumerate(edited_data[:3], 1):  # 显示前3条
        print(f"{i}. {json.dumps(item, ensure_ascii=False)}")
        print()

    # 5. 保存到文件
    print("正在保存数据...")
    # save_to_json_file(edited_data, output_file_path, format='lines')
    # 或者保存为JSON数组格式：
    save_to_json_file(edited_data, output_file_path, format='array')


if __name__ == "__main__":
    main()