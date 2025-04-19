import pymysql
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QSpinBox, QDoubleSpinBox, QMessageBox, QSplitter, QFileDialog, QProgressBar,
    QDialog, QInputDialog, QTableWidget, QHeaderView, QTableWidgetItem
)

from page_style.setstyle import setStyleSheet, add_btn_style, delete_btn_style
from ui.student_count import TeacherPieChart


class TeacherTab(QWidget):
    """学生管理标签页"""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.db_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1qaz2wsx',
            database='student_db',
            charset='utf8mb4',  # 支持所有 Unicode 字符
            cursorclass=pymysql.cursors.DictCursor,  # 返回字典格式结果
            autocommit=False,  # 手动控制事务提交
            connect_timeout=10,  # 连接超时时间（秒）
            read_timeout=30  # 查询超时时间
        )

        # 初始化UI
        self._init_ui()
        self.load_students()

    def _init_ui(self):
        """初始化UI"""
        """初始化UI"""
        # 创建主布局
        # 布局

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)
        # self.main_widget.setLayout()

        # self.edit_student_id = QLineEdit()
        # self.edit_student_id.setPlaceholderText("请输入学号搜索...")
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("请输入姓名搜索...")

        # 表格数据字段显示
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        headers = ['姓名', '性别', '专业', '电话','操作']
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(40)
        header.setStyleSheet(setStyleSheet)

        # 按钮
        # self.btn_add = QPushButton("新增")
        # self.btn_add.setStyleSheet(add_btn_style)
        # self.btn_pd = QPushButton("批量导入")
        # self.btn_pd.setStyleSheet(add_btn_style)

        self.btn_search = QPushButton("查询")
        self.btn_search.setStyleSheet(add_btn_style)
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setStyleSheet(add_btn_style)

        # 查询表单布局
        self.form_layout = QFormLayout()
        # self.form_layout.addWidget(QLabel("学号:"))
        # self.form_layout.addRow(self.edit_student_id)
        # self.form_layout.addWidget(QLabel("姓名:"))
        self.form_layout.addWidget(self.student_name)
        self.form_layout.addRow(self.student_name)

        # 按钮布局
        self.btn_layout = QHBoxLayout()
        # self.btn_layout.addWidget(self.btn_add)
        #
        # self.btn_layout.addWidget(self.btn_pd)
        self.btn_layout.addWidget(self.btn_search)
        self.btn_layout.addWidget(self.btn_clear)

        main_layout.addLayout(self.form_layout)
        main_layout.addLayout(self.btn_layout)
        main_layout.addWidget(self.table)

        # 绑定信号事件
        # self.btn_add.clicked.connect(self.add_dialog)
        # self.btn_pd.clicked.connect(self.show_batch_import_dialog)
        self.btn_search.clicked.connect(self.search_student)
        self.btn_clear.clicked.connect(self.clear_inputs)
    def load_students(self):
        try:
            # 恢复数据库查询
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT name, gender, major,telephone FROM teachers")
                result = cursor.fetchall()

                # 清空表格并重置
                self.table.setRowCount(0)
                self.table.setColumnCount(5)  # 5数据列+1操作列
                self.table.setHorizontalHeaderLabels(['姓名', '性别', '专业', '电话','操作'])

                # 填充数据行
                for row_idx, student in enumerate(result):
                    self.table.insertRow(row_idx)  # 动态添加行

                    # 填充前5列数据
                    for col_idx in range(4):
                        data = str(student.get(list(student.keys())[col_idx], ""))
                        item = QTableWidgetItem(data)
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 禁止编辑
                        self.table.setItem(row_idx, col_idx, item)

                    # 添加操作按钮（修复闭包变量问题）
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(5, 2, 5, 2)

                    # 编辑按钮：使用默认参数固定当前row_idx
                    btn_edit = QPushButton("统计")
                    btn_edit.clicked.connect(lambda _, r=row_idx:self.zhanbi_student())
                    btn_edit.setStyleSheet(add_btn_style)

                    # 删除按钮：移除特殊空格字符
                    # btn_delete = QPushButton("删除")
                    # # btn_delete.clicked.connect(lambda _, r=row_idx: self.delete_student(r))
                    # btn_delete.setStyleSheet(delete_btn_style)

                    layout.addWidget(btn_edit)
                    # layout.addWidget(btn_delete)
                    self.table.setCellWidget(row_idx, 4, container)  # 第5列为操作列

                self.db_connection.commit()

        except pymysql.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "数据库错误", f"加载失败: {e}\n错误码: {e.args}")
        except Exception as e:
            QMessageBox.warning(self, "运行时错误", f"发生意外错误: {str(e)}")
    def clear_inputs(self):
        """清空所有输入框内容"""
        self.student_name.clear()  # 学号输入框
        self.search_student()
    def search_student(self):
        keyword = self.student_name.text()
        try:
            with self.db_connection.cursor() as cursor:
                sql = """SELECT name, gender, major,telephone FROM teachers 
                        WHERE  name LIKE %s"""
                params= f"%{keyword}%"
                cursor.execute(sql,
                    params)
                result = cursor.fetchall()
                print(result,sql)
                self.db_connection.commit()
                self.table.setRowCount(len(result))
                self.table.setRowCount(0)
                # for row, student in enumerate(result):
                #     for col, data in enumerate(student):
                #         self.table.setItem(row, col, QTableWidgetItem(str(data)))
                for row_idx, student in enumerate(result):
                    self.table.insertRow(row_idx)  # 动态添加行

                    # 填充前5列数据
                    for col_idx in range(4):
                        data = str(student.get(list(student.keys())[col_idx], ""))
                        item = QTableWidgetItem(data)
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 禁止编辑
                        self.table.setItem(row_idx, col_idx, item)
                        container = QWidget()
                        layout = QHBoxLayout(container)
                        layout.setContentsMargins(5, 2, 5, 2)

                        # 编辑按钮：使用默认参数固定当前row_idx
                        btn_edit = QPushButton("统计")
                        btn_edit.clicked.connect(lambda _, r=row_idx: self.zhanbi_student())
                        btn_edit.setStyleSheet(add_btn_style)

                        # 删除按钮：移除特殊空格字符
                        # btn_delete = QPushButton("删除")
                        # btn_delete.clicked.connect(lambda _, r=row_idx: self.delete_student(r))
                        # btn_delete.setStyleSheet(delete_btn_style)

                        layout.addWidget(btn_edit)
                        # layout.addWidget(btn_delete)
                        self.table.setCellWidget(row_idx, 4, container)

        except Exception as e:
                QMessageBox.warning(self, "错误", f"查询失败: {str(e)}")


    def zhanbi_student(self):

        # print(student_data)
        dialog = TeacherPieChart(self)
        dialog.exec()
