import sys
import os
import argparse
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from qasync import QEventLoop, QApplication as QAsyncApplication
from ui.main_window import StudentManage
# from ui.components import ThemeManager

async def main():
    """主函数"""

    # 创建应用程序
    app = QAsyncApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 创建主窗口
    window = StudentManage()

    # 设置主题
    # if args.dark:
    #     theme_manager = ThemeManager(app)
    #     theme_manager.set_theme(ThemeManager.DARK_THEME)

    # 显示窗口
    window.show()


    # 运行应用程序
    with loop:
        return loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
