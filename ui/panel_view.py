import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable
import os

class PanelView(ctk.CTkFrame):
    """Vue d'un panel - Affiche fichiers à la racine SANS dossier _root_"""
   
    PANEL_INFO = {
        'certification': {'name': 'Certification', 'icon': '📜', 'color': ('#28a745', '#1e7e34')},
        'entete': {'name': 'En-tête', 'icon': '📋', 'color': ('#1f538d', '#14375e')},
        'interface_emp': {'name': 'Interface Employés', 'icon': '👥', 'color': ('#17a2b8', '#138496')},
        'autre': {'name': 'Autre', 'icon': '📦', 'color': ('#6c757d', '#5a6268')}
    }
   
    def __init__(self, parent, db, file_handler, panel: str,
                 folder_id: Optional[int] = None,
                 on_folder_open: Callable = None,
                 notification_manager=None):
        super().__init__(parent, fg_color="transparent")
       
        self.db = db
        self.file_handler = file_handler
        self.panel = panel
        self.folder_id = folder_id
        self.on_folder_open = on_folder_open
        self.notification_manager = notification_manager
       
        self.panel_info = self.PANEL_INFO.get(panel, {
            'name': 'Inconnu',
            'icon': '📁',
            'color': ('#6c757d', '#5a6268')
        })
       
        self.view_mode = "grid"
       
        self.create_widgets()
        self.load_content()
   
    def create_widgets(self):
        """Créer widgets"""
        self.create_breadcrumb()
       
        self.content_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray15"),
            corner_radius=15
        )
        self.content_scrollable.pack(fill="both", expand=True, pady=(10, 0))
   
    def create_breadcrumb(self):
        """Créer fil d'Ariane"""
        breadcrumb_frame = ctk.CTkFrame(
            self,
            height=60,
            fg_color=(self.panel_info['color'][0], self.panel_info['color'][1]),
            corner_radius=10
        )
        breadcrumb_frame.pack(fill="x", pady=(0, 10))
        breadcrumb_frame.pack_propagate(False)
       
        content_container = ctk.CTkFrame(breadcrumb_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=20)
       
        header_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        header_frame.pack(side="left", pady=15)
       
        ctk.CTkLabel(
            header_frame,
            text=f"{self.panel_info['icon']} {self.panel_info['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(side="left")
       
        if self.folder_id is not None:
            path = self.db.get_folder_path(self.folder_id)
           
            if path:
                ctk.CTkLabel(
                    header_frame,
                    text=" / ",
                    font=ctk.CTkFont(size=16),
                    text_color=("white", "white")
                ).pack(side="left", padx=5)
               
                for i, folder in enumerate(path):
                    if i > 0:
                        ctk.CTkLabel(
                            header_frame,
                            text=" / ",
                            font=ctk.CTkFont(size=16),
                            text_color=("white", "white")
                        ).pack(side="left", padx=5)
                   
                    if i == len(path) - 1:
                        ctk.CTkLabel(
                            header_frame,
                            text=folder["name"],
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color=("#ffeb3b", "#ffc107")
                        ).pack(side="left")
                    else:
                        link_btn = ctk.CTkButton(
                            header_frame,
                            text=folder["name"],
                            width=len(folder["name"]) * 8 + 20,
                            height=25,
                            font=ctk.CTkFont(size=14),
                            fg_color="transparent",
                            text_color="white",
                            hover_color=("gray80", "gray40"),
                            command=lambda fid=folder["id"]: self.navigate_to(fid)
                        )
                        link_btn.pack(side="left")
       
        view_switch_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        view_switch_frame.pack(side="right", pady=15, padx=20)
       
        self.view_switch = ctk.CTkSwitch(
            view_switch_frame,
            text="Vue Liste" if self.view_mode == "list" else "Vue Grille",
            command=self.toggle_view_mode
        )
        self.view_switch.pack()
        if self.view_mode == "list":
            self.view_switch.select()

    def toggle_view_mode(self):
        """Toggle vue"""
        self.view_mode = "list" if self.view_switch.get() else "grid"
        self.view_switch.configure(text="Vue Liste" if self.view_mode == "list" else "Vue Grille")
        self.load_content()

    def navigate_to(self, folder_id: Optional[int]):
        """Naviguer"""
        if self.on_folder_open:
            self.on_folder_open(folder_id)
   
    def load_content(self):
        """✅ CORRECTION CRITIQUE : Charger contenu en excluant _root_*"""
        for widget in self.content_scrollable.winfo_children():
            widget.destroy()
       
        try:
            # Charger sous-dossiers (EXCLURE _root_*)
            subfolders = self.db.get_subfolders(self.folder_id, panel=self.panel if self.folder_id is None else None)
            
            # ✅ FILTRER _root_*
            subfolders = [f for f in subfolders if not f['name'].startswith('_root_')]
           
            # Charger fichiers
            files = []
            if self.folder_id is not None:
                # Fichiers du dossier courant
                files = self.db.get_files_in_folder(self.folder_id)
            else:
                # ✅ IMPORTANT : Fichiers de la racine (dossier _root_* inclus)
                all_folders = self.db.get_subfolders(None, panel=self.panel)
                
                # Récupérer fichiers du dossier _root_* uniquement
                root_folder = next((f for f in all_folders if f['name'].startswith('_root_')), None)
                if root_folder:
                    files = self.db.get_files_in_folder(root_folder['id'])
           
            if not subfolders and not files:
                self.show_empty_state()
                return
           
            if self.view_mode == "grid":
                self.load_grid_view(subfolders, files)
            else:
                self.load_list_view(subfolders, files)
           
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            self.show_error_state(str(e))
   
    def load_grid_view(self, subfolders: list, files: list):
        """Vue grille"""
        if subfolders:
            self.create_section_title("📁 Dossiers", len(subfolders))
           
            folders_grid = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
            folders_grid.pack(fill="x", pady=(10, 20))
           
            for i, folder in enumerate(subfolders):
                row = i // 4
                col = i % 4
                self.create_folder_card(folders_grid, folder, row, col)
       
        if files:
            self.create_section_title("📄 Fichiers", len(files))
           
            files_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
            files_frame.pack(fill="x", pady=10)
           
            for file in files:
                self.create_file_card(files_frame, file)

    def load_list_view(self, subfolders: list, files: list):
        """Vue liste"""
        list_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
        list_frame.pack(fill="x", pady=10)
       
        for folder in subfolders:
            self.create_folder_list_item(list_frame, folder)
       
        for file in files:
            self.create_file_list_item(list_frame, file)

    def create_folder_list_item(self, parent, folder: dict):
        """Carte dossier liste"""
        card = ctk.CTkFrame(
            parent,
            height=60,
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray40")
        )
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)
       
        ctk.CTkLabel(
            card,
            text="📁",
            font=ctk.CTkFont(size=24),
            width=50
        ).pack(side="left", padx=10)
       
        ctk.CTkLabel(
            card,
            text=folder['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(side="left", expand=True)
       
        file_count = self.db.count_files_in_folder(folder['id'], recursive=True)
        ctk.CTkLabel(
            card,
            text=f"{file_count} fichiers",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        ).pack(side="right", padx=10)
       
        card.bind('<Button-1>', lambda e: self.navigate_to(folder['id']))

    def create_file_list_item(self, parent, file: dict):
        """Carte fichier liste"""
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        icon = self.file_handler.get_file_icon(extension)
       
        card = ctk.CTkFrame(
            parent,
            height=60,
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray40")
        )
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)
       
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=50
        ).pack(side="left", padx=10)
       
        ctk.CTkLabel(
            card,
            text=file['filename'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(side="left", expand=True)
       
        size_formatted = self.format_file_size(file.get('file_size', 0))
        ctk.CTkLabel(
            card,
            text=size_formatted,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        ).pack(side="right", padx=10)
       
        card.bind('<Button-1>', lambda e: self.open_file_with_viewer(file))
   
    def create_section_title(self, title: str, count: int):
        """Titre section"""
        section_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
        section_frame.pack(fill="x", pady=(20, 10))
       
        ctk.CTkLabel(
            section_frame,
            text=f"{title} ({count})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(self.panel_info['color'][0], self.panel_info['color'][1]),
            anchor="w"
        ).pack(side="left")
   
    def create_folder_card(self, parent, folder: dict, row: int, col: int):
        """Carte dossier"""
        card = ctk.CTkFrame(
            parent,
            width=300,
            height=120,
            fg_color=("white", "gray20"),
            corner_radius=15,
            border_width=2,
            border_color=("gray80", "gray40")
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="w")
        card.pack_propagate(False)
       
        try:
            parent.grid_columnconfigure(col, weight=1)
        except:
            pass
       
        ctk.CTkLabel(
            card,
            text="📁",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(15, 5))
       
        ctk.CTkLabel(
            card,
            text=folder['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=280
        ).pack(pady=(0, 5))
       
        try:
            file_count = self.db.count_files_in_folder(folder['id'], recursive=True)
        except:
            file_count = 0
           
        ctk.CTkLabel(
            card,
            text=f"{file_count} fichier{'s' if file_count != 1 else ''}",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        ).pack()
       
        def on_click(event, fid=folder['id']):
            self.navigate_to(fid)
       
        def on_enter(event):
            card.configure(border_color=(self.panel_info['color'][0], self.panel_info['color'][1]))
       
        def on_leave(event):
            card.configure(border_color=("gray80", "gray40"))
       
        card.bind('<Button-1>', on_click)
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
   
    def create_file_card(self, parent, file: dict):
        """Carte fichier"""
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        icon = self.file_handler.get_file_icon(extension)
        is_pdf = extension == 'pdf'
       
        card = ctk.CTkFrame(
            parent,
            height=80,
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray40")
        )
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)
       
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28),
            width=70
        ).pack(side="left", padx=15)
       
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=15)
       
        name_label = ctk.CTkLabel(
            info_frame,
            text=file['filename'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x")
       
        try:
            size = file.get('file_size', 0)
            if size == 0 and os.path.exists(file['filepath']):
                size = os.path.getsize(file['filepath'])
            size_formatted = self.format_file_size(size)
        except:
            size_formatted = "N/A"
       
        type_text = f"{size_formatted} • {'🔒 PDF (Lecture seule)' if is_pdf else '💾 Téléchargeable'}"
       
        meta_label = ctk.CTkLabel(
            info_frame,
            text=type_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        meta_label.pack(fill="x")
       
        action_text = "👁️ Visualiser" if is_pdf else "📥 Ouvrir"
        action_button = ctk.CTkButton(
            card,
            text=action_text,
            width=130,
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=(self.panel_info['color'][0], self.panel_info['color'][1]),
            hover_color=("gray60", "gray40"),
            command=lambda f=file: self.open_file_with_viewer(f)
        )
        action_button.pack(side="right", padx=15)
       
        card.bind('<Double-Button-1>', lambda e, f=file: self.open_file_with_viewer(f))
   
    def open_file_with_viewer(self, file: dict):
        """Ouvrir fichier"""
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "❌ Fichier n'existe plus")
            return
       
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
       
        if self.notification_manager:
            try:
                self.notification_manager.show_app_notification(
                    "📂 Ouverture",
                    f"Ouverture de '{file['filename']}'"
                )
            except Exception as e:
                print(f"⚠️ Erreur notification: {e}")
       
        if extension == 'pdf':
            try:
                from .pdf_viewer import PDFViewer
                pdf_window = ctk.CTkToplevel(self.winfo_toplevel())
                PDFViewer(pdf_window, file['filepath'], file['filename'])
                print(f"✅ PDF ouvert: {file['filename']}")
            except ImportError:
                messagebox.showerror("Erreur", "❌ Viewer PDF non disponible")
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible d'ouvrir:\n{e}")
                print(f"❌ Erreur PDF: {e}")
        else:
            success = self.file_handler.open_file(file['filepath'])
            if not success:
                messagebox.showerror("Erreur", "❌ Impossible d'ouvrir")
   
    def show_empty_state(self):
        """État vide"""
        empty_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=100)
       
        ctk.CTkLabel(
            empty_frame,
            text=self.panel_info['icon'],
            font=ctk.CTkFont(size=80)
        ).pack(pady=(50, 20))
       
        ctk.CTkLabel(
            empty_frame,
            text=f"Aucun contenu dans {self.panel_info['name']}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray40", "gray60")
        ).pack(pady=(0, 10))
       
        ctk.CTkLabel(
            empty_frame,
            text="Connectez-vous en admin\npour ajouter des fichiers",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        ).pack()
   
    def show_error_state(self, error_message: str):
        """État erreur"""
        error_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
        error_frame.pack(fill="both", expand=True, pady=100)
       
        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=ctk.CTkFont(size=80)
        ).pack(pady=(50, 20))
       
        ctk.CTkLabel(
            error_frame,
            text="Erreur de chargement",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#dc3545", "#e04555")
        ).pack(pady=(0, 10))
       
        ctk.CTkLabel(
            error_frame,
            text=error_message,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            wraplength=600
        ).pack()
   
    @staticmethod
    def format_file_size(size: int) -> str:
        """Formater taille"""
        if size == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
