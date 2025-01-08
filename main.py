#%% 1. Head
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:52:05 2024

@author: vctr23
"""

#%% 2. Imports
import customtkinter as ctk
from src import mainwindow

#%% 3. Main
if __name__ == '__main__':
    root = ctk.CTk()
    app = mainwindow.MainWindow(root)

    root.mainloop()