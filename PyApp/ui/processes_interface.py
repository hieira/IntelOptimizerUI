from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from qfluentwidgets import TitleLabel, TableWidget, PrimaryPushButton

from core.affinity_manager import ProcessAffinityManager

class ProcessesInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ProcessesInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.titleLabel = TitleLabel("Tiến Trình Đang Chạy", self)
        self.vBoxLayout.addWidget(self.titleLabel)

        self.refreshBtn = PrimaryPushButton("Làm mới danh sách", self)
        self.refreshBtn.clicked.connect(self.load_data)
        self.vBoxLayout.addWidget(self.refreshBtn)

        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Tên Tiến Trình", "CPU (%)", "Affinity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vBoxLayout.addWidget(self.table)
        
        # Initial load
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        procs = ProcessAffinityManager.get_process_list()
        self.table.setRowCount(len(procs))
        
        for i, proc in enumerate(procs):
            from PySide6.QtWidgets import QTableWidgetItem
            self.table.setItem(i, 0, QTableWidgetItem(str(proc["pid"])))
            self.table.setItem(i, 1, QTableWidgetItem(proc["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(str(proc["cpu"])))
            self.table.setItem(i, 3, QTableWidgetItem(proc["affinity"]))
