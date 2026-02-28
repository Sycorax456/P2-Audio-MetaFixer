#!/usr/bin/env python3
"""
P3D Toolkit Compact - Multilingual
GUI switchable: English/Russian
Subtitle editor: Auto-detect all languages in P3D
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from pathlib import Path
import threading
import struct

# Traducciones del GUI
TRANSLATIONS = {
    'en': {
        'title': 'P3D Toolkit - Prototype 2',
        'converter': 'Hybrid Converter',
        'subtitle_editor': 'Subtitle Editor',
        'converter_title': 'Hybrid Converter - Prototype 2',
        'converter_subtitle': 'Original structure + your mod audio',
        'mode_info': 'Uses complete original structure (until RADP)\n'
                     'Replaces only compressed audio with your mod\n'
                     'Keeps subtitles, KEY and metadata from original',
        'folders': 'Folders',
        'originals': 'Originals:',
        'mods': 'Mods:',
        'output': 'Output:',
        'process': 'PROCESS FILES',
        'log': 'Log',
        'confirm_process': 'Process files in Hybrid P2 mode?',
        'confirm': 'Confirm',
        'error': 'Error',
        'select_folders': 'Select all folders',
        'completed': 'Completed',
        'processed': 'Processed',
        'saved_in': 'Saved in',
        'subtitle_title': 'Subtitle Editor',
        'open_p3d': 'Open P3D',
        'save': 'Save',
        'no_file': 'No file',
        'information': 'Information',
        'instructions_title': 'Instructions',
        'preview': 'PREVIEW Original',
        'editor': 'EDITOR',
        'restore': 'Restore',
        'confirm_save': 'Save changes?\nWill create _edited.p3d file',
        'success': 'Success',
        'file_loaded': 'File loaded correctly',
        'changes_saved': 'Changes saved',
        'no_changes': 'No changes',
        'modified': 'Modified',
        'languages': 'languages',
        'exceeds': 'EXCEEDS',
        'missing': 'Missing',
        'bytes': 'bytes',
        'no_subtitles': 'No subtitles found in file',
    },
    'ru': {
        'title': 'P3D Инструменты - Prototype 2',
        'converter': 'Гибридный конвертер',
        'subtitle_editor': 'Редактор субтитров',
        'converter_title': 'Гибридный конвертер - Prototype 2',
        'converter_subtitle': 'Оригинальная структура + аудио вашего мода',
        'mode_info': 'Использует полную оригинальную структуру (до RADP)\n'
                     'Заменяет только сжатое аудио вашим модом\n'
                     'Сохраняет субтитры, KEY и метаданные из оригинала',
        'folders': 'Папки',
        'originals': 'Оригиналы:',
        'mods': 'Моды:',
        'output': 'Выход:',
        'process': 'ОБРАБОТАТЬ ФАЙЛЫ',
        'log': 'Журнал',
        'confirm_process': 'Обработать файлы в режиме Гибрид P2?',
        'confirm': 'Подтвердить',
        'error': 'Ошибка',
        'select_folders': 'Выберите все папки',
        'completed': 'Завершено',
        'processed': 'Обработано',
        'saved_in': 'Сохранено в',
        'subtitle_title': 'Редактор субтитров',
        'open_p3d': 'Открыть P3D',
        'save': 'Сохранить',
        'no_file': 'Нет файла',
        'information': 'Информация',
        'instructions_title': 'Инструкции',
        'preview': 'ПРЕДПРОСМОТР Оригинал',
        'editor': 'РЕДАКТОР',
        'restore': 'Восстановить',
        'confirm_save': 'Сохранить изменения?\nБудет создан файл _edited.p3d',
        'success': 'Успех',
        'file_loaded': 'Файл загружен успешно',
        'changes_saved': 'Изменения сохранены',
        'no_changes': 'Нет изменений',
        'modified': 'Изменено',
        'languages': 'языков',
        'exceeds': 'ПРЕВЫШАЕТ',
        'missing': 'Не хватает',
        'bytes': 'байт',
        'no_subtitles': 'Субтитры не найдены в файле',
    }
}

# Iconos de idiomas
LANGUAGE_FLAGS = {
    'spanish': '🇪🇸 Español',
    'italian': '🇮🇹 Italiano',
    'french': '🇫🇷 Français',
    'english': '🇬🇧 English',
    'german': '🇩🇪 Deutsch',
    'russian': '🇷🇺 Русский',
}

class P3DToolkit:
    def __init__(self, root):
        self.root = root
        self.current_lang = 'en'
        self.root.title(TRANSLATIONS[self.current_lang]['title'])
        
        # Optimizado para 1280x720
        self.root.geometry("1260x680")
        self.root.minsize(1100, 600)
        
        # Variables
        self.original_folder = tk.StringVar()
        self.mod_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        # Subtítulos
        self.current_subtitle_file = None
        self.subtitle_data = None
        self.subtitle_languages = {}  # {lang_name: {data}}
        
        self.setup_ui()
        
    def t(self, key):
        """Traduce una clave"""
        return TRANSLATIONS[self.current_lang].get(key, key)
    
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variable para selector de idioma
        self.gui_lang_var = tk.StringVar(value='en')
        
        # Barra superior con selector de idioma
        top_bar = ttk.Frame(self.root, padding="5")
        top_bar.pack(fill=tk.X, side=tk.TOP)
        
        ttk.Label(top_bar, text="🌍 GUI Language:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(top_bar, text="🇬🇧 English", 
                       value='en', 
                       variable=self.gui_lang_var,
                       command=lambda: self.change_language('en')).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(top_bar, text="🇷🇺 Русский", 
                       value='ru',
                       variable=self.gui_lang_var,
                       command=lambda: self.change_language('ru')).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(top_bar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.top_title = ttk.Label(top_bar, text=self.t('title'), 
                                   font=('Arial', 11, 'bold'))
        self.top_title.pack(side=tk.LEFT, padx=10)
        
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña 1: Conversor
        self.converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_frame, text=f"🔄 {self.t('converter')}")
        self.create_converter_tab()
        
        # Pestaña 2: Editor
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text=f"📝 {self.t('subtitle_editor')}")
        self.create_subtitle_editor_tab()
    
    def change_language(self, lang):
        """Cambia el idioma del GUI"""
        self.current_lang = lang
        
        # Actualizar título
        self.root.title(self.t('title'))
        self.top_title.config(text=self.t('title'))
        
        # Actualizar pestañas
        self.notebook.tab(0, text=f"🔄 {self.t('converter')}")
        self.notebook.tab(1, text=f"📝 {self.t('subtitle_editor')}")
        
        # Recrear contenido
        for widget in self.converter_frame.winfo_children():
            widget.destroy()
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        
        self.create_converter_tab()
        self.create_subtitle_editor_tab()
        
        # Si hay archivo de subtítulos cargado, recrear pestañas
        if self.subtitle_languages:
            self.create_language_tabs()
    
    def create_converter_tab(self):
        """Pestaña del conversor"""
        # Canvas con scroll
        canvas = tk.Canvas(self.converter_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.converter_frame, orient="vertical", 
                                  command=canvas.yview)
        
        main_frame = ttk.Frame(canvas, padding="10")
        
        main_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame.columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(main_frame, text=self.t('converter_title'), 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 5))
        ttk.Label(main_frame, text=self.t('converter_subtitle'), 
                 font=('Arial', 9), foreground='#666').grid(row=1, column=0, pady=(0, 10))
        
        # Info
        info_box = ttk.LabelFrame(main_frame, text=f"ℹ️ {self.t('information')}", 
                                 padding="8")
        info_box.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(info_box, text=self.t('mode_info'), 
                 font=('Arial', 9), justify=tk.LEFT).pack(anchor=tk.W)
        
        # Carpetas
        folders_frame = ttk.LabelFrame(main_frame, 
                                      text=f"📁 {self.t('folders')}", 
                                      padding="8")
        folders_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        folders_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folders_frame, text=self.t('originals'), 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(folders_frame, textvariable=self.original_folder, 
                 width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(folders_frame, text="📂", width=3,
                  command=lambda: self.browse_folder(self.original_folder)).grid(
                      row=0, column=2)
        
        ttk.Label(folders_frame, text=self.t('mods'), 
                 font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(folders_frame, textvariable=self.mod_folder, 
                 width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(folders_frame, text="📂", width=3,
                  command=lambda: self.browse_folder(self.mod_folder)).grid(
                      row=1, column=2)
        
        ttk.Label(folders_frame, text=self.t('output'), 
                 font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(folders_frame, textvariable=self.output_folder, 
                 width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(folders_frame, text="📂", width=3,
                  command=lambda: self.browse_folder(self.output_folder)).grid(
                      row=2, column=2)
        
        # Botón
        ttk.Button(main_frame, text=f"▶️ {self.t('process')}", 
                  command=self.process_files,
                  width=30).grid(row=4, column=0, pady=10)
        
        # Progreso
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(main_frame, text="", font=('Arial', 8))
        self.progress_label.grid(row=6, column=0)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text=f"📋 {self.t('log')}", 
                                  padding="5")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=120,
                                                  font=('Courier', 8),
                                                  state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_subtitle_editor_tab(self):
        """Pestaña del editor de subtítulos"""
        # Canvas con scroll
        canvas = tk.Canvas(self.editor_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.editor_frame, orient="vertical", 
                                 command=canvas.yview)
        
        self.subtitle_main_frame = ttk.Frame(canvas, padding="10")
        
        self.subtitle_main_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), 
                                            window=self.subtitle_main_frame, 
                                            anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.subtitle_main_frame.columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(self.subtitle_main_frame, text=self.t('subtitle_title'), 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Botones
        file_frame = ttk.Frame(self.subtitle_main_frame)
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text=f"📂 {self.t('open_p3d')}", 
                  command=self.open_subtitle_file, width=20).pack(side=tk.LEFT, padx=5)
        
        self.subtitle_file_label = ttk.Label(file_frame, 
                                            text=self.t('no_file'), 
                                            foreground='gray', font=('Arial', 9))
        self.subtitle_file_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(file_frame, text=f"💾 {self.t('save')}", 
                  command=self.save_subtitles, width=20).pack(side=tk.RIGHT, padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(self.subtitle_main_frame, 
                                    text=f"ℹ️ {self.t('information')}", 
                                    padding="8")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.subtitle_info_label = ttk.Label(info_frame, text="", 
                                            font=('Courier', 8))
        self.subtitle_info_label.pack(anchor=tk.W)
        
        # Notebook para idiomas
        self.language_notebook = ttk.Notebook(self.subtitle_main_frame)
        self.language_notebook.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instrucciones iniciales
        instructions_frame = ttk.Frame(self.language_notebook, padding="20")
        self.language_notebook.add(instructions_frame, 
                                   text=f"📖 {self.t('instructions_title')}")
        
        if self.current_lang == 'en':
            instructions = """
📝 SUBTITLE EDITOR

1. Open a P3D file
2. The editor will AUTO-DETECT all languages in the file
3. A tab will be created for each language found
4. Edit subtitles in each tab
5. Save changes (creates _edited.p3d)

Supported languages:
• Spanish, Italian, French, English, German, Russian
            """
        else:
            instructions = """
📝 РЕДАКТОР СУБТИТРОВ

1. Откройте файл P3D
2. Редактор АВТОМАТИЧЕСКИ ОПРЕДЕЛИТ все языки в файле
3. Будет создана вкладка для каждого найденного языка
4. Редактируйте субтитры в каждой вкладке
5. Сохраните изменения (создаст _edited.p3d)

Поддерживаемые языки:
• Испанский, Итальянский, Французский, Английский, Немецкий, Русский
            """
        
        ttk.Label(instructions_frame, text=instructions, 
                 font=('Courier', 10), justify=tk.LEFT).pack(anchor=tk.W)
    
    # ===== FUNCIONES CONVERSOR =====
    
    def browse_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            self.log(f"✓ {folder}")
    
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
    
    def mode_hybrid(self, original_data, mod_data):
        radp_orig = original_data.find(b'RADP')
        radp_mod = mod_data.find(b'RADP')
        
        if radp_orig == -1 or radp_mod == -1:
            raise ValueError("RADP not found")
        
        self.log(f"    📍 RADP: 0x{radp_orig:08X} | 0x{radp_mod:08X}")
        
        result = bytearray()
        result.extend(original_data[0:radp_orig])
        result.extend(mod_data[radp_mod:])
        result[0x08:0x0C] = len(result).to_bytes(4, 'little')
        
        self.log(f"    📊 {len(original_data)} → {len(result)} bytes")
        
        return bytes(result)
    
    def process_files(self):
        if not all([self.original_folder.get(), self.mod_folder.get(), 
                   self.output_folder.get()]):
            messagebox.showerror(self.t('error'), self.t('select_folders'))
            return
        
        if not messagebox.askyesno(self.t('confirm'), 
                                   self.t('confirm_process')):
            return
        
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
    
    def process_thread(self):
        try:
            orig_path = Path(self.original_folder.get())
            mod_path = Path(self.mod_folder.get())
            out_path = Path(self.output_folder.get())
            
            out_path.mkdir(parents=True, exist_ok=True)
            
            mods = list(mod_path.glob("*.p3d")) + list(mod_path.glob("*.P3D"))
            
            if not mods:
                self.log("⚠️ No P3D files")
                return
            
            self.log(f"\n{'='*70}\n🎮 PROTOTYPE 2 - HYBRID MODE\n"
                    f"📁 {len(mods)} files\n{'='*70}\n")
            
            self.progress['maximum'] = len(mods)
            processed = skipped = errors = 0
            
            for i, mod_file in enumerate(mods):
                name = mod_file.name
                orig_file = orig_path / name
                out_file = out_path / name
                
                self.progress_label.config(text=f"{i+1}/{len(mods)}: {name}")
                self.log(f"[{i+1}/{len(mods)}] {name}")
                
                if not orig_file.exists():
                    self.log(f"  ⚠️ No original")
                    skipped += 1
                else:
                    try:
                        with open(orig_file, 'rb') as f:
                            orig_data = f.read()
                        with open(mod_file, 'rb') as f:
                            mod_data = f.read()
                        
                        result = self.mode_hybrid(orig_data, mod_data)
                        
                        with open(out_file, 'wb') as f:
                            f.write(result)
                        
                        self.log(f"  ✅ Done")
                        processed += 1
                        
                    except Exception as e:
                        self.log(f"  ❌ {str(e)}")
                        errors += 1
                
                self.progress['value'] = i + 1
                self.root.update_idletasks()
            
            self.log(f"\n{'='*70}\n✅ {self.t('processed')}: {processed}\n{'='*70}\n")
            self.progress_label.config(text=f"✅ {self.t('completed')}: {processed}")
            
            if processed > 0:
                messagebox.showinfo(self.t('completed'), 
                                  f"{self.t('processed')}: {processed}\n"
                                  f"{self.t('saved_in')}: {out_path}")
        
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            messagebox.showerror(self.t('error'), str(e))
    
    # ===== FUNCIONES EDITOR =====
    
    def open_subtitle_file(self):
        filepath = filedialog.askopenfilename(
            title="Open P3D",
            filetypes=[("P3D files", "*.p3d"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'rb') as f:
                self.subtitle_data = bytearray(f.read())
            
            self.current_subtitle_file = filepath
            self.subtitle_file_label.config(
                text=os.path.basename(filepath), 
                foreground='green')
            
            # Auto-detectar idiomas
            self.extract_all_subtitles()
            
            if not self.subtitle_languages:
                messagebox.showwarning(self.t('error'), 
                                     self.t('no_subtitles'))
                return
            
            # Actualizar info
            langs = ', '.join(self.subtitle_languages.keys())
            count = len(self.subtitle_languages)
            self.subtitle_info_label.config(
                text=f"Found {count} {self.t('languages')}: {langs}")
            
            # Crear pestañas
            self.create_language_tabs()
            
            messagebox.showinfo(self.t('success'), 
                              f"{self.t('file_loaded')}\n"
                              f"{count} {self.t('languages')}")
            
        except Exception as e:
            messagebox.showerror(self.t('error'), str(e))
    
    def extract_all_subtitles(self):
        """Auto-detecta TODOS los idiomas en el archivo"""
        self.subtitle_languages = {}
        
        # Buscar todos los idiomas posibles
        search_languages = [
            (b'spanish', 'spanish'),
            (b'italian', 'italian'),
            (b'french', 'french'),
            (b'english', 'english'),
            (b'german', 'german'),
            (b'russian', 'russian'),
        ]
        
        for marker, lang_name in search_languages:
            offset = self.subtitle_data.find(marker)
            
            if offset != -1:
                try:
                    len_offset = offset + len(marker) + 1
                    if len_offset + 4 <= len(self.subtitle_data):
                        text_len = struct.unpack('<I', 
                            self.subtitle_data[len_offset:len_offset+4])[0]
                        
                        text_offset = len_offset + 4
                        
                        if text_offset + text_len <= len(self.subtitle_data):
                            text_bytes = self.subtitle_data[
                                text_offset:text_offset+text_len]
                            
                            text = text_bytes.decode('utf-8', errors='replace')
                            
                            self.subtitle_languages[lang_name] = {
                                'text': text,
                                'original': text,
                                'length': text_len,
                                'offset': text_offset,
                                'editor': None,
                                'count_label': None,
                            }
                except:
                    continue
    
    def create_language_tabs(self):
        """Crea pestañas dinámicas para cada idioma encontrado"""
        # Limpiar pestañas excepto instrucciones
        for tab in self.language_notebook.tabs()[1:]:
            self.language_notebook.forget(tab)
        
        # Crear pestaña para cada idioma
        for lang_name, lang_data in sorted(self.subtitle_languages.items()):
            self.create_language_tab(lang_name, lang_data)
    
    def create_language_tab(self, lang_name, lang_data):
        """Crea una pestaña para un idioma"""
        tab_frame = ttk.Frame(self.language_notebook, padding="15")
        tab_label = LANGUAGE_FLAGS.get(lang_name, lang_name.capitalize())
        self.language_notebook.add(tab_frame, text=tab_label)
        
        tab_frame.columnconfigure(0, weight=1)
        
        # Info
        info_text = f"Offset: 0x{lang_data['offset']:08X} | " \
                   f"Length: {lang_data['length']} bytes"
        ttk.Label(tab_frame, text=info_text, 
                 font=('Courier', 9)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Preview
        ttk.Label(tab_frame, text=self.t('preview'), 
                 font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W)
        
        preview = scrolledtext.ScrolledText(tab_frame, height=4,
                                           font=('Arial', 9),
                                           state='disabled',
                                           bg='#f0f0f0')
        preview.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(2, 10))
        
        preview.config(state='normal')
        preview.insert('1.0', lang_data['original'])
        preview.config(state='disabled')
        
        # Editor
        ttk.Label(tab_frame, text=self.t('editor'), 
                 font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky=tk.W)
        
        editor = scrolledtext.ScrolledText(tab_frame, height=8,
                                          font=('Arial', 10))
        editor.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(2, 5))
        editor.insert('1.0', lang_data['original'])
        
        lang_data['editor'] = editor
        
        # Contador
        count_label = ttk.Label(tab_frame, text="", font=('Arial', 9))
        count_label.grid(row=5, column=0, sticky=tk.W, pady=(2, 10))
        
        lang_data['count_label'] = count_label
        
        editor.bind('<KeyRelease>', 
                   lambda e, ln=lang_name: self.update_subtitle_count(ln))
        
        # Botón restaurar
        ttk.Button(tab_frame, text=f"🔄 {self.t('restore')}", 
                  command=lambda ln=lang_name: self.restore_subtitle(ln)).grid(
                      row=6, column=0)
        
        self.update_subtitle_count(lang_name)
    
    def update_subtitle_count(self, lang_name):
        """Actualiza contador"""
        data = self.subtitle_languages[lang_name]
        editor = data['editor']
        label = data['count_label']
        
        if not editor or not label:
            return
        
        text = editor.get('1.0', 'end-1c')
        current = len(text.encode('utf-8'))
        original = data['length']
        
        if current > original:
            color = 'red'
            status = f"⚠️ {self.t('exceeds')} {current-original} {self.t('bytes')}"
        elif current < original - 10:
            color = 'orange'
            status = f"{self.t('missing')} {original-current} {self.t('bytes')}"
        else:
            color = 'green'
            status = "✅ OK"
        
        label.config(text=f"{current}/{original} {self.t('bytes')} | {status}", 
                    foreground=color)
    
    def restore_subtitle(self, lang_name):
        """Restaura subtítulo original"""
        data = self.subtitle_languages[lang_name]
        editor = data['editor']
        
        if editor:
            editor.delete('1.0', tk.END)
            editor.insert('1.0', data['original'])
            self.update_subtitle_count(lang_name)
    
    def save_subtitles(self):
        """Guarda cambios"""
        if not self.current_subtitle_file or not self.subtitle_data:
            messagebox.showerror(self.t('error'), "No file")
            return
        
        if not messagebox.askyesno(self.t('confirm'), 
                                   self.t('confirm_save')):
            return
        
        try:
            modified = 0
            
            for lang_name, data in self.subtitle_languages.items():
                editor = data['editor']
                if not editor:
                    continue
                
                new_text = editor.get('1.0', 'end-1c')
                
                if new_text != data['original']:
                    new_bytes = new_text.encode('utf-8')
                    
                    if len(new_bytes) > data['length']:
                        new_bytes = new_bytes[:data['length']]
                    elif len(new_bytes) < data['length']:
                        new_bytes += b'\x00' * (data['length'] - len(new_bytes))
                    
                    offset = data['offset']
                    length = data['length']
                    
                    self.subtitle_data[offset:offset+length] = new_bytes
                    
                    len_offset = offset - 4
                    self.subtitle_data[len_offset:len_offset+4] = struct.pack(
                        '<I', len(new_text.encode('utf-8')))
                    
                    modified += 1
            
            if modified == 0:
                messagebox.showinfo(self.t('information'), 
                                  self.t('no_changes'))
                return
            
            output = self.current_subtitle_file.replace('.p3d', '_edited.p3d')
            
            with open(output, 'wb') as f:
                f.write(self.subtitle_data)
            
            messagebox.showinfo(self.t('success'), 
                              f"{self.t('changes_saved')}\n"
                              f"{self.t('modified')}: {modified} {self.t('languages')}")
            
        except Exception as e:
            messagebox.showerror(self.t('error'), str(e))

def main():
    root = tk.Tk()
    app = P3DToolkit(root)
    root.mainloop()

if __name__ == "__main__":
    main()
