from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import TitleLabel, SubtitleLabel, Slider, SwitchButton, CardWidget

from core.color_manager import ColorManager
from core.zero_bleed_manager import ZeroBleedManager

class ColorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ColorInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.titleLabel = TitleLabel("🎨 Color Studio", self)
        self.vBoxLayout.addWidget(self.titleLabel)

        self.card = CardWidget(self)
        self.cardLayout = QVBoxLayout(self.card)
        self.cardLayout.setContentsMargins(24, 24, 24, 24)
        self.cardLayout.setSpacing(16)

        # Helper function to create sliders
        self.sliders = {}
        self.create_slider("Vibrance", "Digital Vibrance (%)", 50, 100, 75, 1)
        self.create_slider("BlackEqualizer", "Black Equalizer / Shadow Boost", 50, 200, 100, 100) # 0.5 to 2.0
        self.create_slider("Brightness", "Brightness", -50, 50, 0, 100) # -0.5 to 0.5
        self.create_slider("Contrast", "Contrast", 50, 150, 100, 100) # 0.5 to 1.5
        self.create_slider("RGain", "Red Gain", 50, 150, 100, 100)
        self.create_slider("GGain", "Green Gain", 50, 150, 100, 100)
        self.create_slider("BGain", "Blue Gain", 50, 150, 100, 100)

        # Zero-Bleed
        self.zbLayout = QHBoxLayout()
        self.zbLabel = SubtitleLabel("Kích hoạt 0ms Zero-Bleed (Auto Game Detect)", self.card)
        self.zbSwitch = SwitchButton(self.card)
        self.zbSwitch.checkedChanged.connect(self.toggle_zero_bleed)
        self.zbLayout.addWidget(self.zbLabel)
        self.zbLayout.addStretch(1)
        self.zbLayout.addWidget(self.zbSwitch)

        self.cardLayout.addLayout(self.zbLayout)
        self.vBoxLayout.addWidget(self.card)

    def create_slider(self, key, text, min_val, max_val, default_val, divider):
        layout = QHBoxLayout()
        label = SubtitleLabel(text, self.card)
        
        slider = Slider(Qt.Orientation.Horizontal, self.card)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        
        val_label = QLabel(str(default_val / divider), self.card)
        
        slider.valueChanged.connect(lambda v, l=val_label, d=divider: l.setText(str(v / d)))
        slider.sliderReleased.connect(self.apply_settings)
        
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(slider)
        layout.addWidget(val_label)
        
        self.cardLayout.addLayout(layout)
        self.sliders[key] = (slider, divider)

    def apply_settings(self):
        vib = self.sliders["Vibrance"][0].value()
        gamma = self.sliders["BlackEqualizer"][0].value() / 100.0
        brightness = self.sliders["Brightness"][0].value() / 100.0
        contrast = self.sliders["Contrast"][0].value() / 100.0
        r_gain = self.sliders["RGain"][0].value() / 100.0
        g_gain = self.sliders["GGain"][0].value() / 100.0
        b_gain = self.sliders["BGain"][0].value() / 100.0
        
        if self.zbSwitch.isChecked():
            ZeroBleedManager.set_profile(
                brightness=brightness, contrast=contrast, gamma=gamma,
                r_gain=r_gain, g_gain=g_gain, b_gain=b_gain, vibrance=vib
            )
        else:
            ColorManager.apply_color_profile(
                brightness=brightness, contrast=contrast, gamma=gamma,
                r_gain=r_gain, g_gain=g_gain, b_gain=b_gain, vibrance=vib
            )

    def toggle_zero_bleed(self, checked):
        if checked:
            ColorManager.restore_default() # Restore immediately, zero-bleed takes over when game is active
            ZeroBleedManager.start()
            self.apply_settings()
        else:
            ZeroBleedManager.stop()
            self.apply_settings()
