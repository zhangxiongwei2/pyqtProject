import pymysql
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QMessageBox, QSplitter, QDialog, QListWidget, QListWidgetItem,
    QTabWidget, QInputDialog, QScrollArea, QProgressBar,
    QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog, QToolTip,
    QToolBar, QStatusBar, QMainWindow, QApplication, QMenu, QRadioButton, QDialogButtonBox, QTableWidget
)
from pandas.core.methods.to_dict import to_dict


# from ui.load_fresh import load_students


class UpdateStudent(QDialog):
    def __init__(self,student_data):
        super().__init__()

        self.setWindowTitle("新增学生信息")
        self.resize(200, 400)
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
        self.student_data = student_data
        self.updated_data = None
        self._init_ui()
        # 初始化ui

    def _init_ui(self):
        cursor = None
        try:
            # 0. 检查连接有效性（新增）
            self.db_connection.ping(reconnect=True)
            self.table = QTableWidget()
            # 1. 获取原始数据（添加空值校验）
            # student_id = self.table.item(row_index, 0).text().strip()
            # name = self.table.item(row_index, 1).text()
            # current_sex = self.table.item(row_index, 2).text()  # 当前性别值
            # age = self.table.item(row_index, 3).text()
            # major = self.table.item(row_index, 4).text()
            if not self.student_data["student_id"]:
                raise ValueError("学号不能为空")
            print(self.student_data["student_id"])
            # ... [保持原有数据获取逻辑不变] ...

            # 2. 创建编辑弹窗（保持原有UI逻辑不变）
            # ... [弹窗创建和数据处理代码] ...

            layout = QVBoxLayout(self)

            # 学号（设为只读）
            lbl_id = QLabel("学号:")
            self.edit_id = QLineEdit(self.student_data["student_id"])
            self.edit_id.setReadOnly(True)  # 学号不可修改
            layout.addWidget(lbl_id)
            layout.addWidget(self.edit_id)

            # 姓名输入框
            lbl_name = QLabel("姓名:")
            self.edit_name = QLineEdit(self.student_data["name"])
            layout.addWidget(lbl_name)
            layout.addWidget(self.edit_name)

            # 性别选择框（关键修改部分）
            sex_group = QGroupBox("性别")  # 修正标题设置
            radio_layout = QVBoxLayout()
            self.radio_male = QRadioButton("男")
            self.radio_female = QRadioButton("女")
            # 设置默认选中状态
            if self.student_data["gender"] == "女":
                self.radio_female.setChecked(True)
            else:
                self.radio_male.setChecked(True)
            radio_layout.addWidget(self.radio_male)
            radio_layout.addWidget(self.radio_female)
            sex_group.setLayout(radio_layout)
            layout.addWidget(sex_group)

            # 年龄输入框
            lbl_age = QLabel("年龄:")
            self.edit_age = QLineEdit(str(self.student_data["age"]))
            layout.addWidget(lbl_age)
            layout.addWidget(self.edit_age)

            # 专业输入框
            lbl_major = QLabel("专业:")
            self.edit_major = QLineEdit(self.student_data["major"])
            layout.addWidget(lbl_major)
            layout.addWidget(self.edit_major)

            # 操作按钮
            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btn_box.accepted.connect(self.accept)
            btn_box.rejected.connect(self.reject)
            layout.addWidget(btn_box)

            if self.exec() == QDialog.DialogCode.Accepted:
                # 3. 使用参数化查询（关键修复点）
                new_name = self.edit_name.text().strip()
                new_sex = "女" if self.radio_female.isChecked() else "男"  # 获取单选状态
                new_age = self.edit_age.text().strip()
                new_major = self.edit_major.text().strip()
                sql = """
                       UPDATE students 
                       SET name=%s, gender=%s, age=%s, major=%s
                       WHERE student_id=%s
                   """
                params = (new_name, new_sex, new_age, new_major, self.student_data["student_id"])

                # 4. 创建新游标并执行
                cursor = self.db_connection.cursor()
                cursor.execute(sql, params)
                print(f"更新影响行数：{cursor.rowcount}")
                self.db_connection.commit()  # 显式提交
                self.updated_data = {
                    "student_id": self.student_data["student_id"],
                    "name": new_name,
                    "gender": new_sex,
                    "age": new_age,
                    "major": new_major
                }


                # 5. 局部刷新界面（保持原有逻辑不变）
                # ... [界面更新代码] ...
                # self.table.item(row_index, 1).setText(new_name)
                # self.table.item(row_index, 2).setText(new_sex)
                # self.table.item(row_index, 3).setText(new_age)
                # self.table.item(row_index, 4).setText(new_major)
        except pymysql.Error as e:
            # 错误处理优化
            if self.db_connection:
                self.db_connection.rollback()
                QMessageBox.critical(self, "数据库错误", f"更新失败: {e}\n错误码: {e.args}")
        except ValueError as ve:
            QMessageBox.warning(self, "输入错误", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "未知错误", f"系统异常: {str(e)}")
        finally:
            # 仅关闭游标，保持连接开启（关键修复点）
            if cursor:
                cursor.close()

