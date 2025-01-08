# %% 1. Header
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:52:05 2024

@author: vctr23
"""

# %% 2. Imports
import io
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image

# %% 3. Classes


class MainWindow():
    def __init__(self, root):
        self.root = root
        self.root.title("PySic IDE")
        self.root.geometry("1100x700")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=10)
        self.root.grid_rowconfigure(2, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=20)

        self.create_ctk_menu()
        self.create_sidebar()
        self.create_main_area()
        self.create_console()

        self.root.bind("<Control-o>", self.open_file)
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-c>", self.copy_text)  
        self.root.bind("<Control-x>", self.cut_text)   
        self.root.bind("<Control-v>", self.paste_text)

    def create_ctk_menu(self):
        """Creates a menu bar using CustomTkinter buttons."""
        self.menu_frame = ctk.CTkFrame(self.root, fg_color="gray14")
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        file_button = ctk.CTkButton(
            self.menu_frame, text="File", command=self.show_file_menu, fg_color="gray14",
            width=20, height=20
        )
        file_button.pack(side="left", padx=10)

        edit_button = ctk.CTkButton(
        self.menu_frame, text="Edit", command=self.show_edit_menu, fg_color="gray14",
        width=20, height=20
        )
        edit_button.pack(side="left", padx=10)

        help_button = ctk.CTkButton(
            self.menu_frame, text="Help", command=self.show_help_menu, fg_color="gray14",
            width=20, height=20
        )
        help_button.pack(side="left")

    def show_file_menu(self):
        """Shows the file menu options."""
        file_menu = tk.Menu(self.root, tearoff=0, bg="gray14", fg="white")
        file_menu.add_command(label="Open File", command=lambda: self.open_file(None))
        file_menu.add_command(label="Save File", command=lambda: self.save_file(None))
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        file_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def show_edit_menu(self):
        """Shows the edit menu options (Copy, Cut, Paste)."""
        edit_menu = tk.Menu(self.root, tearoff=0, bg="gray14", fg="white")
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())


    def show_help_menu(self):
        """Shows the help menu options."""
        help_menu = tk.Menu(self.root, tearoff=0, bg="gray14", fg="white")
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        help_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def create_sidebar(self):
        """Creates the file tree view on the left side."""
        self.sidebar = ttk.Frame(self.root)
        self.sidebar.grid(row=1, column=0, rowspan=2, sticky="nswe")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="gray10",   
            foreground="white",   
            fieldbackground="gray14", 
            highlightthickness=0, 
            rowheight=25      
        )
        style.map(
            "Treeview",
            background=[("selected", "gray30")],  
            foreground=[("selected", "white")]
        )


        self.file_tree = ttk.Treeview(self.sidebar, style="Treeview")
        self.file_tree.heading("#0", text="Files", anchor="w")
        self.file_tree.grid(row=0, column=0, sticky="nswe")

        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.populate_file_tree(os.getcwd())

        self.file_tree.bind("<Double-1>", self.on_file_double_click)

    def on_file_double_click(self, event):
        """Maneja el doble clic en el Treeview para abrir el archivo."""
        selected_item = self.file_tree.selection()
        if selected_item:
            item = selected_item[0]
            file_path = self.file_tree.item(item, "values")[0]

            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding="utf-8") as file:
                    content = file.read()

                self.add_new_tab(os.path.basename(file_path))

                current_tab = self.notebook.tabs()[-1]
                self.notebook.select(current_tab)

                frame = self.notebook.nametowidget(current_tab)
                for widget in frame.winfo_children():
                    if isinstance(widget, ctk.CTkTextbox):
                        widget.insert("1.0", content)

    def populate_file_tree(self, path):
        """Populate the file tree with files and directories, including subdirectories."""
        for item in os.listdir(path):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                # Insert the directory into the tree
                node = self.file_tree.insert(
                    "", "end", text=item, open=False, values=(abs_path,))
                # Recursively populate the subdirectories
                self.populate_file_tree_recursively(abs_path, node)
            else:
                self.file_tree.insert("", "end", text=item, values=(abs_path,))

    def populate_file_tree_recursively(self, path, parent_node):
        """Recursively populate the file tree with subdirectories."""
        for item in os.listdir(path):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                # Insert the directory into the tree under the parent node
                node = self.file_tree.insert(
                    parent_node, "end", text=item, open=False, values=(abs_path,))
                # Recurse into the subdirectory
                self.populate_file_tree_recursively(abs_path, node)
            else:
                self.file_tree.insert(parent_node, "end", text=item, values=(abs_path,))

    def create_main_area(self):
        """Crea el área principal con un notebook y un botón de ejecución."""
        self.main_area = ttk.Frame(self.root)
        self.main_area.grid(row=1, column=1, sticky="nswe")

        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=0)
        self.main_area.grid_columnconfigure(1, weight=1)

        self.run_button_image = Image.open("assets\\play_arrow.png")
        self.run_button = ctk.CTkButton(
            self.main_area, command=lambda: self.run_current_code(None), width=50,
            image= ctk.CTkImage(dark_image=self.run_button_image), text=""
        )
        self.run_button.grid(row=0, column=1, sticky="e")

        style = ttk.Style(self.root)
        style.configure(
            "TNotebook",
            background="gray20",  
            foreground="white"  
        )

        style.configure(
            "TNotebook.Tab",
            background="gray25", 
            foreground="white", 
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", "gray35")], 
            foreground=[("selected", "white")] 
        )

        self.line_canvas = tk.Canvas(self.main_area, width=30, bg="gray20")
        self.line_canvas.grid(row=1, column=0, sticky="ns")

        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.grid(row=1, column=1, sticky="nswe")

        self.add_new_tab("Untitled")

        self.notebook.bind("<Button-2>", self.close_tab)
        self.root.bind("<Control-w>", self.close_tab)
        self.root.bind("<Control-r>", self.run_current_code)

    def update_line_numbers(self, event=None):
        """Actualiza los números de línea en el canvas."""
        text_widget = self.get_current_text_widget()
        if not text_widget:
            return

        self.line_canvas.delete("all")
        i = text_widget.index("@0,0") 

        while True:
            dline_info = text_widget.dlineinfo(i)
            if dline_info is None: 
                break

            x = dline_info[0]
            y = dline_info[1]
            line_number = str(i).split(".")[0]
            self.line_canvas.create_text(
               x + 10, y + 30, anchor="nw", text=line_number, font=("Cascadia code", 10), fill="white")
            i = text_widget.index(f"{i}+1line") 

    def add_new_tab(self, title):
        """Adds a new tab to the notebook."""
        frame = ttk.Frame(self.notebook)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        text_widget = ctk.CTkTextbox(frame, wrap="none", font=("Cascadia code", 12))
        text_widget.grid(row=0, column=0, sticky="nswe")

        text_widget.bind("<KeyRelease>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<MouseWheel>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<Button-1>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<Motion>", lambda e: self.update_line_numbers(e))

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.notebook.add(frame, text=title)

    def close_tab(self, event):
        """Cerrar la pestaña cuando se haga clic en la rueda del ratón (Button-2)."""
        tab_id = self.notebook.index("@%d,%d" % (event.x, event.y))
        if tab_id is not None:
            self.notebook.forget(tab_id)

    def sync_scroll(self, event, text_widget):
        """Sincroniza el scroll entre el texto y el canvas de números de línea."""
        text_widget.yview_scroll(-1 * int(event.delta / 120), "units")
        self.update_line_numbers()

    def get_current_text_widget(self):
        """Returns the CTkTextbox of the currently selected tab."""
        current_tab = self.notebook.select()
        if current_tab:
            frame = self.notebook.nametowidget(current_tab)
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkTextbox):
                    return widget
        return None


    def run_current_code(self, event=None):
        """Runs the Python code from the current tab."""
        text_widget = self.get_current_text_widget()
        if text_widget:
            code = text_widget.get("1.0", "end-1c")
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                exec(code, globals())
                output = sys.stdout.getvalue()
                self.console_output.insert(
                    "end", f"Output:\n{output}\n", "output")
            except Exception as e:
                error = str(e)
                self.console_output.insert(
                    "end", f"Error:\n{error}\n", "error")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    def create_console(self):
        """Creates a notebook-based console area."""
        self.console_frame = ttk.Frame(self.root)
        self.console_frame.grid(row=2, column=0, columnspan=2, sticky="nswe")

        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("CustomNotebook.TNotebook", background="gray14", foreground="white")

        self.console_notebook = ttk.Notebook(self.console_frame, style="CustomNotebook.TNotebook")
        self.console_notebook.grid(row=0, column=0, sticky="nswe")

        console_tab = ttk.Frame(self.console_notebook)
        console_tab.grid_rowconfigure(0, weight=1)
        console_tab.grid_columnconfigure(0, weight=1)

        self.console_output = tk.Text(
            console_tab, height=10, wrap="none", bg="gray14", fg="white", font=("Consolas", 12)
        )
        self.console_output.grid(row=0, column=0, sticky="nswe")
        self.console_output.tag_configure("output", foreground="green")
        self.console_output.tag_configure("error", foreground="red")

        scrollbar = ttk.Scrollbar(console_tab, orient="vertical", command=self.console_output.yview)
        self.console_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.console_notebook.add(console_tab, text="Console")

    def open_file(self, event=None):
        """Open a file and display its content in a new tab."""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()

            self.add_new_tab(os.path.basename(file_path))

            current_tab = self.notebook.tabs()[-1]
            self.notebook.select(current_tab)

            frame = self.notebook.nametowidget(current_tab)
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkTextbox):
                    widget.insert("1.0", content)


    def open_folder(self):
        """Open a folder and display its contents in the file tree."""
        folder_path = filedialog.askdirectory() 
        if folder_path:
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            self.populate_file_tree(folder_path)

    def save_file(self, event=None):
        """Save the content of the current tab to a file and update the file tree."""
        current_tab = self.notebook.select()
        if not current_tab:
            return

        text_widget = self.get_current_text_widget()
        if not text_widget:
            return
        
        file_path = getattr(text_widget, "file_path", None)

        if file_path: 
            with open(file_path, 'w', encoding="utf-8") as file:
                file.write(text_widget.get("1.0", "end-1c"))
            self.console_output.insert(
                "end", f"File saved: {file_path}\n", "output")
            self.update_file_tree(os.path.dirname(
                file_path))  

        else:  
            file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[
                                                     ("Python Files", "*.py"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, 'w', encoding="utf-8") as file:
                    file.write(text_widget.get("1.0", "end-1c"))
                text_widget.file_path = file_path  
                self.console_output.insert(
                    "end", f"File saved: {file_path}\n", "output")
                self.update_file_tree(os.path.dirname(
                    file_path))  
                
    def update_file_tree(self, path):
        """Update the file tree to reflect changes after saving a file."""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        self.populate_file_tree(path)
                
    def copy_text(self):
        """Copy the selected text to the clipboard."""
        text_widget = self.get_current_text_widget()
        if text_widget:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) else ''
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)

    def cut_text(self):
        """Cut the selected text to the clipboard."""
        text_widget = self.get_current_text_widget()
        if text_widget:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) else ''
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def paste_text(self):
        """Paste the text from the clipboard into the current text widget."""
        text_widget = self.get_current_text_widget()
        if text_widget:
            clipboard_content = self.root.clipboard_get()
            text_widget.insert(tk.INSERT, clipboard_content)

    def show_about(self):
        """Show information about the application."""
        tk.messagebox.showinfo("About", "PySic IDE\nVersion 1.0")

    def show_shortcuts(self):
        """Muestra los atajos de teclado y ratón en un messagebox."""
        shortcuts_text = """
        Keyboard shortcuts:

        - Open file: Ctrl + O
        - Save file: Ctrl + S
        - Run code: Ctrl + r
        - Close tab: Ctrl + W
        - Copy: Ctrl + c
        - Paste: Ctrl + v
        - Cut: Ctrl + x
        
        Mouse shortcuts:

        - Double click on file (Treeview): Open file
        - Mouse wheel click on tab: Close tab
        """
        messagebox.showinfo("Shortcuts", shortcuts_text)