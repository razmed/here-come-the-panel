import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES
from typing import Callable, Optional
import os
import re

class AdminWindow:
    """Fenêtre d'administration - Import direct sans dossier racine"""
   
    PANEL_INFO = {
        'certification': {'name': 'Certification', 'icon': '📜', 'color': '#28a745'},
        'entete': {'name': 'En-tête', 'icon': '📋', 'color': '#1f538d'},
        'interface_emp': {'name': 'Interface Employés', 'icon': '👥', 'color': '#17a2b8'},
        'autre': {'name': 'Autre', 'icon': '📦', 'color': '#6c757d'}
    }
   
    def __init__(self, root: ctk.CTkToplevel, db, file_handler, panel: str, on_changes: Callable):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.panel = panel
        self.on_changes = on_changes
       
        self.panel_info = self.PANEL_INFO.get(panel, {
            'name': 'Inconnu',
            'icon': '📁',
            'color': '#6c757d'
        })
       
        self.root.title(f"Administration - {self.panel_info['name']}")
        self.root.geometry("1100x750")
       
        self.center_window()
        self.create_widgets()
        self.load_folders()
   
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = 1100
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
   
    def create_widgets(self):
        """Créer les widgets"""
        header = ctk.CTkFrame(
            self.root,
            height=80,
            corner_radius=0,
            fg_color=(self.panel_info['color'], self.panel_info['color'])
        )
        header.pack(fill="x")
        header.pack_propagate(False)
       
        title_label = ctk.CTkLabel(
            header,
            text=f"{self.panel_info['icon']} Gestion - {self.panel_info['name']}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=30, pady=20)
       
        close_button = ctk.CTkButton(
            header,
            text="✖️ Fermer",
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=self.root.destroy
        )
        close_button.pack(side="right", padx=30)
       
        dragdrop_container = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        dragdrop_container.pack(fill="x", padx=20, pady=20)
       
        dragdrop_frame = ctk.CTkFrame(
            dragdrop_container,
            height=160,
            corner_radius=15,
            fg_color=("#e7f3ff", "#1a3a52"),
            border_width=3,
            border_color=("#0066cc", "#0088ee")
        )
        dragdrop_frame.pack(fill="x")
        dragdrop_frame.pack_propagate(False)
       
        ctk.CTkLabel(
            dragdrop_frame,
            text="📦 Zone Drag & Drop Universelle",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0066cc", "#00aaff")
        ).pack(pady=(15, 10))
       
        self.drop_zone = ctk.CTkLabel(
            dragdrop_frame,
            text="⬇️ Glissez-déposez ici:\n\n"
                 "📁 UN OU PLUSIEURS DOSSIERS → Import complet avec arborescence\n"
                 "📄 UN OU PLUSIEURS FICHIERS → Import direct à la racine\n\n"
                 "✅ Formats acceptés: .docx, .pdf, .xlsx",
            font=ctk.CTkFont(size=13),
            fg_color=("#ffffff", "#2a4a5a"),
            corner_radius=10,
            height=90,
            cursor="hand2"
        )
        self.drop_zone.pack(fill="x", padx=20, pady=(0, 15))
       
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_zone.bind('<Button-1>', lambda e: self.show_import_menu())
       
        toolbar = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        toolbar.pack(fill="x", padx=20, pady=(0, 15))
       
        button_data = [
            ("➕ Nouveau Dossier", "#28a745", "#1e7e34", self.create_folder),
            ("📂 Importer Dossier", "#1f538d", "#14375e", self.import_folder),
            ("📄 Importer Fichiers", "#17a2b8", "#138496", self.import_files),
            ("🔄 Rafraîchir", "#6c757d", "#5a6268", self.load_folders)
        ]
       
        for text, fg_color, hover_color, command in button_data:
            btn = ctk.CTkButton(
                toolbar,
                text=text,
                width=160,
                height=45,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=fg_color,
                hover_color=hover_color,
                command=command
            )
            btn.pack(side="left", padx=5)
       
        list_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
       
        self.folders_list = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=("#f0f0f0", "#2b2b2b"),
            corner_radius=15
        )
        self.folders_list.pack(fill="both", expand=True)
   
    def load_folders(self):
        """Charger les dossiers du panel (en excluant _root_*)"""
        for widget in self.folders_list.winfo_children():
            widget.destroy()
       
        root_folders = self.db.get_subfolders(None, panel=self.panel)
        
        # ✅ FILTRER les dossiers _root_*
        visible_folders = [f for f in root_folders if not f['name'].startswith('_root_')]
        
        # ✅ RÉCUPÉRER les fichiers du dossier _root_* pour affichage
        root_folder = next((f for f in root_folders if f['name'].startswith('_root_')), None)
        root_files = []
        if root_folder:
            root_files = self.db.get_files_in_folder(root_folder['id'])
       
        if not visible_folders and not root_files:
            ctk.CTkLabel(
                self.folders_list,
                text=f"📭 Aucun contenu dans {self.panel_info['name']}\n\nCommencez par créer ou importer un dossier",
                font=ctk.CTkFont(size=16),
                text_color=("gray50", "gray60")
            ).pack(expand=True, pady=100)
            return
       
        # ✅ AFFICHER les fichiers de la racine EN PREMIER
        if root_files:
            root_label = ctk.CTkLabel(
                self.folders_list,
                text="📄 Fichiers à la racine",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#1f538d", "#2563a8"),
                anchor="w"
            )
            root_label.pack(fill="x", padx=15, pady=(10, 5))
            
            for file in root_files:
                self.insert_file_card(self.folders_list, file, root_folder['id'])
        
        # ✅ AFFICHER les dossiers visibles
        if visible_folders:
            folders_label = ctk.CTkLabel(
                self.folders_list,
                text="📁 Dossiers",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#1f538d", "#2563a8"),
                anchor="w"
            )
            folders_label.pack(fill="x", padx=15, pady=(20, 5))
            
            for folder in visible_folders:
                self.insert_folder_card(self.folders_list, folder, level=0)
   
    def insert_folder_card(self, parent, folder: dict, level: int):
        """Insérer une carte de dossier AVEC SES FICHIERS"""
        card = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e1e1e"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        card.pack(fill="x", padx=(level * 30 + 10, 10), pady=5)
       
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
       
        left_frame = ctk.CTkFrame(inner, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
       
        name_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        name_frame.pack(side="left")
       
        subfolders = self.db.get_subfolders(folder['id'])
        has_subfolders = len(subfolders) > 0
        
        # ✅ RÉCUPÉRER LES FICHIERS DU DOSSIER
        folder_files = self.db.get_files_in_folder(folder['id'])
       
        if has_subfolders or folder_files:
            expanded = ctk.BooleanVar(value=True)
            chevron = ctk.CTkLabel(
                name_frame,
                text='▼',
                font=ctk.CTkFont(size=18),
                cursor="hand2"
            )
            chevron.pack(side="left", padx=(0, 5))
           
            children_container = ctk.CTkFrame(parent, fg_color="transparent")
           
            def toggle_expand():
                exp = not expanded.get()
                expanded.set(exp)
                chevron.configure(text='▼' if exp else '▶')
                if exp:
                    children_container.pack(fill="x", pady=0, after=card)
                else:
                    children_container.pack_forget()
            
            chevron.bind("<Button-1>", lambda e: toggle_expand())
           
            if expanded.get():
                children_container.pack(fill="x", pady=0, after=card)
           
            # ✅ AFFICHER LES FICHIERS DU DOSSIER EN PREMIER
            if folder_files:
                for file in folder_files:
                    self.insert_file_card(children_container, file, folder['id'], level + 1)
            
            # ✅ AFFICHER LES SOUS-DOSSIERS APRÈS
            for subfolder in subfolders:
                self.insert_folder_card(children_container, subfolder, level + 1)
       
        ctk.CTkLabel(
            name_frame,
            text="📁",
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))
       
        info_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        info_frame.pack(side="left")
       
        ctk.CTkLabel(
            info_frame,
            text=folder['name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
       
        file_count = self.db.count_files_in_folder(folder['id'], recursive=True)
        ctk.CTkLabel(
            info_frame,
            text=f"{file_count} fichier{'s' if file_count > 1 else ''} • ID: {folder['id']}",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w"
        ).pack(anchor="w")
       
        button_frame = ctk.CTkFrame(inner, fg_color="transparent")
        button_frame.pack(side="right")
       
        buttons_data = [
            ("➕", "#28a745", "#1e7e34", lambda f=folder: self.add_subfolder(f['id'])),
            ("✏️", "#ffc107", "#e0a800", lambda f=folder: self.rename_folder(f['id'])),
            ("📄", "#17a2b8", "#138496", lambda f=folder: self.manage_files(f['id'])),
            ("🗑️", "#dc3545", "#b02a37", lambda f=folder: self.delete_folder(f['id']))
        ]
       
        for text, fg_color, hover_color, command in buttons_data:
            ctk.CTkButton(
                button_frame,
                text=text,
                width=45,
                height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=fg_color,
                hover_color=hover_color,
                command=command
            ).pack(side="left", padx=2)
    
    def insert_file_card(self, parent, file: dict, folder_id: int, level: int = 0):
        """✅ NOUVELLE MÉTHODE : Insérer une carte de fichier dans la liste"""
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        icon = self.file_handler.get_file_icon(extension)
        
        card = ctk.CTkFrame(
            parent,
            height=70,
            fg_color=("#f8f9fa", "#2a2a2a"),
            corner_radius=8,
            border_width=1,
            border_color=("gray70", "gray40")
        )
        card.pack(fill="x", padx=(level * 30 + 30, 10), pady=3)
        card.pack_propagate(False)
        
        # Icône du fichier
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=60
        ).pack(side="left", padx=10)
        
        # Informations du fichier
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=file['filename'],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        # Taille du fichier
        try:
            size = file.get('file_size', 0)
            if size == 0 and os.path.exists(file['filepath']):
                size = os.path.getsize(file['filepath'])
            size_formatted = self.format_file_size(size)
        except:
            size_formatted = "N/A"
        
        is_pdf = self.file_handler.is_pdf(file['filename'])
        type_text = f"{size_formatted} • {'🔒 PDF' if is_pdf else '💾 Téléchargeable'}"
        
        ctk.CTkLabel(
            info_frame,
            text=type_text,
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"),
            anchor="w"
        ).pack(anchor="w")
        
        # Boutons d'action
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(side="right", padx=10)
        
        # Bouton Ouvrir
        ctk.CTkButton(
            button_frame,
            text="👁️",
            width=35,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=lambda: self.open_file_direct(file)
        ).pack(side="left", padx=2)
        
        # Bouton Supprimer
        ctk.CTkButton(
            button_frame,
            text="🗑️",
            width=35,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=lambda: self.delete_file_direct(file, folder_id)
        ).pack(side="left", padx=2)
    
    def open_file_direct(self, file: dict):
        """✅ Ouvrir un fichier directement"""
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "❌ Le fichier n'existe plus")
            return
        
        success = self.file_handler.open_file(file['filepath'])
        if not success:
            messagebox.showerror("Erreur", "❌ Impossible d'ouvrir le fichier")
    
    def delete_file_direct(self, file: dict, folder_id: int):
        """✅ Supprimer un fichier directement"""
        response = messagebox.askyesno(
            "Confirmation",
            f"⚠️ Supprimer le fichier:\n\n{file['filename']} ?",
            icon='warning'
        )
        
        if response:
            try:
                self.db.delete_file(file['id'])
                messagebox.showinfo("Succès", "✅ Fichier supprimé")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible de supprimer:\n{e}")
    
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
   
    def parse_drop_paths(self, data: str) -> list:
        """Parser robuste pour chemins multiples"""
        paths = []
        data = data.strip()
        
        if '{' in data and '}' in data:
            pattern = r'\{([^}]+)\}'
            matches = re.findall(pattern, data)
            if matches:
                paths = [m.strip() for m in matches]
        elif ' ' in data and not ('{' in data or '}' in data):
            parts = data.split()
            temp_path = ""
            for part in parts:
                temp_path += part
                if os.path.exists(temp_path):
                    paths.append(temp_path)
                    temp_path = ""
                else:
                    temp_path += " "
            if temp_path.strip() and os.path.exists(temp_path.strip()):
                paths.append(temp_path.strip())
        elif data.startswith('{') and data.endswith('}'):
            path = data[1:-1].strip()
            if path:
                paths = [path]
        else:
            if data:
                paths = [data]
        
        valid_paths = []
        for path in paths:
            path = path.strip().strip('{}').strip()
            if path and os.path.exists(path):
                valid_paths.append(path)
        
        return valid_paths
   
    def on_drop(self, event):
        """Handler universel pour drop"""
        try:
            paths_raw = event.data
            paths = self.parse_drop_paths(paths_raw)
            
            if not paths:
                messagebox.showwarning("Attention", "❌ Aucun élément valide")
                return
            
            folders = [p for p in paths if os.path.isdir(p)]
            files = [p for p in paths if os.path.isfile(p)]
            
            if folders:
                for folder_path in folders:
                    self.import_folder_confirmed(folder_path)
            
            if files:
                self.import_files_to_root_direct(files)
        
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur:\n\n{e}")
            import traceback
            traceback.print_exc()
   
    def import_folder_confirmed(self, folder_path: str):
        """Importer un dossier après confirmation"""
        folder_name = os.path.basename(folder_path)
        response = messagebox.askyesno(
            "Confirmation",
            f"📁 Importer le dossier :\n\n{folder_name}\n\n"
            f"✅ Panel: {self.panel_info['name']}\n"
            "✅ Tous les fichiers\n"
            "✅ L'arborescence complète",
            icon='question'
        )
       
        if response:
            self.import_folder_path(folder_path)
   
    def import_files_to_root_direct(self, file_paths: list):
        """✅ Import direct SANS CRÉER DE DOSSIER"""
        try:
            valid_files = [f for f in file_paths if self.file_handler.is_allowed_file(os.path.basename(f))]
           
            if not valid_files:
                messagebox.showwarning("Attention", "⚠️ Aucun fichier valide")
                return
           
            print(f"\n📦 IMPORT DIRECT: {len(valid_files)} FICHIER(S)")
           
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Importation...")
            progress_window.geometry("600x250")
            progress_window.transient(self.root)
            progress_window.grab_set()
           
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - 300
            y = (progress_window.winfo_screenheight() // 2) - 125
            progress_window.geometry(f'600x250+{x}+{y}')
           
            ctk.CTkLabel(
                progress_window,
                text="⏳ Importation...",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#1f538d", "#00aaff")
            ).pack(pady=20)
           
            progress_bar = ctk.CTkProgressBar(progress_window, width=500, height=20)
            progress_bar.pack(pady=10)
            progress_bar.set(0)
           
            status_label = ctk.CTkLabel(
                progress_window,
                text=f"Traitement... (0/{len(valid_files)})",
                font=ctk.CTkFont(size=14)
            )
            status_label.pack(pady=10)
            progress_window.update()
           
            # ✅ CRÉER OU RÉCUPÉRER LE DOSSIER VIRTUEL _root_
            root_folder_name = f"_root_{self.panel}"
            root_folders = self.db.get_subfolders(None, panel=self.panel)
            root_folder = next((f for f in root_folders if f['name'] == root_folder_name), None)
            
            if not root_folder:
                root_folder_id = self.db.create_folder(root_folder_name, None, self.panel)
                print(f"✅ Dossier virtuel créé: {root_folder_name} (ID: {root_folder_id})")
            else:
                root_folder_id = root_folder['id']
                print(f"✅ Dossier virtuel existant: {root_folder_name} (ID: {root_folder_id})")
            
            success_count = 0
            error_count = 0
            
            for i, file_path in enumerate(valid_files):
                filename = os.path.basename(file_path)
               
                try:
                    # Copier dans uploads/
                    dest_path = os.path.join(self.file_handler.upload_dir, filename)
                    
                    # Gérer doublons
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(os.path.join(self.file_handler.upload_dir, f"{base}_{counter}{ext}")):
                            counter += 1
                        filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(self.file_handler.upload_dir, filename)
                    
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    
                    # Ajouter en BDD avec le dossier virtuel
                    self.db.add_file(root_folder_id, filename, dest_path)
                    success_count += 1
                    print(f"   ✅ {filename}")
                
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ {filename}: {e}")
               
                progress = (i + 1) / len(valid_files)
                progress_bar.set(progress)
                status_label.configure(text=f"Traitement... ({i+1}/{len(valid_files)})")
                progress_window.update_idletasks()
           
            progress_window.destroy()
           
            if error_count == 0:
                messagebox.showinfo(
                    "Succès",
                    f"✅ Import réussi!\n\n📊 {success_count} fichier(s)"
                )
            else:
                messagebox.showwarning(
                    "Attention",
                    f"✅ {success_count} importé(s)\n❌ {error_count} erreur(s)"
                )
           
            self.load_folders()
            self.on_changes()
           
        except Exception as e:
            if 'progress_window' in locals():
                try:
                    progress_window.destroy()
                except:
                    pass
            messagebox.showerror("Erreur", f"❌ Impossible:\n\n{e}")
            import traceback
            traceback.print_exc()
   
    def show_import_menu(self):
        """Menu d'import"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("Importation")
        menu.geometry("400x300")
        menu.transient(self.root)
        menu.grab_set()
       
        menu.update_idletasks()
        x = (menu.winfo_screenwidth() // 2) - 200
        y = (menu.winfo_screenheight() // 2) - 150
        menu.geometry(f'400x300+{x}+{y}')
       
        ctk.CTkLabel(
            menu,
            text="📦 Type d'import",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=30)
       
        ctk.CTkButton(
            menu,
            text="📁 Importer un Dossier",
            width=300,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=lambda: [menu.destroy(), self.import_folder()]
        ).pack(pady=10)
       
        ctk.CTkButton(
            menu,
            text="📄 Importer des Fichiers",
            width=300,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#17a2b8", "#138496"),
            hover_color=("#20a9cc", "#1e91a6"),
            command=lambda: [menu.destroy(), self.import_files()]
        ).pack(pady=10)
   
    def import_folder_path(self, folder_path: str):
        """Importer un dossier"""
        try:
            total_files = self.file_handler.count_files_to_import(folder_path)
            if total_files == 0:
                messagebox.showwarning("Attention", "⚠️ Aucun fichier valide")
                return
           
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Importation...")
            progress_window.geometry("600x300")
            progress_window.transient(self.root)
            progress_window.grab_set()
           
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - 300
            y = (progress_window.winfo_screenheight() // 2) - 150
            progress_window.geometry(f'600x300+{x}+{y}')
           
            ctk.CTkLabel(
                progress_window,
                text="⏳ Importation...",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#1f538d", "#00aaff")
            ).pack(pady=20)
           
            self.progress_bar = ctk.CTkProgressBar(progress_window, width=500, height=20, mode="determinate")
            self.progress_bar.pack(pady=10)
            self.progress_bar.set(0)
           
            self.status_label = ctk.CTkLabel(
                progress_window,
                text=f"Préparation... (0/{total_files})",
                font=ctk.CTkFont(size=14)
            )
            self.status_label.pack(pady=10)
            progress_window.update()
           
            def progress_callback(current, total):
                progress = current / total
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Importation... ({current}/{total})")
                progress_window.update_idletasks()
           
            count = self.file_handler.save_files_from_folder_with_panel(
                folder_path, self.db, None, self.panel, progress_callback=progress_callback, total=total_files
            )
           
            progress_window.destroy()
           
            if count > 0:
                messagebox.showinfo(
                    "Succès",
                    f"✅ Importation réussie!\n\n📊 {count} fichier(s)\n📁 {os.path.basename(folder_path)}"
                )
            else:
                messagebox.showwarning("Attention", "⚠️ Aucun fichier importé")
           
            self.load_folders()
            self.on_changes()
           
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror("Erreur", f"❌ Impossible:\n\n{e}")
            import traceback
            traceback.print_exc()
   
    def create_folder(self):
        """Créer un dossier"""
        dialog = ctk.CTkInputDialog(
            text=f"Nom du dossier dans {self.panel_info['name']}:",
            title="Nouveau Dossier"
        )
        name = dialog.get_input()
       
        if name and name.strip():
            try:
                self.db.create_folder(name.strip(), None, self.panel)
                messagebox.showinfo("Succès", "✅ Dossier créé")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def add_subfolder(self, parent_id: int):
        """Ajouter sous-dossier"""
        dialog = ctk.CTkInputDialog(text="Nom du sous-dossier:", title="Nouveau Sous-Dossier")
        name = dialog.get_input()
       
        if name and name.strip():
            try:
                self.db.create_folder(name.strip(), parent_id)
                messagebox.showinfo("Succès", "✅ Sous-dossier créé")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def rename_folder(self, folder_id: int):
        """Renommer dossier"""
        folder = self.db.get_folder(folder_id)
        if not folder:
            messagebox.showerror("Erreur", "❌ Dossier introuvable")
            return
       
        dialog = ctk.CTkInputDialog(text="Nouveau nom:", title="Renommer")
        dialog._entry.delete(0, "end")
        dialog._entry.insert(0, folder['name'])
        new_name = dialog.get_input()
       
        if new_name and new_name.strip():
            try:
                self.db.update_folder(folder_id, new_name.strip())
                messagebox.showinfo("Succès", "✅ Renommé")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def delete_folder(self, folder_id: int):
        """Supprimer dossier"""
        folder = self.db.get_folder(folder_id)
        if not folder:
            messagebox.showerror("Erreur", "❌ Introuvable")
            return
       
        response = messagebox.askyesno(
            "Confirmation",
            f"⚠️ Supprimer '{folder['name']}' ?",
            icon='warning'
        )
       
        if response:
            try:
                self.db.delete_folder(folder_id)
                messagebox.showinfo("Succès", "✅ Supprimé")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def manage_files(self, folder_id: int):
        """Gérer fichiers"""
        folder = self.db.get_folder(folder_id)
        if not folder:
            messagebox.showerror("Erreur", "❌ Introuvable")
            return
       
        file_window = ctk.CTkToplevel(self.root)
        FileManagerWindow(file_window, self.db, self.file_handler, folder, self.on_changes)
   
    def import_folder(self):
        """Importer dossier"""
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier")
        if not folder_path:
            return
        self.import_folder_confirmed(folder_path)
   
    def import_files(self):
        """Importer fichiers"""
        folders = self.db.get_all_folders(panel=self.panel)
        # Filtrer _root_*
        folders = [f for f in folders if not f['name'].startswith('_root_')]
       
        selector = ctk.CTkToplevel(self.root)
        selector.title("Importer fichiers")
        selector.geometry("500x600")
        selector.transient(self.root)
        selector.grab_set()
       
        selector.update_idletasks()
        x = (selector.winfo_screenwidth() // 2) - 250
        y = (selector.winfo_screenheight() // 2) - 300
        selector.geometry(f'500x600+{x}+{y}')
       
        header = ctk.CTkFrame(
            selector,
            height=80,
            fg_color=(self.panel_info['color'], self.panel_info['color']),
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
       
        ctk.CTkLabel(
            header,
            text=f"📄 Importer fichiers",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=25)
       
        instructions = ctk.CTkFrame(
            selector,
            fg_color=("#e7f3ff", "#1a3a52"),
            corner_radius=15
        )
        instructions.pack(fill="x", padx=20, pady=20)
       
        ctk.CTkLabel(
            instructions,
            text=f"📌 Destination dans {self.panel_info['name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1f538d", "#2563a8")
        ).pack(pady=(15, 5))
       
        ctk.CTkLabel(
            instructions,
            text="Racine ou dossier existant",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        ).pack(pady=(0, 15))
       
        selected_folder_id = [None]
       
        scroll_frame = ctk.CTkScrollableFrame(
            selector,
            fg_color=("gray90", "gray20")
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
       
        root_option = ctk.CTkFrame(
            scroll_frame,
            fg_color=("#28a745", "#1e7e34"),
            corner_radius=10,
            border_width=2,
            border_color="white"
        )
        root_option.pack(fill="x", pady=10)
       
        root_btn = ctk.CTkButton(
            root_option,
            text=f"🏠 Racine de {self.panel_info['name']}",
            height=60,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color=("gray80", "gray40"),
            text_color="white",
            command=lambda: [
                selected_folder_id.__setitem__(0, None),
                selector.destroy(),
                self.select_and_import_files(None)
            ]
        )
        root_btn.pack(fill="x", padx=10, pady=10)
       
        if folders:
            ctk.CTkLabel(
                scroll_frame,
                text="━━━ ou dossier existant ━━━",
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60")
            ).pack(pady=15)
           
            for folder in folders:
                folder_card = ctk.CTkFrame(
                    scroll_frame,
                    fg_color=("#ffffff", "#2a2a2a"),
                    corner_radius=10,
                    border_width=1,
                    border_color=("gray80", "gray40")
                )
                folder_card.pack(fill="x", pady=5)
               
                folder_btn = ctk.CTkButton(
                    folder_card,
                    text=f"📁 {folder['name']}",
                    height=50,
                    font=ctk.CTkFont(size=13),
                    fg_color="transparent",
                    hover_color=("gray90", "gray30"),
                    text_color=("black", "white"),
                    anchor="w",
                    command=lambda fid=folder['id']: [
                        selected_folder_id.__setitem__(0, fid),
                        selector.destroy(),
                        self.select_and_import_files(fid)
                    ]
                )
                folder_btn.pack(fill="x", padx=10, pady=10)
       
        ctk.CTkButton(
            selector,
            text="❌ Annuler",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=selector.destroy
        ).pack(pady=(0, 20))
   
    def select_and_import_files(self, folder_id: Optional[int]):
        """Sélectionner et importer fichiers"""
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner fichiers",
            filetypes=[
                ("Tous supportés", "*.pdf *.docx *.xlsx *.doc *.xls"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx *.doc"),
                ("Excel", "*.xlsx *.xls"),
                ("Tous", "*.*")
            ]
        )
       
        if not file_paths:
            return
       
        try:
            if folder_id is None:
                # Import à la racine
                self.import_files_to_root_direct(list(file_paths))
                return
            
            # Import dans dossier
            folder = self.db.get_folder(folder_id)
            folder_name = folder['name'] if folder else "Racine"
            
            success_count = 0
            error_count = 0
           
            for file_path in file_paths:
                filename = os.path.basename(file_path)
               
                if self.file_handler.is_allowed_file(filename):
                    success, dest_path = self.file_handler.save_file(
                        file_path,
                        filename,
                        folder_name
                    )
                   
                    if success:
                        self.db.add_file(folder_id, filename, dest_path)
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1
           
            if error_count == 0:
                messagebox.showinfo(
                    "Succès",
                    f"✅ {success_count} fichier(s) importé(s)\n\n📁 {folder_name}"
                )
            else:
                messagebox.showwarning(
                    "Attention",
                    f"✅ {success_count} importé(s)\n⚠️ {error_count} erreur(s)"
                )
           
            self.load_folders()
            self.on_changes()
           
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible:\n\n{e}")
            import traceback
            traceback.print_exc()


class FileManagerWindow:
    """Fenêtre gestion fichiers"""
   
    def __init__(self, root: ctk.CTkToplevel, db, file_handler, folder: dict, on_changes: Callable):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.folder = folder
        self.on_changes = on_changes
       
        self.root.title(f"Fichiers - {folder['name']}")
        self.root.geometry("900x650")
       
        self.center_window()
        self.create_widgets()
        self.load_files()
   
    def center_window(self):
        """Centrer"""
        self.root.update_idletasks()
        width = 900
        height = 650
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
   
    def create_widgets(self):
        """Widgets"""
        header = ctk.CTkFrame(
            self.root,
            height=80,
            corner_radius=0,
            fg_color=("#17a2b8", "#138496")
        )
        header.pack(fill="x")
        header.pack_propagate(False)
       
        ctk.CTkLabel(
            header,
            text=f"📄 Fichiers - {self.folder['name']}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#ffffff", "#ffffff")
        ).pack(side="left", padx=30, pady=20)
       
        ctk.CTkButton(
            header,
            text="✖️ Fermer",
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=self.root.destroy
        ).pack(side="right", padx=30)
       
        toolbar = ctk.CTkFrame(self.root, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=15)
       
        buttons = [
            ("➕ Ajouter", "#28a745", "#1e7e34", self.add_files),
            ("🗑️ Supprimer", "#dc3545", "#b02a37", self.delete_file),
            ("👁️ Ouvrir", "#1f538d", "#14375e", self.open_file),
            ("🔄 Rafraîchir", "#6c757d", "#5a6268", self.load_files)
        ]
       
        for text, fg_color, hover_color, command in buttons:
            ctk.CTkButton(
                toolbar,
                text=text,
                width=140,
                height=45,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=fg_color,
                hover_color=hover_color,
                command=command
            ).pack(side="left", padx=5)
       
        self.files_list = ctk.CTkScrollableFrame(
            self.root,
            fg_color=("#f0f0f0", "#2b2b2b"),
            corner_radius=15
        )
        self.files_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
       
        self.selected_file_id = None
   
    def load_files(self):
        """Charger fichiers"""
        for widget in self.files_list.winfo_children():
            widget.destroy()
       
        files = self.db.get_files_in_folder(self.folder['id'])
       
        if not files:
            ctk.CTkLabel(
                self.files_list,
                text="📭 Aucun fichier",
                font=ctk.CTkFont(size=16),
                text_color=("gray50", "gray60")
            ).pack(expand=True, pady=100)
            return
       
        for file in files:
            self.create_file_card(file)
   
    def create_file_card(self, file: dict):
        """Carte fichier"""
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        icon = self.file_handler.get_file_icon(extension)
       
        card = ctk.CTkFrame(
            self.files_list,
            height=70,
            fg_color=("#ffffff", "#1e1e1e"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)
       
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28),
            width=60
        ).pack(side="left", padx=20)
       
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=15)
       
        ctk.CTkLabel(
            info_frame,
            text=file['filename'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
       
        try:
            size = os.path.getsize(file['filepath']) if os.path.exists(file['filepath']) else 0
            size_formatted = self.format_file_size(size)
        except:
            size_formatted = "N/A"
       
        is_pdf = self.file_handler.is_pdf(file['filename'])
        type_text = f"{size_formatted} • {'🔒 PDF' if is_pdf else '💾 Téléchargeable'}"
       
        ctk.CTkLabel(
            info_frame,
            text=type_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w"
        ).pack(anchor="w")
       
        select_btn = ctk.CTkButton(
            card,
            text="✓ Sélectionner",
            width=130,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=lambda: self.select_file(file['id'], card)
        )
        select_btn.pack(side="right", padx=15)
       
        card.bind('<Double-Button-1>', lambda e: self.open_file())
   
    def select_file(self, file_id: int, card: ctk.CTkFrame):
        """Sélectionner"""
        self.selected_file_id = file_id
       
        for widget in self.files_list.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(border_color=("gray80", "gray30"), border_width=1)
       
        card.configure(border_color=("#1f538d", "#2563a8"), border_width=3)
   
    def add_files(self):
        """Ajouter"""
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner fichiers",
            filetypes=[
                ("Tous supportés", "*.pdf *.docx *.xlsx *.doc *.xls"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx *.doc"),
                ("Excel", "*.xlsx *.xls"),
                ("Tous", "*.*")
            ]
        )
       
        if not file_paths:
            return
       
        try:
            success_count = 0
            error_count = 0
           
            for file_path in file_paths:
                filename = os.path.basename(file_path)
               
                if self.file_handler.is_allowed_file(filename):
                    success, dest_path = self.file_handler.save_file(
                        file_path,
                        filename,
                        self.folder['name']
                    )
                   
                    if success:
                        self.db.add_file(self.folder['id'], filename, dest_path)
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1
           
            if error_count == 0:
                messagebox.showinfo("Succès", f"✅ {success_count} ajouté(s)")
            else:
                messagebox.showwarning("Attention", f"✅ {success_count}\n⚠️ {error_count} erreur(s)")
           
            self.load_files()
            self.on_changes()
           
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def delete_file(self):
        """Supprimer"""
        if not self.selected_file_id:
            messagebox.showwarning("Attention", "⚠️ Sélectionnez un fichier")
            return
       
        file = self.db.get_file(self.selected_file_id)
        if not file:
            messagebox.showerror("Erreur", "❌ Introuvable")
            return
       
        response = messagebox.askyesno("Confirmation", f"⚠️ Supprimer:\n\n{file['filename']} ?", icon='warning')
       
        if response:
            try:
                self.db.delete_file(self.selected_file_id)
                messagebox.showinfo("Succès", "✅ Supprimé")
                self.selected_file_id = None
                self.load_files()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Impossible:\n{e}")
   
    def open_file(self):
        """Ouvrir"""
        if not self.selected_file_id:
            messagebox.showwarning("Attention", "⚠️ Sélectionnez un fichier")
            return
       
        file = self.db.get_file(self.selected_file_id)
        if not file:
            messagebox.showerror("Erreur", "❌ Introuvable")
            return
       
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "❌ Fichier n'existe pas")
            return
       
        success = self.file_handler.open_file(file['filepath'])
        if not success:
            messagebox.showerror("Erreur", "❌ Impossible d'ouvrir")
   
    @staticmethod
    def format_file_size(size: int) -> str:
        """Formater taille"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
