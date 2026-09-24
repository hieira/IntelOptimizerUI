from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, SubtitleLabel, CardWidget, PrimaryPushButton, PushButton, InfoBadge, InfoBadgePosition

from core.cpu_topology import CpuTopology
from core.power_manager import PowerManager

class DashboardInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DashboardInterface")
        self.topology = CpuTopology()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        self.titleLabel = TitleLabel("Tổng Quan Hệ Thống", self)
        self.subtitleLabel = SubtitleLabel(f"{self.topology.name} • {self.topology.physical_cores} Cores ({self.topology.p_cores}P + {self.topology.e_cores}E)", self)
        self.subtitleLabel.setTextColor("#7f7f7f", "#808080")
        
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.addSpacing(24)

        # Cards Layout
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setSpacing(16)
        self.vBoxLayout.addLayout(self.hBoxLayout)

        # Card 1: Power Policy
        self.powerCard = CardWidget(self)
        self.powerLayout = QVBoxLayout(self.powerCard)
        self.powerLayout.setContentsMargins(16, 16, 16, 16)
        
        self.pcTitle = SubtitleLabel("Kernel Power Policy", self.powerCard)
        self.pcDesc1 = SubtitleLabel("Plan: Ultra Performance", self.powerCard)
        self.pcDesc1.setStyleSheet("font-size: 13px; color: gray;")
        self.pcBtn = PrimaryPushButton("Tối ưu Power Policy", self.powerCard)
        self.pcBtn.clicked.connect(self.on_power_click)
        
        self.powerLayout.addWidget(self.pcTitle)
        self.powerLayout.addWidget(self.pcDesc1)
        self.powerLayout.addStretch(1)
        self.powerLayout.addWidget(self.pcBtn)
        self.hBoxLayout.addWidget(self.powerCard)

        # Card 2: Affinity
        self.affCard = CardWidget(self)
        self.affLayout = QVBoxLayout(self.affCard)
        self.affLayout.setContentsMargins(16, 16, 16, 16)
        
        self.acTitle = SubtitleLabel("Điều Phối CPU Affinity", self.affCard)
        self.acDesc1 = SubtitleLabel(f"P-Core Mask: {hex(self.topology.p_core_mask)}", self.affCard)
        self.acDesc1.setStyleSheet("font-size: 13px; color: #ffb900;")
        self.acDesc2 = SubtitleLabel(f"E-Core Mask: {hex(self.topology.e_core_mask)}", self.affCard)
        self.acDesc2.setStyleSheet("font-size: 13px; color: #00bcf2;")
        self.acBtn = PrimaryPushButton("Quick Apply Affinity", self.affCard)
        self.acBtn.clicked.connect(self.on_affinity_click)
        
        self.affLayout.addWidget(self.acTitle)
        self.affLayout.addWidget(self.acDesc1)
        self.affLayout.addWidget(self.acDesc2)
        self.affLayout.addStretch(1)
        self.affLayout.addWidget(self.acBtn)
        self.hBoxLayout.addWidget(self.affCard)
        
        # Card 3: Display
        self.dispCard = CardWidget(self)
        self.dispLayout = QVBoxLayout(self.dispCard)
        self.dispLayout.setContentsMargins(16, 16, 16, 16)
        
        self.dcTitle = SubtitleLabel("Display & Color Status", self.dispCard)
        self.dcDesc = SubtitleLabel("Color Engine: Sẵn sàng", self.dispCard)
        self.dcDesc.setStyleSheet("font-size: 13px; color: gray;")
        self.dcBtn = PushButton("Mở Display Studio", self.dispCard)
        
        self.dispLayout.addWidget(self.dcTitle)
        self.dispLayout.addWidget(self.dcDesc)
        self.dispLayout.addStretch(1)
        self.dispLayout.addWidget(self.dcBtn)
        self.hBoxLayout.addWidget(self.dispCard)
        
        # Card 4: RAM Optimizer
        self.ramCard = CardWidget(self)
        self.ramLayout = QVBoxLayout(self.ramCard)
        self.ramLayout.setContentsMargins(16, 16, 16, 16)
        
        self.rcTitle = SubtitleLabel("Memory Optimizer", self.ramCard)
        self.rcDesc = SubtitleLabel("Tình trạng: Phân tích...", self.ramCard)
        self.rcDesc.setStyleSheet("font-size: 13px; color: #107c10;")
        self.rcBtn = PrimaryPushButton("Dọn Dẹp RAM", self.ramCard)
        self.rcBtn.clicked.connect(self.on_ram_click)
        
        self.ramLayout.addWidget(self.rcTitle)
        self.ramLayout.addWidget(self.rcDesc)
        self.ramLayout.addStretch(1)
        self.ramLayout.addWidget(self.rcBtn)
        self.hBoxLayout.addWidget(self.ramCard)
        
        # Load initial RAM
        self.update_ram_status()
        from PySide6.QtCore import QTimer
        self.ramTimer = QTimer(self)
        self.ramTimer.timeout.connect(self.update_ram_status)
        self.ramTimer.start(1500)

    def update_ram_status(self):
        import psutil
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024**3)
        total_gb = mem.total / (1024**3)
        self.rcDesc.setText(f"Đang dùng: {used_gb:.1f}GB / {total_gb:.1f}GB ({mem.percent}%)")

    def on_power_click(self):
        success, msg = PowerManager.apply_optimal_policy()
        self.pcDesc1.setText(msg)
        
    def on_affinity_click(self):
        from core.affinity_manager import ProcessAffinityManager
        count = ProcessAffinityManager.quick_apply(self.topology.p_core_mask, self.topology.e_core_mask)
        self.acDesc1.setText(f"Đã xử lý {count} tiến trình")

    def on_ram_click(self):
        import threading
        threading.Thread(target=self._run_reduce_memory, daemon=True).start()

    def _run_reduce_memory(self):
        from core.memory_manager import MemoryManager
        MemoryManager.reduce_memory()
        self.update_ram_status()
        from PySide6.QtCore import QTimer
        self.ramTimer = QTimer(self)
        self.ramTimer.timeout.connect(self.update_ram_status)
        self.ramTimer.start(1500)
        self.rcDesc.setText(self.rcDesc.text() + " - Đã dọn dẹp sâu!")

