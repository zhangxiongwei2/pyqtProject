from requests import delete

add_btn_style = """
            QPushButton {
                background-color: #4CAF50;  /* 背景色 */
                color: white;              /* 文字颜色 */
                border-radius: 5px;       /* 圆角 */
                padding: 8px 16px;        /* 内边距 */
                border: 2px solid #45a049; /* 边框 */
            }

            /* 鼠标悬停效果 */
            QPushButton:hover {
                background-color: #45a049;
            }

            /* 按下效果 */
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
delete_btn_style = """
            QPushButton {
                background-color: #FF7F00;  /* 背景色 */
                color: white;              /* 文字颜色 */
                border-radius: 5px;       /* 圆角 */
                padding: 8px 16px;        /* 内边距 */
                border: 2px solid #45a049; /* 边框 */
            }

            /* 鼠标悬停效果 */
            QPushButton:hover {
                background-color: #FF0000;
            }

            /* 按下效果 */
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
setStyleSheet="""
    QHeaderView::section {
        border: none;  # 隐藏表头默认边框
        border-right: 1px solid gray;  # 仅保留右侧分割线
    }
    QTableWidget {
        gridline-color: gray;  # 单元格分割线
    }
"""