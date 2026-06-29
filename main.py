"""
main.py - Точка входа в приложение
"""

import sys
import os
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from gui import StegoAnalysisApp
    import tkinter as tk
    
    root = tk.Tk()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    app = StegoAnalysisApp(root)
    root.mainloop()