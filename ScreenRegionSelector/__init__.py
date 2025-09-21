import tkinter as tk
from tkinter import messagebox


class ScreenRegionSelector:
    def __init__(self, title="选择区域"):
        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)

        # 确保窗口获得焦点
        self.root.focus_force()
        self.root.grab_set()

        # 获取屏幕尺寸
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # 创建画布
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height,
                                bg='black', highlightthickness=0, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 信息标签
        self.info_label = tk.Label(self.root, text="拖拽鼠标选择区域，按回车确认",
                                   font=("Arial", 16), bg='yellow', fg='black')
        self.info_label.place(x=50, y=50)

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Return>", self.confirm_selection)
        self.root.bind("<Escape>", self.cancel_selection)
        self.root.protocol("WM_DELETE_WINDOW", self.cancel_selection)

        # 初始化变量
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selected_area = None
        self.is_completed = False

    def on_button_press(self, event):
        if self.rect:
            self.canvas.delete(self.rect)

        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        pass  # 选择在按回车时确认

    def confirm_selection(self, event=None):
        if self.rect:
            coords = self.canvas.coords(self.rect)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # 确保坐标正确（x2 > x1, y2 > y1）
                if x2 < x1:
                    x1, x2 = x2, x1
                if y2 < y1:
                    y1, y2 = y2, y1
                self.selected_area = (x1, y1, x2 - x1, y2 - y1)
                self.is_completed = True
        self.root.quit()
        self.root.destroy()

    def cancel_selection(self, event=None):
        self.selected_area = None
        self.is_completed = True
        self.root.quit()
        self.root.destroy()

    def get_area(self):
        self.root.mainloop()
        return self.selected_area


# 使用示例
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo("设置问题区域", "请选择问题区域")
    selector = ScreenRegionSelector()
    area = selector.get_area()

    if area:
        print(f"选择的区域: x={area[0]}, y={area[1]}, 宽度={area[2]}, 高度={area[3]}")
    else:
        print("未选择区域")

    root.destroy()