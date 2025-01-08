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
from tkinter import ttk, Menu, filedialog, messagebox
import customtkinter as ctk
from src import themes

# %% 3. Classes


class MainWindow():
    def __init__(self, root):
        self.root = root
        self.root.title("PySic IDE")
        self.root.geometry("1100x700")

        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=10)
        self.root.grid_rowconfigure(2, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=20)

        # Create UI components
        self.create_menu()
        self.create_sidebar()
        self.create_main_area()
        self.create_console()

    def create_menu(self):
        """Creates the menu bar."""
        self.menu_bar = Menu(self.root)

        # File menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(
            label="Open File", command=lambda: self.open_file(None))
        file_menu.add_command(
            label="Save File", command=lambda: self.save_file(None))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=self.menu_bar)

        # Asociar el atajo de teclado Ctrl + S con la acción de guardar archivo
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-o>", self.open_file)

    def create_sidebar(self):
        """Creates the file tree view on the left side."""
        self.sidebar = ttk.Frame(self.root)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nswe")

        self.file_tree = ttk.Treeview(self.sidebar)
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
                        self.apply_syntax_highlighting(widget)

    def populate_file_tree(self, path):
        """Populate the file tree with files and directories."""
        for item in os.listdir(path):
            abs_path = os.path.join(path, item)
            if os.path.isdir(abs_path):
                self.file_tree.insert(
                    "", "end", text=item, open=False, values=(abs_path,))
            else:
                self.file_tree.insert("", "end", text=item, values=(abs_path,))

    def create_main_area(self):
        """Crea el área principal con un notebook y un botón de ejecución."""
        self.main_area = ttk.Frame(self.root)
        self.main_area.grid(row=1, column=1, sticky="nswe")

        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=0)
        self.main_area.grid_columnconfigure(1, weight=1)

        self.run_button = ctk.CTkButton(
            self.main_area, text="Run", command=self.run_current_code
        )
        self.run_button.grid(row=0, column=1, sticky="e")

        self.line_canvas = tk.Canvas(self.main_area, width=30, bg="lightgray")
        self.line_canvas.grid(row=1, column=0, sticky="ns")

        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.grid(row=1, column=1, sticky="nswe")

        self.add_new_tab("Untitled")

        self.notebook.bind("<Button-2>", self.close_tab)
        self.root.bind("<Control-w>", self.close_tab)

    def update_line_numbers(self, event=None):
        """Actualiza los números de línea en el canvas."""
        text_widget = self.get_current_text_widget()
        if not text_widget:
            return

        self.line_canvas.delete("all")
        i = text_widget.index("@0,0")  # Obtén la primera línea visible

        while True:
            dline_info = text_widget.dlineinfo(i)
            if dline_info is None:  # Si no hay más líneas visibles, sal del bucle
                break

            y = dline_info[1]
            line_number = str(i).split(".")[0]
            self.line_canvas.create_text(
                2, y + 28, anchor="nw", text=line_number, font=("Consolas", 10))
            i = text_widget.index(f"{i}+1line")  # Avanza a la siguiente línea

    def add_new_tab(self, title):
        """Adds a new tab to the notebook."""
        frame = ttk.Frame(self.notebook)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # CustomTkinter Text Widget
        text_widget = tk.Text(frame, wrap="none", bg="black", fg="white", font=("Cascadia code", 11))
        text_widget.grid(row=0, column=0, sticky="nswe")

        # Conectar eventos de scroll y cambios de texto al canvas
        text_widget.bind("<KeyRelease>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<MouseWheel>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<Button-1>", lambda e: self.update_line_numbers(e))
        text_widget.bind("<Motion>", lambda e: self.update_line_numbers(e))

        # Scrollbar para el texto
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

    def run_current_code(self):
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
                error = sys.stderr.getvalue()
                self.console_output.insert(
                    "end", f"Error:\n{error}\n", "error")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    def create_console(self):
        """Creates a console area to display output or errors."""
        self.console_frame = ttk.Frame(self.root)
        self.console_frame.grid(row=2, column=0, columnspan=2, sticky="nswe")

        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.console_output = tk.Text(
            self.console_frame, height=10, wrap="none", bg="black", fg="white", font=("Consolas", 11)
        )
        self.console_output.grid(row=0, column=0, sticky="nswe")
        self.console_output.tag_configure("output", foreground="green")
        self.console_output.tag_configure("error", foreground="red")

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

    def save_file(self, event=None):
        """Save the content of the current tab to a file and update the file tree."""
        current_tab = self.notebook.select()
        if not current_tab:
            return

        text_widget = self.get_current_text_widget()
        if not text_widget:
            return

        # Verifica si el archivo tiene una ruta guardada
        file_path = getattr(text_widget, "file_path", None)

        if file_path:  # Si el archivo ya tiene una ruta guardada, solo guardamos
            with open(file_path, 'w', encoding="utf-8") as file:
                file.write(text_widget.get("1.0", "end-1c"))
            self.console_output.insert(
                "end", f"File saved: {file_path}\n", "output")
            self.update_file_tree(os.path.dirname(
                file_path))  # Actualiza el Treeview

        else:  # Si el archivo no tiene una ruta guardada, pedimos la ruta para guardar
            file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[
                                                     ("Python Files", "*.py"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, 'w', encoding="utf-8") as file:
                    file.write(text_widget.get("1.0", "end-1c"))
                text_widget.file_path = file_path  # Guardamos la ruta para futuras referencias
                self.console_output.insert(
                    "end", f"File saved: {file_path}\n", "output")
                self.update_file_tree(os.path.dirname(
                    file_path))  # Actualiza el Treeview

    def update_file_tree(self, path):
        """Update the file tree to reflect changes after saving a file."""
        # Limpiar el árbol existente
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Volver a poblar el árbol con los archivos y carpetas del directorio actualizado
        self.populate_file_tree(path)

    def show_about(self):
        """Show information about the application."""
        tk.messagebox.showinfo("About", "PySic IDE\nVersion 1.0")

    def show_shortcuts(self):
        """Muestra los atajos de teclado y ratón en un messagebox."""
        shortcuts_text = """
        Keyboard shortcuts:

        - Open file: Ctrl + O
        - Save file: Ctrl + S
        - Run code: F5
        - Close tab: Ctrl + W

        Mouse shortcuts:

        - Double click on file (Treeview): Open file
        - Mouse wheel click on tab: Close tab
        """

        # Usar el messagebox para mostrar los atajos
        messagebox.showinfo("Shortcuts", shortcuts_text)
