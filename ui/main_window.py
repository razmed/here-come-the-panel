import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from .folder_view import FolderView
from .search_window import SearchWindow
from .login_window import LoginWindow
try:
    from utils.notifications import NotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
import os

class MainWindow:
    """Fenêtre principale avec background visible - Solution Simple"""
    
    def __init__(self, root: ctk.CTk, db, file_handler):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.current_folder_id = None
        self.folder_history = []
        self.is_admin_authenticated = False
        self.notification_count = 0
        
        if NOTIFICATIONS_AVAILABLE:
            self.notification_manager = NotificationManager(root)
        else:
            self.notification_manager = None
        
        self.root.title("Portail Document - SNTP")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        self.center_window()
        
        # ✅ SOLUTION: Charger background directement avec CTkImage
        self.setup_background()
        
        self.create_widgets()
        self.load_folder(None)
    
    def setup_background(self):
        """Charger le background avec CTkLabel"""
        try:
            if os.path.exists("background.png"):
                from PIL import Image
                
                # Charger l'image
                bg_image = Image.open("background.png")
                bg_image = bg_image.resize((1400, 900), Image.Resampling.LANCZOS)
                
                # Créer CTkImage
                self.bg_photo = ctk.CTkImage(
                    light_image=bg_image,
                    dark_image=bg_image,
                    size=(1400, 900)
                )
                
                # ✅ Créer un label pour le background
                self.bg_label = ctk.CTkLabel(
                    self.root,
                    image=self.bg_photo,
                    text=""
                )
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                print("✅ Background chargé")
                
            else:
                print("⚠️ background.png introuvable")
                self.root.configure(fg_color="#1a1a2e")
                
        except Exception as e:
            print(f"❌ Erreur background: {e}")
            import traceback
            traceback.print_exc()
            self.root.configure(fg_color="#1a1a2e")
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = 1400
        height = 900
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer les widgets"""
        # ============= NAVBAR =============
        navbar = ctk.CTkFrame(
            self.root,
            height=80,
            corner_radius=0,
            fg_color=("#1a1a1a", "#0d0d0d"),
            border_width=0
        )
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)
        
        # Logo et titre
        left_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        left_frame.pack(side="left", padx=30, pady=15)
        
        self.create_navbar_logo(left_frame)
        
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Portail Document",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Société Nationale des Travaux Publics",
            font=ctk.CTkFont(size=12),
            text_color="#a0a0a0"
        ).pack(anchor="w")
        
        # Boutons
        right_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        right_frame.pack(side="right", padx=30, pady=15)
        
        # Notifications
        notification_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        notification_frame.pack(side="left", padx=5)
        
        self.notification_button = ctk.CTkButton(
            notification_frame,
            text="🔔",
            width=50,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="#6c757d",
            hover_color="#7c858d",
            command=self.show_notifications
        )
        self.notification_button.pack()
        
        self.notification_badge_frame = ctk.CTkFrame(
            notification_frame,
            width=22,
            height=22,
            corner_radius=11,
            fg_color="#dc3545"
        )
        self.notification_badge_frame.place(x=35, y=-5)
        
        self.notification_badge = ctk.CTkLabel(
            self.notification_badge_frame,
            text="0",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            width=22,
            height=22
        )
        self.notification_badge.pack()
        self.notification_badge_frame.place_forget()
        
        # Boutons d'action
        ctk.CTkButton(
            right_frame,
            text="🔍 Rechercher",
            width=130,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#32b349",
            command=self.open_search
        ).pack(side="left", padx=5)
        
        self.back_button = ctk.CTkButton(
            right_frame,
            text="⬅️ Retour",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4a4a4a",
            hover_color="#5a5a5a",
            command=self.go_back,
            state="disabled"
        )
        self.back_button.pack(side="left", padx=5)
        
        ctk.CTkButton(
            right_frame,
            text="🏠 Accueil",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f538d",
            hover_color="#2563a8",
            command=lambda: self.load_folder(None, clear_history=True)
        ).pack(side="left", padx=5)
        
        self.admin_button = ctk.CTkButton(
            right_frame,
            text="⚙️ Admin",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#dc3545",
            hover_color="#e04555",
            command=self.toggle_admin
        )
        self.admin_button.pack(side="left", padx=5)
        
        # ============= ZONE CONTENU (TRANSPARENT) =============
        self.content_frame = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent",
            border_width=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ✅ Après création des widgets, remettre le background en arrière
        if hasattr(self, 'bg_label'):
            self.bg_label.lower()
        
        self.root.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event):
        """Redimensionner le background"""
        if event.widget == self.root and hasattr(self, 'bg_label') and os.path.exists("background.png"):
            try:
                from PIL import Image
                
                width = event.width
                height = event.height
                
                bg_image = Image.open("background.png")
                bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
                
                self.bg_photo = ctk.CTkImage(
                    light_image=bg_image,
                    dark_image=bg_image,
                    size=(width, height)
                )
                
                self.bg_label.configure(image=self.bg_photo)
                self.bg_label.lower()
                
            except Exception as e:
                print(f"⚠️ Erreur redimensionnement: {e}")
    
    def create_navbar_logo(self, parent):
        """Logo navbar"""
        try:
            if os.path.exists("sntp.png"):
                from PIL import Image
                
                logo_image = Image.open("sntp.png")
                logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                
                self.navbar_logo = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(50, 50)
                )
                
                ctk.CTkLabel(
                    parent,
                    image=self.navbar_logo,
                    text=""
                ).pack(side="left", padx=(0, 15))
                return
        except:
            pass
        
        ctk.CTkLabel(
            parent,
            text="📁",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(side="left", padx=(0, 15))
    
    def show_notifications(self):
        """Notifications"""
        notif = ctk.CTkToplevel(self.root)
        notif.title("🔔 Notifications")
        notif.geometry("400x500")
        notif.transient(self.root)
        
        notif.update_idletasks()
        x = (notif.winfo_screenwidth() // 2) - 200
        y = (notif.winfo_screenheight() // 2) - 250
        notif.geometry(f'400x500+{x}+{y}')
        
        header = ctk.CTkFrame(notif, height=60, fg_color="#1f538d", corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(notif, fg_color="gray90")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        if self.notification_count == 0:
            ctk.CTkLabel(
                scroll,
                text="📭 Aucune notification",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            ).pack(expand=True, pady=100)
        
        ctk.CTkButton(
            notif,
            text="✖️ Fermer",
            height=40,
            fg_color="#dc3545",
            command=notif.destroy
        ).pack(pady=10)
        
        self.notification_count = 0
        self.update_notification_badge()
    
    def update_notification_badge(self):
        """Badge"""
        if self.notification_count > 0:
            self.notification_badge.configure(text=str(self.notification_count))
            self.notification_badge_frame.place(x=35, y=-5)
        else:
            self.notification_badge_frame.place_forget()
    
    def add_notification(self, message: str):
        """Ajouter notification"""
        self.notification_count += 1
        self.update_notification_badge()
        
        if self.notification_manager:
            self.notification_manager.show_app_notification("Notification", message)
    
    def open_search(self):
        """Recherche"""
        try:
            search = ctk.CTkToplevel(self.root)
            SearchWindow(search, self.db, self.file_handler, self.navigate_to_folder)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Recherche:\n{e}")
    
    def navigate_to_folder(self, folder_id: int):
        """Naviguer"""
        self.load_folder(folder_id)
    
    def toggle_admin(self):
        """Admin"""
        if self.is_admin_authenticated:
            self.show_admin_menu()
        else:
            self.open_admin_login()
    
    def open_admin_login(self):
        """Login admin"""
        try:
            LoginWindow(self.root, self.db, self.on_admin_success)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Login:\n{e}")
    
    def on_admin_success(self):
        """Succès admin"""
        self.is_admin_authenticated = True
        self.admin_button.configure(text="⚙️ Admin ✓", fg_color="#28a745")
        self.add_notification("Admin connecté")
        self.open_admin()
    
    def show_admin_menu(self):
        """Menu admin"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("Menu Admin")
        menu.geometry("300x250")
        menu.transient(self.root)
        menu.grab_set()
        
        menu.update_idletasks()
        x = (menu.winfo_screenwidth() // 2) - 150
        y = (menu.winfo_screenheight() // 2) - 125
        menu.geometry(f'300x250+{x}+{y}')
        
        ctk.CTkLabel(
            menu,
            text="⚙️ Menu Admin",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkButton(
            menu,
            text="📊 Panel",
            width=220,
            height=45,
            fg_color="#1f538d",
            command=lambda: [menu.destroy(), self.open_admin()]
        ).pack(pady=10)
        
        ctk.CTkButton(
            menu,
            text="🚪 Déconnexion",
            width=220,
            height=45,
            fg_color="#dc3545",
            command=lambda: [menu.destroy(), self.logout_admin()]
        ).pack(pady=10)
    
    def logout_admin(self):
        """Déconnexion"""
        if messagebox.askyesno("Déconnexion", "Déconnexion admin ?"):
            self.is_admin_authenticated = False
            self.admin_button.configure(text="⚙️ Admin", fg_color="#dc3545")
            self.add_notification("Déconnecté")
    
    def open_admin(self):
        """Panel admin"""
        try:
            from .admin_window import AdminWindow
            admin = ctk.CTkToplevel(self.root)
            AdminWindow(admin, self.db, self.file_handler, self.refresh_content)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Admin:\n{e}")
    
    def load_folder(self, folder_id: Optional[int], clear_history: bool = False):
        """Charger dossier"""
        if clear_history:
            self.folder_history = []
        elif self.current_folder_id is not None:
            self.folder_history.append(self.current_folder_id)
        
        self.current_folder_id = folder_id
        
        self.back_button.configure(state="normal" if self.folder_history else "disabled")
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        try:
            folder_view = FolderView(
                self.content_frame,
                self.db,
                self.file_handler,
                folder_id,
                on_folder_open=self.handle_folder_open,
                notification_manager=self.notification_manager
            )
            folder_view.pack(fill="both", expand=True)
            
            # ✅ Remettre le background en arrière
            if hasattr(self, 'bg_label'):
                self.bg_label.lower()
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_folder_open(self, folder_id: int):
        """Callback"""
        self.load_folder(folder_id)
    
    def go_back(self):
        """Retour"""
        if self.folder_history:
            previous = self.folder_history.pop()
            self.current_folder_id = previous
            
            self.back_button.configure(state="normal" if self.folder_history else "disabled")
            
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            try:
                folder_view = FolderView(
                    self.content_frame,
                    self.db,
                    self.file_handler,
                    previous,
                    on_folder_open=self.handle_folder_open,
                    notification_manager=self.notification_manager
                )
                folder_view.pack(fill="both", expand=True)
                
                if hasattr(self, 'bg_label'):
                    self.bg_label.lower()
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def refresh_content(self):
        """Rafraîchir"""
        self.add_notification("Rafraîchi")
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        try:
            folder_view = FolderView(
                self.content_frame,
                self.db,
                self.file_handler,
                self.current_folder_id,
                on_folder_open=self.handle_folder_open,
                notification_manager=self.notification_manager
            )
            folder_view.pack(fill="both", expand=True)
            
            if hasattr(self, 'bg_label'):
                self.bg_label.lower()
                
        except Exception as e:
            print(f"❌ Erreur: {e}")