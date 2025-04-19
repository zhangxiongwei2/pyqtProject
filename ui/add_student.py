import pymysql
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QMessageBox, QSplitter, QDialog, QListWidget, QListWidgetItem,
    QTabWidget, QInputDialog, QScrollArea, QProgressBar,
    QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog, QToolTip,
    QToolBar, QStatusBar, QMainWindow, QApplication, QMenu, QRadioButton
)

# from ui.load_fresh import load_students


class AddStudent(QDialog):
    def __init__(self,db_connection=None):
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
        self._init_ui()
    #初始化ui
    def _init_ui(self):
        cursor = None
        student_id = ""
        name = ""
        gender = "男"
        age = ""
        major = ""
        # self.dialog = QDialog()
        # self.dialog.setWindowTitle("新增学生信息")
        layout = QVBoxLayout(self)

        # 学号输入（添加时非只读，编辑时只读）
        lbl_id = QLabel("学号:")
        edit_id = QLineEdit(student_id)
        edit_id.setPlaceholderText("必填")  # 输入提示
        # print(2)
        if student_id:  # 编辑模式时禁止修改学号
            edit_id.setReadOnly(True)
        layout.addWidget(lbl_id)
        layout.addWidget(edit_id)

        # 姓名输入
        lbl_name = QLabel("姓名:")
        edit_name = QLineEdit(name)
        edit_name.setPlaceholderText("必填")
        layout.addWidget(lbl_name)
        layout.addWidget(edit_name)

        # 性别选择（使用局部变量避免污染类属性）
        sex_group = QGroupBox("性别")
        radio_male = QRadioButton("男")
        radio_female = QRadioButton("女")
        radio_male.setChecked(gender == "男")  # 设置默认值
        radio_female.setChecked(gender == "女")
        radio_layout = QVBoxLayout()
        radio_layout.addWidget(radio_male)
        radio_layout.addWidget(radio_female)
        sex_group.setLayout(radio_layout)
        layout.addWidget(sex_group)
        print(3)
        # 年龄输入（数字校验）
        lbl_age = QLabel("年龄:")
        edit_age = QLineEdit(age)
        # edit_age.setValidator(QIntValidator(1, 100, self))  # 限制1-100岁
        layout.addWidget(lbl_age)
        layout.addWidget(edit_age)

        # 专业输入
        lbl_major = QLabel("专业:")
        edit_major = QLineEdit(major)
        layout.addWidget(lbl_major)
        layout.addWidget(edit_major)
        print(4)
        # 按钮操作
        btn_confirm = QPushButton("确定")
        btn_cancel = QPushButton("取消")


        def validate_and_submit():
            # 必填字段校验
            if not edit_id.text().strip():
                QMessageBox.warning(self, "错误", "学号不能为空！")
                edit_id.setFocus()
                return
            if not edit_name.text().strip():
                QMessageBox.warning(self, "错误", "姓名不能为空！")
                edit_name.setFocus()
                return
            # 年龄格式校验
            if edit_age.text() and not edit_age.text().isdigit():
                QMessageBox.warning(self, "格式错误", "年龄必须为整数")
                edit_age.setFocus()
                return
            self.accept()  # 验证通过后关闭对话框

        btn_confirm.clicked.connect(validate_and_submit)
        btn_cancel.clicked.connect(self.reject)

        layout.addWidget(btn_confirm)
        layout.addWidget(btn_cancel)

        # 处理对话框结果
        if self.exec() == QDialog.DialogCode.Accepted:
            # 获取输入值
            try:
                print(5)
                new_id = edit_id.text().strip()
                new_name = edit_name.text().strip()
                new_gender = "女" if radio_female.isChecked() else "男"
                new_age = edit_age.text().strip()
                new_major = edit_major.text().strip()
                print(new_major)
                cursor= self.db_connection.cursor()
                print(6)
                # print(self.db_connection.cursor())
                sql = """
                             INSERT INTO students
                             (student_id, name, gender, age, major)
                             VALUES (%s, %s, %s, %s, %s)
                             """
                params = (
                    new_id,
                    edit_name.text().strip(),
                    "女" if radio_female.isChecked() else "男",
                    int(age_text) if (age_text := edit_age.text().strip()) else None,
                    edit_major.text().strip()
                )
                cursor.execute(sql, params)
                self.db_connection.commit()

                # 刷新界面
                # load_students(self)
                QMessageBox.information(self, "成功", "操作已完成")
                return True
            except Exception as e:
                # self.db_connection.rollback()
                QMessageBox.critical(self, "错误", f"数据库错误: {str(e)}")
            finally:
                if cursor:
                    # print(7)
                    cursor.close()