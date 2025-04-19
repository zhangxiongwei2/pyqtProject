import pandas as pd
import pymysql
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QMessageBox, QSplitter, QDialog, QListWidget, QListWidgetItem,
    QTabWidget, QInputDialog, QScrollArea, QProgressBar,
    QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog, QToolTip,
    QToolBar, QStatusBar, QMainWindow, QApplication, QMenu, QRadioButton
)
import os
# from ui.load_fresh import load_students


class BatchImport(QDialog):
    def __init__(self,db_connection=None):
        super().__init__()

        self.setWindowTitle("批量导入")
        self.resize(600, 400)
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

    # 初始化ui
    def _init_ui(self):
        self.list_widget = QListWidget()

        btn_select_files = QPushButton("选择文件")
        btn_select_dir = QPushButton("选择文件夹")
        btn_delete = QPushButton("删除选中")
        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")

        # 主布局
        top_btn_layout = QHBoxLayout()
        top_btn_layout.addWidget(btn_select_files)
        top_btn_layout.addWidget(btn_select_dir)
        top_btn_layout.addWidget(btn_delete)

        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(btn_ok)
        bottom_btn_layout.addWidget(btn_cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_btn_layout)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(bottom_btn_layout)

        self.setLayout(main_layout)

        btn_select_files.clicked.connect(self.select_files)
        btn_select_dir.clicked.connect(self.select_directory)
        btn_delete.clicked.connect(self.delete_selected)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        if self.exec() == QDialog.DialogCode.Accepted:
            selected_files = self.get_selected_files()
            if selected_files:
                try:
                    self.batch_import_from_files(selected_files)
                    # self.load_students()  # 刷新表格
                    QMessageBox.information(self, "成功", f"成功导入{len(selected_files)}个文件的数据")
                    return True
                except Exception as e:
                    self.db_connection.rollback()  # 回滚事务
                    QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
            else:
                QMessageBox.warning(self, "提示", "请先选择要导入的文件")

    def batch_import_from_files(self, file_paths: list):
        """批量导入文件到数据库"""
        cursor =None
        try:
            cursor = self.db_connection.cursor()

            # 构建基础SQL
            sql = """
               INSERT INTO students 
               (student_id, name, gender, age, major)
               VALUES (%s, %s, %s, %s, %s)
               """

            # 统计成功数量
            total_inserted = 0

            for file_path in file_paths:
                # 根据文件类型读取数据
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    raise ValueError("不支持的文件格式，仅支持.xlsx和.csv")

                # 数据验证
                required_columns = ['学号', '姓名', '性别', '年龄', '专业']
                if not all(col in df.columns for col in required_columns):
                    missing = [col for col in required_columns if col not in df.columns]
                    raise ValueError(f"文件缺少必要列: {', '.join(missing)}")

                # 转换为元组数据
                data = [
                    (row['学号'], row['姓名'], row['性别'], row['年龄'], row['专业'])
                    for _, row in df.iterrows()
                ]

                # 批量插入
                cursor.executemany(sql, data)
                total_inserted += len(data)

            # 提交事务
            self.db_connection.commit()
            print(f"成功插入{total_inserted}条记录")

        except pymysql.Error as e:
            raise Exception(f"数据库错误: {str(e)}")
        except pd.errors.ParserError:
            raise ValueError("文件解析错误，请检查文件格式")
        except Exception as e:
            raise
        finally:
            if cursor:
                cursor.close()

    def select_files(self):
        """选择多个文件"""
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", "所有文件 (*)")
        if files:
            for path in files:
                self._add_file_to_list(path)

    def select_directory(self):
        """选择文件夹并添加所有文件"""
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if directory:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    self._add_file_to_list(file_path)
    def delete_selected(self):
        """删除选中的列表项"""
        for item in reversed(self.list_widget.selectedItems()):
            self.list_widget.takeItem(self.list_widget.row(item))


    def _add_file_to_list(self, file_path):
        """将文件添加到列表（避免重复）"""
        if not self._is_file_exists(file_path):
            item = QListWidgetItem(os.path.basename(file_path))
            item.setToolTip(file_path)  # 悬停显示完整路径
            item.setData(Qt.ItemDataRole.UserRole, file_path)  # 存储完整路径
            self.list_widget.addItem(item)


    def _is_file_exists(self, file_path):
        """检查文件是否已存在列表中"""
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                return True
        return False


    def get_selected_files(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]