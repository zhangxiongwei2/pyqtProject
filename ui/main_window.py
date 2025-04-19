import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
    QMessageBox, QFileDialog, QToolBar, QStatusBar
)
from ui.student_tab import StudentTab
from ui.teacher_tab import TeacherTab

class StudentManage(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("学生管理系统")
        self.setGeometry(100, 100, 1000, 800)
        """初始化ui"""
        self._init_ui()


    def _init_ui(self):

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        self.tab_widget = QTabWidget()
        #self.tab_widget.currentChanged.connect(self._on_tab_changed)  # 连接标签页切换事件
        main_layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.student_tab = StudentTab(self)
        self.teacher_tab = TeacherTab(self)
        # self.chapter_outline_tab = ChapterOutlineTab(self)
        # self.chapter_tab = ChapterTab(self)

        # 添加标签页
        self.tab_widget.addTab(self.student_tab, "学生管理")
        self.tab_widget.addTab(self.teacher_tab, "老师管理")



# if __name__ == "__main__":
#
#
#     app = QApplication(sys.argv)
#     window = StudentManage()
#     window.show()
#     sys.exit(app.exec())
