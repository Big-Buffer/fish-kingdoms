import json
import logging
import re
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
import pyautogui
from Levenshtein import ratio
from paddleocr import PaddleOCR

from ScreenRegionSelector import ScreenRegionSelector

# 禁用PaddleOCR的日志
logging.disable(logging.DEBUG)
logging.getLogger('ppocr').setLevel(logging.ERROR)


class AutoAnswerPaddle:
    def __init__(self, file_path):
        self.file_path = file_path

        # 初始化区域坐标（将通过GUI设置）
        self.question_area = None
        self.true_button = None
        self.false_button = None

        # 初始化PaddleOCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')

        # 题库 - 数组格式
        self.question_bank = self.read_json_file()

        print(f"题库加载成功，共 {len(self.question_bank)} 个问题")

        # 设置屏幕区域
        self.setup_screen_areas()

    def setup_screen_areas(self):
        """通过GUI设置屏幕区域"""
        root = tk.Tk()
        root.attributes('-topmost', True)  # 确保窗口在最前面
        root.withdraw()  # 隐藏主窗口

        print("请按照提示设置屏幕区域坐标")

        # 设置问题区域
        messagebox.showinfo("设置问题区域", "请选择问题区域")
        question_selector = ScreenRegionSelector("选择问题区域")
        self.question_area = question_selector.get_area()

        if not self.question_area:
            print("未选择问题区域，程序退出")
            exit()

        print(f"问题区域设置: {self.question_area}")

        # 设置正确按钮区域
        messagebox.showinfo("设置正确按钮", "请选择正确按钮区域")
        true_selector = ScreenRegionSelector("选择正确按钮区域")
        self.true_button = true_selector.get_area()

        if not self.true_button:
            print("未选择正确按钮区域，程序退出")
            exit()

        print(f"正确按钮区域设置: {self.true_button}")

        # 设置错误按钮区域
        messagebox.showinfo("设置错误按钮", "请选择错误按钮区域")
        false_selector = ScreenRegionSelector("选择错误按钮区域")
        self.false_button = false_selector.get_area()

        if not self.false_button:
            print("未选择错误按钮区域，程序退出")
            exit()

        print(f"错误按钮区域设置: {self.false_button}")

        print("区域设置完成")

    def read_json_file(self):
        """读取JSON题库文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                if isinstance(data, list):
                    print(f"成功读取 {len(data)} 个问题")
                    return data
                else:
                    print("JSON文件应该是数组格式")
                    return []

        except Exception as e:
            print(f"读取文件错误: {e}")
            return []

    def create_question_dict(self):
        """根据新的JSON结构创建问题字典"""
        question_dict = {}
        for i, item in enumerate(self.question_bank):
            if isinstance(item, dict) and 'question' in item:
                question_text = item['question']
                answer = item.get('answer', '')

                # 将"对"/"错"转换为布尔值
                if answer == '对':
                    question_dict[question_text] = True
                elif answer == '错':
                    question_dict[question_text] = False
                else:
                    print(f"第 {i} 个问题答案格式不正确: {answer}")
            else:
                print(f"第 {i} 个问题格式不正确")

        print(f"成功创建 {len(question_dict)} 个有效问题")
        return question_dict

    def capture_screen_area(self, area):
        """捕获指定屏幕区域"""
        left, top, width, height = area
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def extract_text(self, image):
        """使用PaddleOCR提取文字"""
        try:
            result = self.ocr.predict(image)

            if result and result[0]:
                return ''.join(result[0]['rec_texts'])
            return ""
        except Exception as e:
            print(f"OCR识别错误: {e}")
            return ""

    def preprocess_text(self, text):
        """预处理文本，提高匹配准确率"""
        if not text:
            return ""

        # 移除标点符号和特殊字符，但保留问号
        text = re.sub(r'[^\w\u4e00-\u9fff?]', '', text)
        text = text.lower()
        return text

    def find_best_match(self, extracted_text, question_dict):
        """在题库中查找最佳匹配"""
        if not extracted_text or not question_dict:
            return None

        processed_text = self.preprocess_text(extracted_text)
        print(f"处理后的文本: {processed_text}")

        best_match = None
        highest_similarity = 0
        best_question = ""

        for question in question_dict.keys():
            processed_question = self.preprocess_text(question)

            similarity = ratio(processed_text, processed_question)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = question_dict[question]
                best_question = question

        print(f"最高相似度: {highest_similarity:.2f}")
        if best_question:
            print(f"匹配问题: {best_question}")

        if highest_similarity > 0.6:  # 提高阈值以减少误匹配
            return best_match
        return None

    def click_answer(self, is_correct):
        """点击答案按钮"""
        if is_correct:
            area = self.true_button
            button_name = "正确"
        else:
            area = self.false_button
            button_name = "错误"

        left, top, width, height = area
        x = left + width // 2
        y = top + height // 2
        pyautogui.click(x, y)
        print(f"点击了{button_name}按钮")
        time.sleep(0.5)

    def run(self):
        """主运行循环"""
        # 创建问题字典
        question_dict = self.create_question_dict()
        if not question_dict:
            print("没有有效的问题数据，程序退出")
            return

        print("自动答题脚本已启动，按Ctrl+C停止")
        print("正在监听问题区域...")

        try:
            while True:
                # 捕获并识别问题
                question_image = self.capture_screen_area(self.question_area)

                # 保存截图用于调试
                # cv2.imwrite('debug_question.png', question_image)
                # print("截图已保存为 debug_question.png")

                question_text = self.extract_text(question_image)

                if question_text and len(question_text.strip()) > 3:
                    print(f"识别到的问题: {question_text}")

                    # 查找答案并点击
                    answer = self.find_best_match(question_text, question_dict)
                    if answer is not None:
                        print(f"答案: {'正确' if answer else '错误'}")
                        self.click_answer(answer)
                    else:
                        print("未在题库中找到匹配答案")
                        # 可以添加默认策略，比如总是选择"正确"
                        # self.click_answer(True)
                else:
                    print("未识别到有效问题文本")

                time.sleep(3)

        except KeyboardInterrupt:
            print("\n脚本已停止")


if __name__ == "__main__":
    file_path = '题库/output.json'
    # 运行主程序
    auto_answer = AutoAnswerPaddle(file_path)
    auto_answer.run()