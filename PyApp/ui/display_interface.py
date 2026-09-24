from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, SubtitleLabel, ComboBox, PrimaryPushButton, CardWidget

class DisplayInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DisplayInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.titleLabel = TitleLabel("Display & Hz Studio", self)
        self.vBoxLayout.addWidget(self.titleLabel)

        self.card = CardWidget(self)
        self.cardLayout = QVBoxLayout(self.card)
        self.cardLayout.setContentsMargins(24, 24, 24, 24)
        self.cardLayout.setSpacing(16)

        # Resolution
        self.resLabel = SubtitleLabel("Độ phân giải (Esport 4:3)", self.card)
        self.resCombo = ComboBox(self.card)
        self.resCombo.addItems(["1920x1080 (Native)", "1440x1080 (4:3)", "1280x960 (4:3)"])
        
        self.cardLayout.addWidget(self.resLabel)
        self.cardLayout.addWidget(self.resCombo)

        # Refresh Rate
        self.hzLabel = SubtitleLabel("Tần số quét (Hz)", self.card)
        self.hzCombo = ComboBox(self.card)
        self.hzCombo.addItems(["240 Hz", "144 Hz", "60 Hz"])
        
        self.cardLayout.addWidget(self.hzLabel)
        self.cardLayout.addWidget(self.hzCombo)

        # Apply Button
        self.applyBtn = PrimaryPushButton("Áp dụng thông số Màn Hình", self.card)
        self.applyBtn.clicked.connect(self.apply_resolution)
        self.cardLayout.addWidget(self.applyBtn)

        self.vBoxLayout.addWidget(self.card)

    def apply_resolution(self):
        from core.display_manager import DisplayManager
        res_str = self.resCombo.currentText()
        hz_str = self.hzCombo.currentText()
        
        w, h = 1920, 1080
        if "1440x1080" in res_str:
            w, h = 1440, 1080
        elif "1280x960" in res_str:
            w, h = 1280, 960
            
        hz = 240
        if "144 Hz" in hz_str:
            hz = 144
        elif "60 Hz" in hz_str:
            hz = 60
            
        DisplayManager.apply_resolution(w, h, hz)

