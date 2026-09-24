from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, SubtitleLabel, ListWidget, LineEdit, PushButton, CardWidget

class ConfigInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ConfigInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.titleLabel = TitleLabel("Cấu Hình Game & App", self)
        self.vBoxLayout.addWidget(self.titleLabel)

        self.hBoxLayout = QHBoxLayout()
        self.vBoxLayout.addLayout(self.hBoxLayout)

        # Games List
        self.gamesCard = CardWidget(self)
        self.gamesLayout = QVBoxLayout(self.gamesCard)
        self.gamesLayout.setContentsMargins(16, 16, 16, 16)
        
        self.gamesTitle = SubtitleLabel("Game (Ép P-Core)", self.gamesCard)
        self.gamesList = ListWidget(self.gamesCard)
        self.gamesList.addItems(["csgo.exe", "valorant.exe", "dota2.exe"])
        
        self.gInput = LineEdit(self.gamesCard)
        self.gInput.setPlaceholderText("Nhập tên tiến trình...")
        self.gBtn = PushButton("Thêm", self.gamesCard)
        self.gLayout = QHBoxLayout()
        self.gLayout.addWidget(self.gInput)
        self.gLayout.addWidget(self.gBtn)

        self.gamesLayout.addWidget(self.gamesTitle)
        self.gamesLayout.addWidget(self.gamesList)
        self.gamesLayout.addLayout(self.gLayout)
        
        self.hBoxLayout.addWidget(self.gamesCard)

        # Background Apps List
        self.appsCard = CardWidget(self)
        self.appsLayout = QVBoxLayout(self.appsCard)
        self.appsLayout.setContentsMargins(16, 16, 16, 16)
        
        self.appsTitle = SubtitleLabel("App Nền (Đẩy E-Core)", self.appsCard)
        self.appsList = ListWidget(self.appsCard)
        self.appsList.addItems(["chrome.exe", "discord.exe", "spotify.exe"])
        
        self.aInput = LineEdit(self.appsCard)
        self.aInput.setPlaceholderText("Nhập tên tiến trình...")
        self.aBtn = PushButton("Thêm", self.appsCard)
        self.aLayout = QHBoxLayout()
        self.aLayout.addWidget(self.aInput)
        self.aLayout.addWidget(self.aBtn)

        self.appsLayout.addWidget(self.appsTitle)
        self.appsLayout.addWidget(self.appsList)
        self.appsLayout.addLayout(self.aLayout)

        self.hBoxLayout.addWidget(self.appsCard)
