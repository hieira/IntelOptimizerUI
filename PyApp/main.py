import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
    sys.exit()

from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme

from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set PySide6-Fluent-Widgets theme
    setTheme(Theme.DARK)
    
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())
