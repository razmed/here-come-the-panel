import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable
import os

class FolderView(ctk.CTkFrame):
    """Vue d'un dossier avec support des panels"""
    
    def __init__(self, parent, db, file_handler, folder_id: Optional[int], 
                 on_folder_open: Callable = None, notification_manager=None,
                 panel_type: str = 'interface_employes'):
        super().__init__(parent, fg_color="transparent")
        
        self.db = db
        self.file_handler = file_handler
        self.folder_id = folder_id
        self.on_folder_open = on_folder_open
        self.notification_manager = notification_manager
        self.panel_type = panel_type
        
        self.create_widgets()
        self.load_content()
    
    def create_widgets(self):
        """Créer les widgets"""
        self.create_breadcrumb()
        
        self.content_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray15"),
            corner_radius=15
        )
        self.content_scrollable.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_breadcrumb(self):
        """Créer le fil d'Ariane"""
        breadcrumb_frame = ctk.CTkFrame(
            self,
            height=50,
            fg_color=("#e7f3ff", "#1a3a52"),
            corner_radius=10
        )
        breadcrumb_frame.pack(fill="x", pady=(0, 10))
        breadcrumb_frame.pack_propagate(False)
        
        if self.folder_id is None:
            path = [{"id": None, "name": "🏠 Accueil"}]
        else:
            path = self.db.get_folder_path(self.folder_id)
            path.insert(0, {"id": None, "name": "🏠 Accueil"})
        
        for i, folder in enumerate(path):
            if i > 0:
                ctk.CTkLabel(
                    breadcrumb_frame,
                    text=" / ",
                    font=ctk.CTkFont(size=14),
                    text_color=("gray50", "gray60")
                ).pack(side="left")
            
            if i == len(path) - 1:
                ctk.CTkLabel(
                    breadcrumb_frame,
                    text=folder["name"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#1f538d", "#2563a8")
                ).pack(side="left", padx=15)
            else:
                link_button = ctk.CTkButton(
                    breadcrumb_frame,
                    text=folder["name"],
                    width=len(folder["name"]) * 8 + 20,
                    height=30,
                    font=ctk.CTkFont(size=12),
                    fg_color="transparent",
                    text_color=("#1f538d", "#2563a8"),
                    hover_color=("gray80", "gray40"),
                    command=lambda fid=folder["id"]: self.navigate_to(fid)
                )
                link_button.pack(side="left")
    
    def navigate_to(self, folder_id: Optional[int]):
        """Naviguer vers un dossier"""
        if self.on_folder_open:
            self.on_folder_open(folder_id)
    
    def load_content(self):
        """Charger le contenu du dossier pour le panel spécifique"""
        for widget in self.content_scrollable.winfo_children():
            widget.destroy()
        
        try:
            subfolders = self.db.get_subfolders(self.folder_id, self.panel_type)
            files = self.db.get_files_in_folder(self.folder_id) if self.folder_id else []
            
            if not subfolders and not files:
                self.show_empty_state()
                return
            
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
                    
        except Exception as e:
            print(f"❌ Erreur lors du chargement du contenu: {e}")
            self.show_error_state(str(e))
    
    def create_section_title(self, title: str, count: int):
        """Créer un titre de section"""
        section_frame = ctk.CTkFrame(self.content_scrollable, fg_color="transparent")
        section_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            section_frame,
            text=f"{title} ({count})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1f538d", "#2563a8"),
            anchor="w"
        ).pack(side="left")
    
    def create_folder_card(self, parent, folder: dict, row: int, col: int):
        """Créer une carte de dossier"""
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
            card.configure(border_color=("#1f538d", "#2563a8"))
        
        def on_leave(event):
            card.configure(border_color=("gray80", "gray40"))
        
        card.bind('<Button-1>', on_click)
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
    
    def create_file_card(self, parent, file: dict):
        """Créer une carte de fichier"""
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
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=lambda f=file: self.open_file_with_viewer(f)
        )
        action_button.pack(side="right", padx=15)
        
        card.bind('<Double-Button-1>', lambda e, f=file: self.open_file_with_viewer(f))
    
    def open_file_with_viewer(self, file: dict):
        """Ouvrir un fichier avec le bon viewer"""
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "❌ Le fichier n'existe plus")
            return
        
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        
        if self.notification_manager:
            try:
                self.notification_manager.show_app_notification(
                    "📂 Ouverture de fichier",
                    f"Ouverture de '{file['filename']}'"
                )
            except Exception as e:
                print(f"⚠️ Erreur notification: {e}")
        
        if extension == 'pdf':
            try:
                from ui.pdf_viewer import PDFViewer
                pdf_window = ctk.CTkToplevel(self.winfo_toplevel())
                PDFViewer(pdf_window, file['filepath'], file['filename'])
                print(f"✅ PDF ouvert dans le viewer intégré: {file['filename']}")
            except ImportError:
                messagebox.showerror(
                    "Erreur", 
                    "❌ Viewer PDF non disponible\n\nInstallez PyMuPDF: pip install PyMuPDF"
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible d'ouvrir le PDF:\n{e}")
                print(f"❌ Erreur ouverture PDF: {e}")
        else:
            success = self.file_handler.open_file(file['filepath'])
            if not success:
                messagebox.showerror("Erreur", "❌ Impossible d'ouvrir le fichier")
    
    def show_empty_state(self):
        """Afficher l'état vide"""
        empty_frame = ctk.CTkFrame(
            self.content_scrollable,
            fg_color="transparent"
        )
        empty_frame.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(
            empty_frame,
            text="📭",
            font=ctk.CTkFont(size=80)
        ).pack(pady=(50, 20))
        
        message = "Aucun contenu" if self.folder_id else "Bienvenue sur ce Panel"
        ctk.CTkLabel(
            empty_frame,
            text=message,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray40", "gray60")
        ).pack(pady=(0, 10))
        
        if self.folder_id is None:
            ctk.CTkLabel(
                empty_frame,
                text="Connectez-vous en tant qu'administrateur\npour ajouter des dossiers et fichiers",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray70")
            ).pack()
        else:
            ctk.CTkLabel(
                empty_frame,
                text="Ce dossier est vide",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray70")
            ).pack()
    
    def show_error_state(self, error_message: str):
        """Afficher l'état d'erreur"""
        error_frame = ctk.CTkFrame(
            self.content_scrollable,
            fg_color="transparent"
        )
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
        """Formater la taille d'un fichier"""
        if size == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"