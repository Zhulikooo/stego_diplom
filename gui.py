"""
gui.py - Графический интерфейс автоматизированной системы стегоанализа
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import numpy as np
from PIL import Image, ImageTk

from rs_core import analyze_image
from embedding import embed_fixed_bits, embed_bits_in_one_pixel
from extraction import embed_text_only, embed_text_with_fill, extract_text_from_image
from experiments import run_experiment, run_sensitivity_experiment, run_pixel_bits_experiment, run_all_pixels_bits_experiment

matplotlib_imported = False


def import_matplotlib():
    global matplotlib_imported, plt, FigureCanvasTkAgg
    if not matplotlib_imported:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib_imported = True
    return plt, FigureCanvasTkAgg


class StegoAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматизированная система стегоанализа растровых изображений")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        self.setup_styles()
        
        self.current_image_path = None
        self.current_image = None
        self.photo = None
        self.stego_image_path = None
        
        self.fig = None
        self.ax = None
        self.canvas = None
        self.research_left_frame = None
        
        self.sensitivity_fig = None
        self.sensitivity_ax = None
        self.sensitivity_canvas = None
        
        self.pixel_bits_fig = None
        self.pixel_bits_ax = None
        self.pixel_bits_canvas = None
        
        self.all_pixels_fig = None
        self.all_pixels_ax = None
        self.all_pixels_canvas = None
        
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure('TLabel', font=('Segoe UI', 12))
        style.configure('TButton', font=('Segoe UI', 12))
        style.configure('TLabelframe.Label', font=('Segoe UI', 14, 'bold'))
        style.configure('TNotebook.Tab', font=('Segoe UI', 13))
        self.root.option_add('*Text.font', ('Segoe UI', 12))
        self.root.option_add('*Entry.font', ('Segoe UI', 12))
        self.root.option_add('*Combobox.font', ('Segoe UI', 12))
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="🔍 Стегоанализ")
        self.create_analysis_tab()
        
        self.embed_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.embed_tab, text="🖊 Встраивание")
        self.create_embed_tab()
        
        self.extract_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_tab, text="📤 Извлечение")
        self.create_extract_tab()
        
        self.research_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.research_tab, text="📊 Исследование %")
        self.create_research_tab()
        
        self.sensitivity_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sensitivity_tab, text="🎯 Порог (1-20 бит)")
        self.create_sensitivity_tab()
        
        self.pixel_bits_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pixel_bits_tab, text="🔬 Биты в пикселе")
        self.create_pixel_bits_tab()
        
        self.all_pixels_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.all_pixels_tab, text="🔬 Биты во всех пикселях")
        self.create_all_pixels_tab()
        
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # ==================== ВКЛАДКА АНАЛИЗА ====================
    
    def create_analysis_tab(self):
        frame = ttk.Frame(self.analysis_tab, padding="10")
        frame.pack(fill=tk.X)
        
        ttk.Button(frame, text="📂 Открыть изображение", command=self.open_for_analysis).pack(side=tk.LEFT, padx=5)
        
        mask_frame = ttk.LabelFrame(frame, text="Настройки маски", padding="5")
        mask_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(mask_frame, text="Маска (через запятую):").pack(side=tk.LEFT)
        self.mask_entry = ttk.Entry(mask_frame, width=20)
        self.mask_entry.insert(0, "0,1,0")
        self.mask_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="🔬 Запустить анализ", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        
        main_paned = ttk.PanedWindow(self.analysis_tab, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        self.image_label = ttk.Label(left_frame, text="📷 Здесь будет отображаться изображение", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(right_top_frame, text="Результаты анализа:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(right_top_frame, text="📋 Копировать", 
                              command=lambda: self.copy_to_clipboard(self.results_text))
        copy_btn.pack(side=tk.RIGHT)
        
        self.results_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.insert(tk.END, "Ожидание анализа...\n\nНажмите 'Открыть изображение'")
    
    def open_for_analysis(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.current_image_path = file_path
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")
            img = Image.open(file_path)
            display_img = img.copy()
            display_img.thumbnail((400, 400))
            self.photo = ImageTk.PhotoImage(display_img)
            self.image_label.config(image=self.photo, text="")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Изображение: {os.path.basename(file_path)}\n")
            self.results_text.insert(tk.END, f"Размер: {img.width} x {img.height}\n\n")
            self.results_text.insert(tk.END, "Нажмите 'Запустить анализ'\n")
    
    def run_analysis(self):
        if not self.current_image_path:
            messagebox.showwarning("Внимание", "Сначала выберите изображение!")
            return
        try:
            mask = tuple(int(x.strip()) for x in self.mask_entry.get().split(','))
            for m in mask:
                if m not in (-1, 0, 1):
                    raise ValueError()
        except:
            messagebox.showerror("Ошибка", "Неверный формат маски!\nПример: 0,1,0")
            return
        
        self.status_var.set("Выполняется анализ...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Анализ выполняется...\n\n")
        self.root.update()
        thread = threading.Thread(target=self._do_analysis, args=(mask,))
        thread.daemon = True
        thread.start()
    
    def _do_analysis(self, mask):
        try:
            results = analyze_image(self.current_image_path, mask)
            self.root.after(0, self._display_results, results, mask)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _display_results(self, results, mask):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "=" * 55 + "\n")
        self.results_text.insert(tk.END, "РЕЗУЛЬТАТЫ RS-СТЕГОАНАЛИЗА\n")
        self.results_text.insert(tk.END, "=" * 55 + "\n\n")
        self.results_text.insert(tk.END, f"Маска: {mask}\n\n")
        self.results_text.insert(tk.END, "-" * 45 + "\n")
        self.results_text.insert(tk.END, "Маска M:\n")
        self.results_text.insert(tk.END, f"  Regular (R):   {results['R_m']:.2f}%\n")
        self.results_text.insert(tk.END, f"  Singular (S):  {results['S_m']:.2f}%\n")
        self.results_text.insert(tk.END, f"  Разность R-S:  {results['diff_m']:.2f}%\n\n")
        self.results_text.insert(tk.END, "Маска -M:\n")
        self.results_text.insert(tk.END, f"  Regular (R):   {results['R_minus_m']:.2f}%\n")
        self.results_text.insert(tk.END, f"  Singular (S):  {results['S_minus_m']:.2f}%\n")
        self.results_text.insert(tk.END, f"  Разность R-S:  {results['diff_minus_m']:.2f}%\n\n")
        
        diff = results['diff_m']
        if diff > 50:
            verdict = "✅ ЧИСТОЕ"
        elif diff > 20:
            verdict = "⚠️ ПОДОЗРИТЕЛЬНОЕ"
        else:
            verdict = "🚨 ВСТРОЙКА ОБНАРУЖЕНА!"
        self.results_text.insert(tk.END, f"ЗАКЛЮЧЕНИЕ: {verdict}\n")
        self.status_var.set("Анализ завершён")
    
    # ==================== ВКЛАДКА ВСТРАИВАНИЯ ====================
    
    def create_embed_tab(self):
        frame = ttk.Frame(self.embed_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="1. Выберите исходное изображение:").pack(anchor=tk.W)
        select_frame = ttk.Frame(frame)
        select_frame.pack(fill=tk.X, pady=5)
        self.embed_source_path = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.embed_source_path, state='readonly', width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Обзор", command=self.select_source_for_embed).pack(side=tk.LEFT)
        
        self.embed_preview_label = ttk.Label(frame, text="Изображение не выбрано", relief=tk.SUNKEN, anchor=tk.CENTER)
        self.embed_preview_label.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(frame, text="2. Введите сообщение:").pack(anchor=tk.W)
        self.message_text = scrolledtext.ScrolledText(frame, height=4, width=60)
        self.message_text.pack(fill=tk.X, pady=5)
        
        mode_frame = ttk.LabelFrame(frame, text="3. Режим встраивания", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)
        self.embed_mode = tk.StringVar(value="text_only")
        ttk.Radiobutton(mode_frame, text="Только текст (мало битов)", variable=self.embed_mode, value="text_only").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(mode_frame, text="Текст + 50% случайных битов (ДЛЯ ДЕМОНСТРАЦИИ)", variable=self.embed_mode, value="fill_50").pack(anchor=tk.W, pady=2)
        
        ttk.Button(frame, text="4. Встроить сообщение", command=self.run_embed).pack(pady=10)
        self.embed_result_label = ttk.Label(frame, text="", foreground="green", wraplength=600)
        self.embed_result_label.pack()
    
    def select_source_for_embed(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.embed_source_path.set(file_path)
            img = Image.open(file_path)
            display_img = img.copy()
            display_img.thumbnail((300, 200))
            photo = ImageTk.PhotoImage(display_img)
            self.embed_preview_label.config(image=photo, text="")
            self.embed_preview_label.image = photo
    
    def run_embed(self):
        source_path = self.embed_source_path.get()
        if not source_path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Внимание", "Введите сообщение!")
            return
        
        results_dir = os.path.join(os.path.dirname(source_path), "results")
        os.makedirs(results_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        output_path = os.path.join(results_dir, f"{base_name}_stego.png")
        
        self.status_var.set("Встраивание...")
        self.root.update()
        
        try:
            if self.embed_mode.get() == "text_only":
                bits = embed_text_only(source_path, output_path, message)
                self.embed_result_label.config(text=f"✅ Встроено {bits} битов", foreground="green")
            else:
                bits = embed_text_with_fill(source_path, output_path, message, 50)
                self.embed_result_label.config(text=f"✅ Встроено {bits} битов (50% заполнение)", foreground="blue")
            
            if messagebox.askyesno("Анализ", "Проанализировать полученное изображение?"):
                self.current_image_path = output_path
                self.notebook.select(self.analysis_tab)
                self.open_image_for_analysis(output_path)
                self.run_analysis()
        except Exception as e:
            self.embed_result_label.config(text=f"❌ Ошибка: {e}", foreground="red")
    
    def open_image_for_analysis(self, path):
        self.current_image_path = path
        img = Image.open(path)
        display_img = img.copy()
        display_img.thumbnail((400, 400))
        self.photo = ImageTk.PhotoImage(display_img)
        self.image_label.config(image=self.photo, text="")
    
    # ==================== ВКЛАДКА ИЗВЛЕЧЕНИЯ ====================
    
    def create_extract_tab(self):
        frame = ttk.Frame(self.extract_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Выберите изображение:").pack(anchor=tk.W)
        select_frame = ttk.Frame(frame)
        select_frame.pack(fill=tk.X, pady=5)
        self.extract_path = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.extract_path, state='readonly', width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Обзор", command=self.select_for_extract).pack(side=tk.LEFT)
        
        self.extract_preview_label = ttk.Label(frame, text="Изображение не выбрано", relief=tk.SUNKEN, anchor=tk.CENTER)
        self.extract_preview_label.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Button(frame, text="Извлечь сообщение", command=self.run_extract).pack(pady=10)
        
        ttk.Label(frame, text="Извлечённое сообщение:").pack(anchor=tk.W)
        self.extract_result_text = scrolledtext.ScrolledText(frame, height=6, width=60)
        self.extract_result_text.pack(fill=tk.X, pady=5)
        self.extract_status_label = ttk.Label(frame, text="")
        self.extract_status_label.pack()
    
    def select_for_extract(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.extract_path.set(file_path)
            img = Image.open(file_path)
            display_img = img.copy()
            display_img.thumbnail((300, 200))
            photo = ImageTk.PhotoImage(display_img)
            self.extract_preview_label.config(image=photo, text="")
            self.extract_preview_label.image = photo
    
    def run_extract(self):
        path = self.extract_path.get()
        if not path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        
        self.status_var.set("Извлечение...")
        self.extract_result_text.delete(1.0, tk.END)
        self.extract_result_text.insert(tk.END, "Извлечение...\n")
        self.root.update()
        
        try:
            text = extract_text_from_image(path)
            if text:
                self.extract_result_text.delete(1.0, tk.END)
                self.extract_result_text.insert(tk.END, text)
                self.extract_status_label.config(text="✅ Сообщение извлечено", foreground="green")
            else:
                self.extract_result_text.delete(1.0, tk.END)
                self.extract_result_text.insert(tk.END, "Сообщение не найдено")
                self.extract_status_label.config(text="❌ Сообщение не найдено", foreground="red")
        except Exception as e:
            self.extract_result_text.delete(1.0, tk.END)
            self.extract_result_text.insert(tk.END, f"Ошибка: {e}")
    
    # ==================== ВКЛАДКА ИССЛЕДОВАНИЕ % ====================
    
    def create_research_tab(self):
        frame = ttk.Frame(self.research_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.LabelFrame(frame, text="Параметры эксперимента", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Изображение:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.research_image_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.research_image_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Обзор", command=self.select_research_image).grid(row=0, column=2, padx=5)
        
        ttk.Label(control_frame, text="Метод:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.research_method = tk.StringVar(value="LSB все пиксели")
        combo = ttk.Combobox(control_frame, textvariable=self.research_method, width=45)
        combo['values'] = ("LSB все пиксели", "LSB синий канал", "Случайные пиксели", 
                          "Случайные биты и случайные пиксели", "Только случайные биты")
        combo.grid(row=1, column=1, padx=5)
        
        ttk.Label(control_frame, text="Номер бита (0-7):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.bit_pos = tk.IntVar(value=0)
        ttk.Spinbox(control_frame, from_=0, to=7, textvariable=self.bit_pos, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(control_frame, text="Макс. процент:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_percent = tk.IntVar(value=100)
        ttk.Spinbox(control_frame, from_=10, to=100, textvariable=self.max_percent, width=10).grid(row=3, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(control_frame, text="Шаг (%):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_percent = tk.IntVar(value=10)
        ttk.Spinbox(control_frame, from_=5, to=20, textvariable=self.step_percent, width=10).grid(row=4, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(control_frame, text="ЗАПУСТИТЬ ЭКСПЕРИМЕНТ", command=self.run_research_experiment).grid(row=5, column=0, columnspan=3, pady=15)
        
        self.experiment_status = ttk.Label(frame, text="", foreground="blue")
        self.experiment_status.pack(pady=5)
        
        self.research_progress = ttk.Progressbar(frame, mode='determinate', length=400)
        self.research_progress.pack(pady=5)
        
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        left_frame = ttk.LabelFrame(paned, text="График")
        right_frame = ttk.LabelFrame(paned, text="Результаты")
        paned.add(left_frame, weight=2)
        paned.add(right_frame, weight=1)
        
        self.research_placeholder = ttk.Label(left_frame, text="Нажмите 'ЗАПУСТИТЬ ЭКСПЕРИМЕНТ'", font=('Segoe UI', 14))
        self.research_placeholder.pack(expand=True)
        self.research_left_frame = left_frame
        
        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(right_top_frame, text="Результаты эксперимента:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(right_top_frame, text="📋 Копировать", 
                              command=lambda: self.copy_to_clipboard(self.research_text))
        copy_btn.pack(side=tk.RIGHT)
        
        self.research_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.research_text.yview)
        self.research_text.configure(yscrollcommand=scrollbar.set)
        self.research_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.research_text.insert(tk.END, "Ожидание эксперимента...")
    
    def select_research_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.research_image_path.set(path)
    
    def run_research_experiment(self):
        path = self.research_image_path.get()
        if not path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        self.experiment_status.config(text="Выполняется эксперимент...", foreground="blue")
        self.research_progress['value'] = 0
        self.root.update()
        thread = threading.Thread(target=self._do_research_experiment, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _do_research_experiment(self, path):
        import_matplotlib()
        self.root.after(0, self._init_research_graph)
        
        method = self.research_method.get()
        bit = self.bit_pos.get()
        max_p = self.max_percent.get()
        step = self.step_percent.get()
        
        from experiments import run_experiment_with_progress
        results = run_experiment_with_progress(path, method, max_p, step, bit, self._update_research_progress)
        
        self.root.after(0, self._display_research_results, results, method, bit)
        self.root.after(0, self._reset_research_progress)
    
    def _update_research_progress(self, percent, current_percent):
        self.root.after(0, lambda: self.research_progress.configure(value=percent))
        self.root.after(0, lambda: self.experiment_status.config(
            text=f"Выполняется эксперимент... {current_percent}% готово", foreground="blue"))
    
    def _reset_research_progress(self):
        self.research_progress['value'] = 0
        self.experiment_status.config(text="Эксперимент завершён!", foreground="green")
    
    def _init_research_graph(self):
        if self.fig is None:
            plt, FigureCanvasTkAgg = import_matplotlib()
            self.research_placeholder.destroy()
            self.fig, self.ax = plt.subplots(figsize=(7, 5))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.research_left_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_research_results(self, results, method, bit):
        self.ax.clear()
        percents = [r['percent'] for r in results]
        diffs = [r['diff_m'] for r in results]
        self.ax.plot(percents, diffs, 'b-o', linewidth=2)
        self.ax.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='Порог 50%')
        self.ax.axhline(y=20, color='orange', linestyle='--', alpha=0.5, label='Порог 20%')
        self.ax.set_xlabel('Процент встройки (%)')
        self.ax.set_ylabel('R-S разность (%)')
        self.ax.set_title(f'{method}, бит {bit}')
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()
        
        self.research_text.delete(1.0, tk.END)
        self.research_text.insert(tk.END, "=" * 50 + "\n")
        self.research_text.insert(tk.END, f"Метод: {method}\nБит: {bit}\n")
        self.research_text.insert(tk.END, "=" * 50 + "\n\n")
        for r in results:
            self.research_text.insert(tk.END, f"{r['percent']:3}%  →  {r['diff_m']:.2f}%\n")
    
    # ==================== ВКЛАДКА ПОРОГ (1-20 БИТ) ====================
    
    def create_sensitivity_tab(self):
        frame = ttk.Frame(self.sensitivity_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        desc_frame = ttk.LabelFrame(frame, text="Описание", padding="10")
        desc_frame.pack(fill=tk.X, pady=5)
        ttk.Label(desc_frame, text="Эксперимент: встраивание от 1 до 20 битов в разные пиксели", wraplength=800).pack()
        
        control_frame = ttk.LabelFrame(frame, text="Параметры", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Изображение:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sens_image_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.sens_image_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Обзор", command=self.select_sens_image).grid(row=0, column=2, padx=5)
        
        ttk.Label(control_frame, text="Номер бита (0-7):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sens_bit_pos = tk.IntVar(value=0)
        ttk.Spinbox(control_frame, from_=0, to=7, textvariable=self.sens_bit_pos, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(control_frame, text="Макс. битов:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_sens_bits = tk.IntVar(value=20)
        ttk.Spinbox(control_frame, from_=5, to=50, textvariable=self.max_sens_bits, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(control_frame, text="ЗАПУСТИТЬ ЭКСПЕРИМЕНТ", command=self.run_sens_experiment).grid(row=3, column=0, columnspan=3, pady=15)
        
        self.sens_status = ttk.Label(frame, text="", foreground="blue")
        self.sens_status.pack(pady=5)
        
        self.sens_progress = ttk.Progressbar(frame, mode='determinate', length=400)
        self.sens_progress.pack(pady=5)
        
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        left_frame = ttk.LabelFrame(paned, text="График")
        right_frame = ttk.LabelFrame(paned, text="Результаты")
        paned.add(left_frame, weight=2)
        paned.add(right_frame, weight=1)
        
        self.sens_placeholder = ttk.Label(left_frame, text="Нажмите 'ЗАПУСТИТЬ ЭКСПЕРИМЕНТ'", font=('Segoe UI', 14))
        self.sens_placeholder.pack(expand=True)
        self.sens_left_frame = left_frame
        
        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(right_top_frame, text="Результаты эксперимента:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(right_top_frame, text="📋 Копировать", 
                              command=lambda: self.copy_to_clipboard(self.sens_text))
        copy_btn.pack(side=tk.RIGHT)
        
        self.sens_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.sens_text.yview)
        self.sens_text.configure(yscrollcommand=scrollbar.set)
        self.sens_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sens_text.insert(tk.END, "Ожидание эксперимента...")
    
    def select_sens_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.sens_image_path.set(path)
    
    def run_sens_experiment(self):
        path = self.sens_image_path.get()
        if not path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        self.sens_status.config(text="Выполняется...", foreground="blue")
        self.sens_progress['value'] = 0
        self.root.update()
        thread = threading.Thread(target=self._do_sens_experiment, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _do_sens_experiment(self, path):
        import_matplotlib()
        self.root.after(0, self._init_sens_graph)
        bit = self.sens_bit_pos.get()
        max_bits = self.max_sens_bits.get()
        
        from experiments import run_sensitivity_experiment_with_progress
        results = run_sensitivity_experiment_with_progress(path, max_bits, bit, self._update_sens_progress)
        
        self.root.after(0, self._display_sens_results, results, bit)
        self.root.after(0, self._reset_sens_progress)
    
    def _update_sens_progress(self, percent, current_bit):
        self.root.after(0, lambda: self.sens_progress.configure(value=percent))
        self.root.after(0, lambda: self.sens_status.config(
            text=f"Выполняется... {current_bit}/{self.max_sens_bits.get()} битов", foreground="blue"))
    
    def _reset_sens_progress(self):
        self.sens_progress['value'] = 0
        self.sens_status.config(text="Эксперимент завершён!", foreground="green")
    
    def _init_sens_graph(self):
        if self.sensitivity_fig is None:
            plt, FigureCanvasTkAgg = import_matplotlib()
            self.sens_placeholder.destroy()
            self.sensitivity_fig, self.sensitivity_ax = plt.subplots(figsize=(7, 5))
            self.sensitivity_canvas = FigureCanvasTkAgg(self.sensitivity_fig, master=self.sens_left_frame)
            self.sensitivity_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_sens_results(self, results, bit):
        self.sensitivity_ax.clear()
        bits = [r['bits'] for r in results]
        diffs = [r['diff_m'] for r in results]
        self.sensitivity_ax.plot(bits, diffs, 'r-o', linewidth=2)
        self.sensitivity_ax.set_xlabel('Количество битов')
        self.sensitivity_ax.set_ylabel('R-S разность (%)')
        self.sensitivity_ax.set_title(f'Порог чувствительности, бит {bit}')
        self.sensitivity_ax.grid(True)
        self.sensitivity_canvas.draw()
        
        self.sens_text.delete(1.0, tk.END)
        self.sens_text.insert(tk.END, "=" * 50 + f"\nБит: {bit}\n" + "=" * 50 + "\n\n")
        self.sens_text.insert(tk.END, f"{'Битов':<8} {'R-S':<12} {'Изменение':<12}\n")
        self.sens_text.insert(tk.END, "-" * 35 + "\n")
        for r in results:
            self.sens_text.insert(tk.END, f"{r['bits']:<8} {r['diff_m']:<12.4f} {r['change']:<12.4f}\n")
    
    # ==================== ВКЛАДКА БИТЫ В ПИКСЕЛЕ ====================
    
    def create_pixel_bits_tab(self):
        frame = ttk.Frame(self.pixel_bits_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        desc_frame = ttk.LabelFrame(frame, text="Описание эксперимента", padding="10")
        desc_frame.pack(fill=tk.X, pady=5)
        desc_text = (
            "Цель: определить, как изменяется R-S при встраивании разного количества битов\n"
            "в ОДИН пиксель изображения.\n\n"
            "• 1 бит → меняется только бит 0 (LSB)\n"
            "• 2 бита → меняются биты 0 и 1\n"
            "...\n"
            "• 8 битов → меняются ВСЕ биты (0-7)"
        )
        ttk.Label(desc_frame, text=desc_text, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        control_frame = ttk.LabelFrame(frame, text="Параметры", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Изображение:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pixel_bits_image_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.pixel_bits_image_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Обзор", command=self.select_pixel_bits_image).grid(row=0, column=2, padx=5)
        
        ttk.Button(control_frame, text="ЗАПУСТИТЬ ЭКСПЕРИМЕНТ", command=self.run_pixel_bits_experiment).grid(row=1, column=0, columnspan=3, pady=15)
        
        self.pixel_bits_status = ttk.Label(frame, text="", foreground="blue")
        self.pixel_bits_status.pack(pady=5)
        
        self.pixel_bits_progress = ttk.Progressbar(frame, mode='determinate', length=400)
        self.pixel_bits_progress.pack(pady=5)
        
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        left_frame = ttk.LabelFrame(paned, text="График")
        right_frame = ttk.LabelFrame(paned, text="Результаты")
        paned.add(left_frame, weight=2)
        paned.add(right_frame, weight=1)
        
        self.pixel_bits_placeholder = ttk.Label(left_frame, text="Нажмите 'ЗАПУСТИТЬ ЭКСПЕРИМЕНТ'", font=('Segoe UI', 14))
        self.pixel_bits_placeholder.pack(expand=True)
        self.pixel_bits_left_frame = left_frame
        
        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(right_top_frame, text="Результаты эксперимента:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(right_top_frame, text="📋 Копировать", 
                              command=lambda: self.copy_to_clipboard(self.pixel_bits_text))
        copy_btn.pack(side=tk.RIGHT)
        
        self.pixel_bits_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.pixel_bits_text.yview)
        self.pixel_bits_text.configure(yscrollcommand=scrollbar.set)
        self.pixel_bits_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pixel_bits_text.insert(tk.END, "Ожидание эксперимента...")
    
    def select_pixel_bits_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.pixel_bits_image_path.set(path)
    
    def run_pixel_bits_experiment(self):
        path = self.pixel_bits_image_path.get()
        if not path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        self.pixel_bits_status.config(text="Выполняется эксперимент...", foreground="blue")
        self.pixel_bits_progress['value'] = 0
        self.root.update()
        thread = threading.Thread(target=self._do_pixel_bits_experiment, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _do_pixel_bits_experiment(self, path):
        import_matplotlib()
        self.root.after(0, self._init_pixel_bits_graph)
        
        from experiments import run_pixel_bits_experiment_with_progress
        results = run_pixel_bits_experiment_with_progress(path, 8, self._update_pixel_bits_progress)
        
        self.root.after(0, self._display_pixel_bits_results, results)
        self.root.after(0, self._reset_pixel_bits_progress)
    
    def _update_pixel_bits_progress(self, percent, current_bit):
        self.root.after(0, lambda: self.pixel_bits_progress.configure(value=percent))
        self.root.after(0, lambda: self.pixel_bits_status.config(
            text=f"Выполняется... {current_bit}/8 битов в пикселе", foreground="blue"))
    
    def _reset_pixel_bits_progress(self):
        self.pixel_bits_progress['value'] = 0
        self.pixel_bits_status.config(text="Эксперимент завершён!", foreground="green")
    
    def _init_pixel_bits_graph(self):
        if self.pixel_bits_fig is None:
            plt, FigureCanvasTkAgg = import_matplotlib()
            self.pixel_bits_placeholder.destroy()
            self.pixel_bits_fig, self.pixel_bits_ax = plt.subplots(figsize=(7, 5))
            self.pixel_bits_canvas = FigureCanvasTkAgg(self.pixel_bits_fig, master=self.pixel_bits_left_frame)
            self.pixel_bits_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_pixel_bits_results(self, results):
        self.pixel_bits_ax.clear()
        bits = [r['bits'] for r in results]
        diffs = [r['diff_m'] for r in results]
        self.pixel_bits_ax.plot(bits, diffs, 'r-o', linewidth=2, markersize=10)
        self.pixel_bits_ax.set_xlabel('Количество изменённых битов в пикселе')
        self.pixel_bits_ax.set_ylabel('R-S разность (%)')
        self.pixel_bits_ax.set_title('Биты в одном пикселе')
        self.pixel_bits_ax.grid(True)
        self.pixel_bits_ax.set_xticks(range(0, 9))
        self.pixel_bits_canvas.draw()
        
        self.pixel_bits_text.delete(1.0, tk.END)
        self.pixel_bits_text.insert(tk.END, "=" * 55 + "\n")
        self.pixel_bits_text.insert(tk.END, "БИТЫ В ОДНОМ ПИКСЕЛЕ\n")
        self.pixel_bits_text.insert(tk.END, "=" * 55 + "\n\n")
        self.pixel_bits_text.insert(tk.END, f"{'Битов':<8} {'R-S':<12} {'Изменение':<12}\n")
        self.pixel_bits_text.insert(tk.END, "-" * 35 + "\n")
        for r in results:
            self.pixel_bits_text.insert(tk.END, f"{r['bits']:<8} {r['diff_m']:<12.4f} {r['change']:<12.4f}\n")
        
        if len(results) > 1:
            self.pixel_bits_text.insert(tk.END, "\n" + "=" * 55 + "\n")
            self.pixel_bits_text.insert(tk.END, "ВЫВОДЫ:\n")
            ch1 = results[1]['change'] if len(results) > 1 else 0
            ch8 = results[-1]['change'] if results else 0
            self.pixel_bits_text.insert(tk.END, f"  • Падение после 1 бита: {ch1:.4f}%\n")
            self.pixel_bits_text.insert(tk.END, f"  • Падение после 8 битов: {ch8:.4f}%\n")
            if ch1 > 0:
                self.pixel_bits_text.insert(tk.END, f"  • Эффект сильнее в {ch8/ch1:.1f} раз\n")
    
    # ==================== ВКЛАДКА БИТЫ ВО ВСЕХ ПИКСЕЛЯХ ====================
    
    def create_all_pixels_tab(self):
        """Создание вкладки: встраивание битов во ВСЕ пиксели"""
        frame = ttk.Frame(self.all_pixels_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        desc_frame = ttk.LabelFrame(frame, text="Описание эксперимента", padding="10")
        desc_frame.pack(fill=tk.X, pady=5)
        desc_text = (
            "Цель: определить, как изменяется R-S при встраивании разного количества битов\n"
            "в КАЖДЫЙ пиксель изображения.\n\n"
            "• 1 бит → в каждом пикселе меняется только бит 0 (LSB)\n"
            "• 2 бита → в каждом пикселе меняются биты 0 и 1\n"
            "...\n"
            "• 8 битов → в каждом пикселе меняются ВСЕ биты (0-7)"
        )
        ttk.Label(desc_frame, text=desc_text, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        control_frame = ttk.LabelFrame(frame, text="Параметры", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Изображение:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.all_pixels_image_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.all_pixels_image_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Обзор", command=self.select_all_pixels_image).grid(row=0, column=2, padx=5)
        
        ttk.Button(control_frame, text="ЗАПУСТИТЬ ЭКСПЕРИМЕНТ", command=self.run_all_pixels_experiment).grid(row=1, column=0, columnspan=3, pady=15)
        
        self.all_pixels_status = ttk.Label(frame, text="", foreground="blue")
        self.all_pixels_status.pack(pady=5)
        
        self.all_pixels_progress = ttk.Progressbar(frame, mode='determinate', length=400)
        self.all_pixels_progress.pack(pady=5)
        
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        left_frame = ttk.LabelFrame(paned, text="График")
        right_frame = ttk.LabelFrame(paned, text="Результаты")
        paned.add(left_frame, weight=2)
        paned.add(right_frame, weight=1)
        
        self.all_pixels_placeholder = ttk.Label(left_frame, text="Нажмите 'ЗАПУСТИТЬ ЭКСПЕРИМЕНТ'", font=('Segoe UI', 14))
        self.all_pixels_placeholder.pack(expand=True)
        self.all_pixels_left_frame = left_frame
        
        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(right_top_frame, text="Результаты эксперимента:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(right_top_frame, text="📋 Копировать", 
                              command=lambda: self.copy_to_clipboard(self.all_pixels_text))
        copy_btn.pack(side=tk.RIGHT)
        
        self.all_pixels_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.all_pixels_text.yview)
        self.all_pixels_text.configure(yscrollcommand=scrollbar.set)
        self.all_pixels_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.all_pixels_text.insert(tk.END, "Ожидание эксперимента...")
    
    def select_all_pixels_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.all_pixels_image_path.set(path)
    
    def run_all_pixels_experiment(self):
        path = self.all_pixels_image_path.get()
        if not path:
            messagebox.showwarning("Внимание", "Выберите изображение!")
            return
        self.all_pixels_status.config(text="Выполняется эксперимент...", foreground="blue")
        self.all_pixels_progress['value'] = 0
        self.root.update()
        thread = threading.Thread(target=self._do_all_pixels_experiment, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _do_all_pixels_experiment(self, path):
        import_matplotlib()
        self.root.after(0, self._init_all_pixels_graph)
        
        results = run_all_pixels_bits_experiment(path, 8, self._update_all_pixels_progress)
        
        self.root.after(0, self._display_all_pixels_results, results)
        self.root.after(0, self._reset_all_pixels_progress)
    
    def _update_all_pixels_progress(self, percent, current_bit):
        self.root.after(0, lambda: self.all_pixels_progress.configure(value=percent))
        self.root.after(0, lambda: self.all_pixels_status.config(
            text=f"Выполняется... {current_bit}/8 битов в каждом пикселе", foreground="blue"))
    
    def _reset_all_pixels_progress(self):
        self.all_pixels_progress['value'] = 0
        self.all_pixels_status.config(text="Эксперимент завершён!", foreground="green")
    
    def _init_all_pixels_graph(self):
        if self.all_pixels_fig is None:
            plt, FigureCanvasTkAgg = import_matplotlib()
            self.all_pixels_placeholder.destroy()
            self.all_pixels_fig, self.all_pixels_ax = plt.subplots(figsize=(7, 5))
            self.all_pixels_canvas = FigureCanvasTkAgg(self.all_pixels_fig, master=self.all_pixels_left_frame)
            self.all_pixels_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_all_pixels_results(self, results):
        self.all_pixels_ax.clear()
        bits = [r['bits'] for r in results]
        diffs = [r['diff_m'] for r in results]
        self.all_pixels_ax.plot(bits, diffs, 'r-o', linewidth=2, markersize=10)
        self.all_pixels_ax.set_xlabel('Количество битов в каждом пикселе')
        self.all_pixels_ax.set_ylabel('R-S разность (%)')
        self.all_pixels_ax.set_title('Биты во всех пикселях')
        self.all_pixels_ax.grid(True)
        self.all_pixels_ax.set_xticks(range(0, 9))
        self.all_pixels_canvas.draw()
        
        self.all_pixels_text.delete(1.0, tk.END)
        self.all_pixels_text.insert(tk.END, "=" * 55 + "\n")
        self.all_pixels_text.insert(tk.END, "БИТЫ ВО ВСЕХ ПИКСЕЛЯХ\n")
        self.all_pixels_text.insert(tk.END, "=" * 55 + "\n\n")
        self.all_pixels_text.insert(tk.END, f"{'Битов':<8} {'R-S':<12} {'Изменение':<12}\n")
        self.all_pixels_text.insert(tk.END, "-" * 35 + "\n")
        for r in results:
            self.all_pixels_text.insert(tk.END, f"{r['bits']:<8} {r['diff_m']:<12.4f} {r['change']:<12.4f}\n")
        
        if len(results) > 1:
            self.all_pixels_text.insert(tk.END, "\n" + "=" * 55 + "\n")
            self.all_pixels_text.insert(tk.END, "ВЫВОДЫ:\n")
            ch1 = results[1]['change'] if len(results) > 1 else 0
            ch8 = results[-1]['change'] if results else 0
            self.all_pixels_text.insert(tk.END, f"  • Падение после 1 бита (LSB): {ch1:.4f}%\n")
            self.all_pixels_text.insert(tk.END, f"  • Падение после 8 битов: {ch8:.4f}%\n")
            if ch1 > 0:
                self.all_pixels_text.insert(tk.END, f"  • Эффект сильнее в {ch8/ch1:.1f} раз\n")
    
    # ==================== ОБРАБОТКА ОШИБОК И КОПИРОВАНИЕ ====================
    
    def copy_to_clipboard(self, text_widget):
        """Копирует содержимое текстового виджета в буфер обмена"""
        try:
            content = text_widget.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_var.set("✅ Результаты скопированы в буфер обмена")
        except Exception as e:
            self.status_var.set(f"❌ Ошибка копирования: {e}")
    
    def _show_error(self, msg):
        messagebox.showerror("Ошибка", msg)
        self.status_var.set("Ошибка")


if __name__ == "__main__":
    root = tk.Tk()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    app = StegoAnalysisApp(root)
    root.mainloop()