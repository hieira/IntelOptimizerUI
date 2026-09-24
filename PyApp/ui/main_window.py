from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon as FIF

from ui.dashboard_interface import DashboardInterface
from ui.processes_interface import ProcessesInterface
from ui.display_interface import DisplayInterface
from ui.color_interface import ColorInterface
from ui.config_interface import ConfigInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        
        # Interfaces
        self.dashboardInterface = DashboardInterface(self)
        self.displayInterface = DisplayInterface(self)
        self.colorInterface = ColorInterface(self)
        self.processesInterface = ProcessesInterface(self)
        self.configInterface = ConfigInterface(self)
        
        self.initNavigation()

    def initNavigation(self):
        self.addSubInterface(self.dashboardInterface, FIF.HOME, "Tổng Quan")
        self.addSubInterface(self.displayInterface, FIF.APPLICATION, "Display & Hz", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.colorInterface, FIF.PALETTE, "Color Studio", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.processesInterface, FIF.SEARCH, "Tiến Trình", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.configInterface, FIF.SETTING, "Cấu Hình", position=NavigationItemPosition.BOTTOM)
        
    def initWindow(self):
        self.resize(1000, 700)
        self.setWindowTitle('Intel Hybrid Optimizer')
        
        # Center window
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
