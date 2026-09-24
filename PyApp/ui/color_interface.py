from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, SubtitleLabel, Slider, SwitchButton, CardWidget

class ColorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ColorInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.titleLabel = TitleLabel("Color Studio", self)
        self.vBoxLayout.addWidget(self.titleLabel)

        self.card = CardWidget(self)
        self.cardLayout = QVBoxLayout(self.card)
        self.cardLayout.setContentsMargins(24, 24, 24, 24)
        self.cardLayout.setSpacing(16)

        # Vibrance
        self.vibLabel = SubtitleLabel("Digital Vibrance (%)", self.card)
        self.vibSlider = Slider(Qt.Orientation.Horizontal, self.card)
        self.vibSlider.setRange(50, 100)
        self.vibSlider.setValue(75)
        self.vibSlider.sliderReleased.connect(self.apply_vibrance)
        
        self.cardLayout.addWidget(self.vibLabel)
        self.cardLayout.addWidget(self.vibSlider)

        # Zero-Bleed
        self.zbLayout = QHBoxLayout()
        self.zbLabel = SubtitleLabel("Kích hoạt 0ms Zero-Bleed", self.card)
        self.zbSwitch = SwitchButton(self.card)
        self.zbLayout.addWidget(self.zbLabel)
        self.zbLayout.addStretch(1)
        self.zbLayout.addWidget(self.zbSwitch)

        self.cardLayout.addLayout(self.zbLayout)
        self.vBoxLayout.addWidget(self.card)

    def apply_vibrance(self):
        from core.nvapi_manager import NvApiManager
        vib = self.vibSlider.value()
        NvApiManager.set_vibrance_percent(vib)

