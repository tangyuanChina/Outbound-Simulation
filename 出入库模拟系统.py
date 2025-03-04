import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import matplotlib.pyplot as plt
import mysql.connector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mysql.connector import Error


######################################商品信息维护函数部分
# 连接到本地MySQL数据库
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="TANGtang@1475514",
        database="出库模拟"
    )


# 显示数据库中的内容
def fetch_data():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 商品信息表")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Error as e:
        print(f"Error: {e}")
        return []


# 刷新表格
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    rows = fetch_data()
    for row in rows:
        tree.insert("", "end", values=row)


# 添加数据
def add_data():
    product_id = simpledialog.askstring("输入", "请输入商品编号:")
    product_name = simpledialog.askstring("输入", "请输入商品名称:")
    product_model = simpledialog.askstring("输入", "请输入商品型号:")
    product_price = simpledialog.askstring("输入", "请输入商品价格:")
    wholesale_price = simpledialog.askstring("输入", "请输入商品批发价格:")

    # 输入字段检查
    if len(product_id) > 255 or len(product_name) > 255 or len(product_model) > 255:
        messagebox.showerror("错误", "输入字段长度超出限制（最大255字符）")
        return

    try:
        product_price = float(product_price)
        wholesale_price = float(wholesale_price)
    except ValueError:
        messagebox.showerror("错误", "商品价格和批发价格必须是数字")
        return

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO 商品信息表 (商品编号, 商品名称, 商品型号, 商品价格, 商品批发价格)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_id, product_name, product_model, product_price, wholesale_price))
        conn.commit()
        conn.close()
        refresh_table()
    except Error as e:
        messagebox.showerror("错误", f"添加数据失败: {e}")


# 删除数据
def delete_data():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        product_id = item['values'][0]

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM 商品信息表 WHERE 商品编号 = %s", (product_id,))
            conn.commit()
            conn.close()
            refresh_table()
        except Error as e:
            messagebox.showerror("错误", f"删除数据失败: {e}")
    else:
        messagebox.showwarning("警告", "请选择要删除的项")


# 更新数据
def update_data():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        product_id = item['values'][0]

        product_name = simpledialog.askstring("更新", f"更新商品名称 (当前: {item['values'][1]}):")
        product_model = simpledialog.askstring("更新", f"更新商品型号 (当前: {item['values'][2]}):")
        product_price = simpledialog.askstring("更新", f"更新商品价格 (当前: {item['values'][3]}):")
        wholesale_price = simpledialog.askstring("更新", f"更新商品批发价格 (当前: {item['values'][4]}):")

        # 输入字段检查
        if len(product_name) > 255 or len(product_model) > 255:
            messagebox.showerror("错误", "输入字段长度超出限制（最大255字符）")
            return

        try:
            product_price = float(product_price)
            wholesale_price = float(wholesale_price)
        except ValueError:
            messagebox.showerror("错误", "商品价格和批发价格必须是数字")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE 商品信息表 
                SET 商品名称 = %s, 商品型号 = %s, 商品价格 = %s, 商品批发价格 = %s
                WHERE 商品编号 = %s
            """, (product_name, product_model, product_price, wholesale_price, product_id))
            conn.commit()
            conn.close()
            refresh_table()
        except Error as e:
            messagebox.showerror("错误", f"更新数据失败: {e}")
    else:
        messagebox.showwarning("警告", "请选择要更新的项")


# 退出商品信息维护并回到主菜单
def exit_to_main_menu(product_window):
    if messagebox.askyesno("退出", "确定返回主菜单吗？"):
        product_window.destroy()  # 销毁商品信息窗口


######################################

######################################仿真模拟函数部分
# 初始化库存管理系统
class InventorySystem:
    def __init__(self, stock, danger_threshold, reorder_amount, early_warning_threshold, price, wholesale_price):
        """
        初始化库存管理系统实例

        :param stock: 初始库存量
        :param danger_threshold: 危险库存量
        :param reorder_amount: 每次发货的订单量
        :param early_warning_threshold: 提前警告阈值
        """
        self.stock = stock
        self.danger_threshold = danger_threshold
        self.reorder_amount = reorder_amount
        self.early_warning_threshold = early_warning_threshold  # 添加提前警告阈值
        self.price = price  # 记录商品价格
        self.wholesale_price = wholesale_price  # 记录商品批发价格
        self.stock_history = []  # 记录库存历史变化
        self.reorder_days = []  # 记录发货的天数
        self.pending_orders = []  # 记录待发货的订单
        self.benefit = []  # 记录每天的收益
        self.expense = []  # 记录每天的支出
        self.is_order_pending = False  # 标记当前是否有待发货的订单

    def check_stock(self, day, restock_time_min, restock_time_max):
        """
        检查库存是否低于危险库存量，如果低于提前警告阈值，则发起订单

        :param day: 当前的天数，用于记录发起订单的时间
        """
        if self.stock < self.early_warning_threshold and not self.is_order_pending:
            # 打开（或创建）一个文本文件用来记录模拟情况
            with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
                file.write(f"\n库存接近危险库存量！当前库存：{self.stock}, 提前发起订单！")
            self.place_order(day, restock_time_min, restock_time_max)

    def place_order(self, day, restock_time_min, restock_time_max):
        """
        发起订单并延迟到货（随机）

        :param day: 当前的天数，用于记录发货的时间
        """
        self.is_order_pending = True
        restocking_time = random.randint(restock_time_min, restock_time_max)  # 随机设置补货的时间（2-3天）
        # 打开（或创建）一个文本文件用来记录模拟情况
        with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
            file.write(f"\n发出订单，数量为：{self.reorder_amount}，预计到货时间：{restocking_time}天后...")
        self.reorder_days.append(day)
        self.pending_orders.append(day + restocking_time)  # 记录订单预计到货的时间

    def receive_order(self, delivery_day):
        """
        接收订单，更新库存

        :param delivery_day: 订单到货的天数
        """
        # 打开（或创建）一个文本文件用来记录模拟情况
        with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
            file.write(f"\n订单到货，库存增加 {self.reorder_amount} 个，当前库存：{self.stock + self.reorder_amount}。")
        self.stock += self.reorder_amount
        # 打开（或创建）一个文本文件用来记录模拟情况
        with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
            file.write(f"\n当前库存：{self.stock}")
        self.is_order_pending = False  # 重置订单状态为无待发货订单
        self.record_stock()
        self.expenses()

    def outgoing_goods(self, amount, day, restock_time_min, restock_time_max):
        """
        出库操作
        :param amount: 出库的数量
        :param day: 当前的天数
        """
        if self.stock >= amount:
            self.stock -= amount
            # 打开（或创建）一个文本文件用来记录模拟情况
            with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
                file.write(f"\n出库 {amount} 个，当前库存：{self.stock}")
        else:
            # 打开（或创建）一个文本文件用来记录模拟情况
            with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
                file.write(f"\n库存不足，无法出库 {amount} 个，当前库存：{self.stock}")
        self.record_stock()
        self.check_stock(day, restock_time_min, restock_time_max)
        self.benefits(amount)

    def record_stock(self):
        """
        记录当前库存到库存历史
        """
        self.stock_history.append(self.stock)

    def benefits(self, outgoing_goods_amount):
        """
        记录每天收益
        """
        self.benefit.append(outgoing_goods_amount * self.price)

    def expenses(self):
        """
        记录每天支出
        """
        self.expense.append(self.reorder_amount * self.wholesale_price)

    def process_pending_orders(self, current_day):
        """
        处理待发货的订单

        :param current_day: 当前的天数，用于判断哪些订单需要到货
        """
        for delivery_day in self.pending_orders[:]:
            if delivery_day == current_day:
                self.pending_orders.remove(delivery_day)
                self.receive_order(current_day)


######################################

##############################################菜单部分
# 设置主菜单界面
def main_menu():
    global root
    root = tk.Tk()
    root.title("出入库仿真系统")
    root.geometry("400x300")

    # 创建菜单
    menubar = tk.Menu(root)

    # 商品信息维护菜单项
    product_menu = tk.Menu(menubar, tearoff=0)
    product_menu.add_command(label="商品信息维护", command=open_product_info)
    menubar.add_cascade(label="商品信息维护", menu=product_menu)

    # 仿真模拟菜单项
    simulation_menu = tk.Menu(menubar, tearoff=0)
    simulation_menu.add_command(label="仿真模拟", command=Simulated_Modeling)
    menubar.add_cascade(label="仿真模拟", menu=simulation_menu)

    # 退出菜单项
    menubar.add_command(label="退出", command=root.quit)

    # 显示菜单栏
    root.config(menu=menubar)

    root.mainloop()


######################################

########################################################商品信息维护可视化部分
# 打开商品信息维护窗口
def open_product_info():
    global tree
    # 创建商品信息维护窗口
    product_window = tk.Toplevel(root)
    product_window.title("商品信息维护")
    product_window.geometry("1200x600")

    # 创建表格
    tree = ttk.Treeview(product_window, columns=("商品编号", "商品名称", "商品型号", "商品价格", "商品批发价格"),
                        show="headings")
    tree.heading("商品编号", text="商品编号")
    tree.heading("商品名称", text="商品名称")
    tree.heading("商品型号", text="商品型号")
    tree.heading("商品价格", text="商品价格")
    tree.heading("商品批发价格", text="商品批发价格")
    tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    # 刷新显示数据按钮
    refresh_button = tk.Button(product_window, text="刷新数据", command=refresh_table)
    refresh_button.grid(row=2, column=3, columnspan=4, padx=10, pady=10, sticky="ew")

    # 添加、删除、更新按钮
    add_button = tk.Button(product_window, text="添加", command=add_data)
    add_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    delete_button = tk.Button(product_window, text="删除", command=delete_data)
    delete_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    update_button = tk.Button(product_window, text="修改", command=update_data)
    update_button.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

    # 退出按钮
    exit_button = tk.Button(product_window, text="返回主菜单", command=lambda: exit_to_main_menu(product_window))
    exit_button.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

    # 配置行列权重，确保布局自适应窗口大小
    product_window.grid_rowconfigure(0, weight=1)  # 表格所在行可拉伸
    product_window.grid_columnconfigure((0, 1, 2, 3), weight=1)  # 按钮和表格所在列可拉伸

    # 初始化
    refresh_table()


######################################

########################################################仿真模拟可视化部分
# 主可视化界面
class InventorySimulationApp:
    def __init__(self, root):
        """
        初始化库存管理模拟应用程序

        :param root: tkinter根窗口
        """
        self.root = root
        self.root.geometry("1100x1000")
        self.root.title("库存管理模拟")

        # 连接到本地MySQL数据库
        def create_connection():
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="TANGtang@1475514",
                database="出库模拟"
            )

        # 显示数据库中的内容
        def fetch_data():
            try:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM 商品信息表")
                rows = cursor.fetchall()
                conn.close()
                return rows
            except Error as e:
                print(f"Error: {e}")
                return []

        # 刷新表格
        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)

            rows = fetch_data()
            for row in rows:
                tree.insert("", "end", values=row)

        # 刷新表格
        def refresh_table_1():
            for row in tree.get_children():
                tree.delete(row)

            rows = fetch_data()
            for row in rows:
                tree.insert("", "end", values=row)
            # 刷新商品价格和商品批发价格
            self.price_entry.delete(0, tk.END)  # 删除从0到最后的内容
            self.wholesale_price_entry.delete(0, tk.END)  # 删除从0到最后的内容
            self.price_entry.insert(0, 0)  # 默认值
            self.wholesale_price_entry.insert(0, 0)  # 默认值

        # 用于存储点击的商品价格和批发价格
        clicked_items = []  # 存储点击的商品价格和批发价格的列表

        def on_item_click(event):
            selected_item = tree.selection()
            clicked_items = [0, 0]  # 存储点击的商品价格和批发价格的列表清空
            if selected_item:
                item = tree.item(selected_item)
                self.product_price = item['values'][3]
                self.wholesale_price = item['values'][4]

                # 将商品价格和批发价格添加到列表
                clicked_items[0] = (self.product_price)
                clicked_items[1] = (self.wholesale_price)
                # 更新商品价格和商品批发价格
                self.price_entry.delete(0, tk.END)  # 删除从0到最后的内容
                self.wholesale_price_entry.delete(0, tk.END)  # 删除从0到最后的内容
                self.price_entry.insert(0, clicked_items[0])  # 默认值
                self.wholesale_price_entry.insert(0, clicked_items[1])  # 默认值

                # 弹出对话框显示价格信息
                messagebox.showinfo("商品价格信息",
                                    f"商品价格: {self.product_price}\n商品批发价格: {self.wholesale_price}")
            return clicked_items

        # 创建表格
        tree = ttk.Treeview(root, columns=("商品编号", "商品名称", "商品型号", "商品价格", "商品批发价格"),
                            show="headings")
        tree.heading("商品编号", text="商品编号")
        tree.heading("商品名称", text="商品名称")
        tree.heading("商品型号", text="商品型号")
        tree.heading("商品价格", text="商品价格")
        tree.heading("商品批发价格", text="商品批发价格")

        # 表格位置使用grid
        tree.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # 绑定点击事件
        tree.bind("<ButtonRelease-1>", on_item_click)

        # 刷新显示数据按钮
        refresh_button = tk.Button(root, text="刷新数据", command=refresh_table_1)
        refresh_button.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # 初始化
        refresh_table()

        # 输入框和标签
        self.initial_stock_label = tk.Label(root, text="初始库存量:")
        self.initial_stock_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.initial_stock_entry = tk.Entry(root)
        self.initial_stock_entry.grid(row=2, column=1, padx=5, pady=5)
        self.initial_stock_entry.insert(0, "100")  # 默认值

        self.danger_threshold_label = tk.Label(root, text="危险库存量:")
        self.danger_threshold_label.grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.danger_threshold_entry = tk.Entry(root)
        self.danger_threshold_entry.grid(row=2, column=3, padx=5, pady=5)
        self.danger_threshold_entry.insert(0, "20")  # 默认值

        self.reorder_amount_label = tk.Label(root, text="每次发货订单量:")
        self.reorder_amount_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.reorder_amount_entry = tk.Entry(root)
        self.reorder_amount_entry.grid(row=3, column=1, padx=5, pady=5)
        self.reorder_amount_entry.insert(0, "50")  # 默认值

        self.early_warning_threshold_label = tk.Label(root, text="提前发货阈值:")
        self.early_warning_threshold_label.grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.early_warning_threshold_entry = tk.Entry(root)
        self.early_warning_threshold_entry.grid(row=3, column=3, padx=5, pady=5)
        self.early_warning_threshold_entry.insert(0, "60")  # 默认值

        self.simulation_days_label = tk.Label(root, text="模拟天数:")
        self.simulation_days_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.simulation_days_entry = tk.Entry(root)
        self.simulation_days_entry.grid(row=4, column=1, padx=5, pady=5)
        self.simulation_days_entry.insert(0, "20")  # 默认值

        self.outgoing_range_min_label = tk.Label(root, text="每天出库数 (下限):")
        self.outgoing_range_min_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.outgoing_range_min_entry = tk.Entry(root)
        self.outgoing_range_min_entry.grid(row=7, column=1, padx=5, pady=5)
        self.outgoing_range_min_entry.insert(0, "5")  # 默认值

        self.outgoing_range_max_label = tk.Label(root, text="每天出库数 (上限):")
        self.outgoing_range_max_label.grid(row=7, column=2, padx=5, pady=5, sticky="e")
        self.outgoing_range_max_entry = tk.Entry(root)
        self.outgoing_range_max_entry.grid(row=7, column=3, padx=5, pady=5)
        self.outgoing_range_max_entry.insert(0, "15")  # 默认值

        # 订单到货时间范围输入框
        self.restock_time_min_label = tk.Label(root, text="到货时间 (下限):")
        self.restock_time_min_label.grid(row=9, column=0, padx=5, pady=5, sticky="e")
        self.restock_time_min_entry = tk.Entry(root)
        self.restock_time_min_entry.grid(row=9, column=1, padx=5, pady=5)
        self.restock_time_min_entry.insert(0, "2")  # 默认值

        self.restock_time_max_label = tk.Label(root, text="到货时间 (上限):")
        self.restock_time_max_label.grid(row=9, column=2, padx=5, pady=5, sticky="e")
        self.restock_time_max_entry = tk.Entry(root)
        self.restock_time_max_entry.grid(row=9, column=3, padx=5, pady=5)
        self.restock_time_max_entry.insert(0, "3")  # 默认值

        clicked_items = [0, 0]  # 设置初始的商品价格和商品批发价格
        self.price_label = tk.Label(root, text="商品价格:")
        self.price_label.grid(row=11, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = tk.Entry(root)
        self.price_entry.grid(row=11, column=1, padx=5, pady=5)
        self.price_entry.insert(0, clicked_items[0])  # 默认值

        self.wholesale_price_label = tk.Label(root, text="商品批发价格:")
        self.wholesale_price_label.grid(row=11, column=2, padx=5, pady=5, sticky="e")
        self.wholesale_price_entry = tk.Entry(root)
        self.wholesale_price_entry.grid(row=11, column=3, padx=5, pady=5)
        self.wholesale_price_entry.insert(0, clicked_items[1])  # 默认值

        # 启动仿真按钮
        self.start_button = tk.Button(root, text="开始仿真", command=self.start_simulation)
        self.start_button.grid(row=13, column=0, columnspan=4, padx=5, pady=5)

        # 退出按钮
        exit_button = tk.Button(root, text="退出仿真", command=lambda: self.exit_to_main_menu(root))
        exit_button.grid(row=13, column=1, columnspan=4, padx=5, pady=5)

        # 创建一个Frame来容纳图形区域
        self.graph_frame = tk.Frame(root)
        self.graph_frame.grid(row=14, column=0, columnspan=4, padx=5, pady=5)

        # 在Frame中显示图形
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)  # 增大显示区域
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建最终收入标签
        self.label_benefit_all = tk.Label(root, text="最终收入：0元")
        self.label_benefit_all.grid(row=15, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # 创建最终支出标签
        self.label_expense_all = tk.Label(root, text="最终支出：0元")
        self.label_expense_all.grid(row=15, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

    # 退出仿真模拟并回到主菜单
    def exit_to_main_menu(self, simulation_window):
        if messagebox.askyesno("退出", "确定返回主菜单吗？"):
            simulation_window.destroy()  # 销毁商品信息窗口

    def start_simulation(self):
        """
        启动库存管理模拟仿真

        从输入框获取初始数据，模拟出库操作，更新库存，发起订单等，并生成库存变化的图表
        """
        try:
            # 获取输入的初始数据
            initial_stock = self.get_valid_integer(self.initial_stock_entry.get(), 100)
            danger_threshold = self.get_valid_integer(self.danger_threshold_entry.get(), 20)
            reorder_amount = self.get_valid_integer(self.reorder_amount_entry.get(), 50)
            early_warning_threshold = self.get_valid_integer(self.early_warning_threshold_entry.get(), 60)
            simulation_days = self.get_valid_integer(self.simulation_days_entry.get(), 20)
            outgoing_range_min = self.get_valid_integer(self.outgoing_range_min_entry.get(), 5)
            outgoing_range_max = self.get_valid_integer(self.outgoing_range_max_entry.get(), 15)
            restock_time_min = self.get_valid_integer(self.restock_time_min_entry.get(), 2)
            restock_time_max = self.get_valid_integer(self.restock_time_max_entry.get(), 3)
            price = float(self.price_entry.get())
            wholesale_price = float(self.wholesale_price_entry.get())
            # 创建库存管理系统实例
            inventory = InventorySystem(initial_stock, danger_threshold, reorder_amount, early_warning_threshold, price,
                                        wholesale_price)

            # 打开（或创建）一个文本文件用来记录模拟情况
            with open("../出库/模拟过程记录.txt", "w", encoding="utf-8") as file:
                file.write("模拟过程")

            # 模拟出库流程
            for day in range(1, simulation_days + 1):
                # 打开（或创建）一个文本文件用来记录模拟情况
                with open("../出库/模拟过程记录.txt", "a", encoding="utf-8") as file:
                    file.write(f"\n\n--- 第{day}天 ---")
                # 随机出库量
                outgoing = random.randint(outgoing_range_min, outgoing_range_max)
                inventory.outgoing_goods(outgoing, day, restock_time_min, restock_time_max)
                inventory.process_pending_orders(day)

            # 输出最后的收入与支出
            self.label_benefit_all.config(text=f"最终收入：{sum(inventory.benefit):.2f}元")
            self.label_expense_all.config(text=f"最终支出：{sum(inventory.expense):.2f}元")

            # 绘制库存变化图
            self.figure.clear()
            ax = self.figure.add_subplot(121)
            ax.plot(inventory.stock_history, marker='o', linestyle='-', color='b', label="Stock Level")
            ax.axhline(y=danger_threshold, color='r', linestyle='--', label="Danger Threshold")

            # 标记发货的时间点
            for reorder_day in inventory.reorder_days:
                ax.plot(reorder_day - 1, inventory.stock_history[reorder_day - 1], marker='*', color='g', markersize=10,
                        label="Order Placed")

            ax.set_xlabel("Days")
            ax.set_ylabel("Stock Level")
            ax.set_title("Inventory Level Over Time")
            ax.grid(True)
            # 设置图例位置在图外
            ax.legend(bbox_to_anchor=(1.5, 0.9), loc='upper left')
            # 更新图形
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数值！")

    def get_valid_integer(self, value, default_value):
        """
        获取有效的整数值，如果无法转换，则返回默认值

        :param value: 输入的字符串
        :param default_value: 默认值
        :return: 转换后的整数值
        """
        try:
            return int(value)
        except ValueError:
            return default_value


# 启用仿真模拟
def Simulated_Modeling():
    root = tk.Tk()
    app = InventorySimulationApp(root)
    root.mainloop()


######################################

######################################运行主菜单
if __name__ == "__main__":
    main_menu()
