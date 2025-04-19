import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDialog
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtGui import QPainter, QColor,QCursor
from PyQt6.QtCore import Qt, QPoint
import pymysql
from collections import defaultdict

class TeacherPieChart(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("教师学生分布饼图（带悬停提示）")
        self.setGeometry(100, 100, 800, 600)
        self.db_config = {
        "host": "localhost",
        "user": "root",
        "password": "1qaz2wsx",
        "database": "student_db",
        "charset": "utf8mb4"
    }
        # 初始化数据
        self.teachers = defaultdict(int)
        self.major_mapping = {
            'cs': '计算机科学',
            '计算机': '计算机科学',
            'computer science': '计算机科学',
            'ee': '电子信息工程',
            '电子工程': '电子信息工程',
            'electronic': '电子信息工程'
        }
        self.fetch_data()
        self.init_ui()
        self.setup_hover()

    def init_ui(self):
        # 创建饼图系列
        self.series = QPieSeries()
        self.series.setHoleSize(0.35)

        # 添加数据切片（增加异常处理）
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                  QColor(255, 255, 0), QColor(255, 0, 255)]

        try:
            for i, (name, count) in enumerate(self.teachers.items()):
                slice = QPieSlice(f"{name} ({count}人)", count)
                slice.setColor(colors[i % len(colors)])
                slice.setLabelVisible(True)
                self.series.append(slice)
        except Exception as e:
            print(f"初始化切片时出错: {str(e)}")
            return

        # 创建图表
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("教师学生数量分布")
        self.chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 创建信息显示标签
        self.info_label = QLabel(self.chart_view)  # 父组件改为图表视图
        self.info_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 220);
                border: 1px solid #666;
                padding: 5px;
                border-radius: 3px;
                min-width: 120px;
            }
        """)
        self.info_label.hide()
        self.info_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 设置主布局
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)


    def setup_hover(self):
        # 安全连接信号
        for slice1 in self.series.slices():
            try:
                slice1.hovered.disconnect()  # 先断开可能存在的旧连接
            except:
                pass
            slice1.hovered.connect(self.on_slice_hovered)

    def on_slice_hovered(self, state):
        try:
            slice = self.sender()
            if not isinstance(slice, QPieSlice):
                return

            if state:
                # 计算数值
                total = sum(self.teachers.values())
                percentage = (slice.value() / total) * 100

                # 更新标签内容
                self.info_label.setText(
                    f"{slice.label()}\n"
                    f"精确数量: {int(slice.value())}\n"
                    f"占比: {percentage:.1f}%"
                )

                # 获取相对图表视图的坐标
                cursor_pos = self.chart_view.mapFromGlobal(QCursor.pos())
                self.info_label.move(cursor_pos + QPoint(20, 20))
                self.info_label.show()

                # 安全设置突出效果
                slice.setExploded(True)
                slice.setLabelVisible(True)
            else:
                self.info_label.hide()
                slice.setExploded(False)

        except Exception as e:
            print(f"处理悬停事件时出错: {str(e)}")
            self.info_label.hide()

    def normalize_major(self, raw_major):
        """标准化专业名称"""
        if not raw_major:
            return '未分类'

        # 清洗处理步骤
        clean_major = raw_major.strip().lower()  # 转小写并去空格
        # print(clean_major)
        for key, value in self.major_mapping.items():
            if key in clean_major:
                return value
        return clean_major.capitalize()

    def fetch_data(self):
        """从数据库获取并处理数据"""
        try:
            with pymysql.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    # 获取教师信息（包含专业）
                    teacher_data = self._fetch_teachers(cursor)

                    # 获取学生专业分布
                    student_stats = self._fetch_students(cursor)

                    # 生成最终结果
                    self._generate_result(teacher_data, student_stats)

        except pymysql.Error as e:
            print(f"数据库操作失败: {e}")
            raise

    def _fetch_teachers(self, cursor):
        """获取教师专业信息"""
        cursor.execute("""
            SELECT name, major 
            FROM teachers
            WHERE major IS NOT NULL
        """)
        return {
            name: self.normalize_major(major)
            for name, major in cursor.fetchall()
        }

    def _fetch_students(self, cursor):
        """统计学生专业分布"""
        cursor.execute("""
            SELECT 
                TRIM(major) AS clean_major,
                COUNT(*) AS total 
            FROM students
            WHERE major IS NOT NULL
            GROUP BY clean_major
        """)

        stats = defaultdict(int)
        for raw_major, count in cursor.fetchall():
            normalized = self.normalize_major(raw_major)
            stats[normalized] += count
        # print(stats)
        return stats

    def _generate_result(self, teacher_data, student_stats):
        """生成教师-学生人数对应关系"""
        # print(teacher_data)
        self.teachers = {
            teacher: student_stats.get(major, 0)
            for teacher, major in teacher_data.items()
        }

