# %% 1. Head
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:52:05 2024

@author: vctr23
"""

# %% 2. Functions


def center_window(root, window_width):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_height = int((screen_height * window_width)/screen_width)

    x_pos = int(screen_width/2 - window_width/2)
    y_pos = int(screen_height/2 - window_height/2)

    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
