#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application Portail Document - SNTP
Application desktop moderne de gestion de documents avec système de panels

Auteur: Portail Document Team
Version: 5.0.0 - Système multi-panels avec interface d'accueil
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT: Importer CustomTkinter et TkinterDnD
try:
    import customtkinter as ctk
    from tkinterdnd2 import TkinterDnD
    DRAG_DROP_AVAILABLE = True
    print("✅ Module customtkinter chargé")
    print("✅ Module tkinterdnd2 chargé - Drag & Drop activé")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("   Installez: pip install customtkinter tkinterdnd2")
    sys.exit(1)

from tkinter import messagebox
from database import Database
from utils.file_handler import FileHandler
try:
    from utils.notifications import NotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("⚠️ Module notifications non disponible")

from ui.home_window import HomeWindow
from ui.panel_view import PanelView
from ui.entete_choice_window import EnteteChoiceWindow
from ui.login_window import LoginWindow
from ui.panel_selector_window import PanelSelectorWindow
from ui.admin_window import AdminWindow
from ui.search_window import SearchWindow  # ✅ AJOUT DE L'IMPORT

# Configuration du thème CustomTkinter
ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class CTkinterDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """Classe combinant CustomTkinter et TkinterDnD"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class PortalApplication:
    """Application principale du Portail Document avec système de panels"""
    
    def __init__(self):
        # Créer la fenêtre principale avec support Drag & Drop
        if DRAG_DROP_AVAILABLE:
            self.root = CTkinterDnD()
            print("✅ Fenêtre CTkinterDnD créée")
        else:
            self.root = ctk.CTk()
            print("⚠️ Fenêtre CTk standard créée (pas de Drag & Drop)")
        
        self.db = None
        self.file_handler = None
        self.notification_manager = None
        
        # État de l'application
        self.current_view = None  # 'home', 'panel', 'admin'
        self.current_panel = None
        self.current_folder_id = None
        self.folder_history = []
        self.is_admin_authenticated = False
        
        # Initialiser la base de données
        self.init_database()
        
        # Initialiser le gestionnaire de fichiers
        self.init_file_handler()
        
        # Initialiser le gestionnaire de notifications
        if NOTIFICATIONS_AVAILABLE:
            self.notification_manager = NotificationManager(self.root)
        
        # Configuration de la fenêtre
        self.setup_main_window()
        
        # Afficher l'interface d'accueil
        self.show_home()
    
    def init_database(self):
        """Initialiser la connexion à la base de données"""
        try:
            self.db = Database("portal.db")
            print("✅ Base de données initialisée avec support des panels")
        except Exception as e:
            messagebox.showerror(
                "Erreur Critique",
                f"Impossible d'initialiser la base de données:\n\n{e}"
            )
            sys.exit(1)
    
    def init_file_handler(self):
        """Initialiser le gestionnaire de fichiers"""
        try:
            self.file_handler = FileHandler("uploads")
            print("✅ Gestionnaire de fichiers initialisé")
        except Exception as e:
            messagebox.showerror(
                "Erreur Critique",
                f"Impossible d'initialiser le gestionnaire de fichiers:\n\n{e}"
            )
            sys.exit(1)
    
    def setup_main_window(self):
        """Configurer la fenêtre principale"""
        self.root.title("Portail Document - SNTP")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Configuration de l'arrière-plan (si disponible)
        self.bg_label = None
        self.setup_background()
        
        # ============= NAVBAR SUPÉRIEURE FIXE =============
        self.navbar = ctk.CTkFrame(
            self.root,
            height=80,
            corner_radius=0,
            fg_color=("#1a1a1a", "#0d0d0d"),
            border_width=0
        )
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        
        # Frame gauche pour logo et titre
        left_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        left_frame.pack(side="left", padx=30, pady=15)
        
        # Logo SNTP si disponible
        self.create_navbar_logo(left_frame)
        
        # Titre et sous-titre
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Portail Document",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#ffffff", "#ffffff")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Société Nationale des Travaux Publics",
            font=ctk.CTkFont(size=12),
            text_color=("#a0a0a0", "#808080")
        )
        subtitle_label.pack(anchor="w")
        
        # Frame droite pour boutons de navigation
        right_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        right_frame.pack(side="right", padx=30, pady=15)
        
        # ✅ BOUTON RECHERCHE (AJOUTÉ)
        self.search_button = ctk.CTkButton(
            right_frame,
            text="🔍 Rechercher",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#32b349", "#229143"),
            command=self.open_search
        )
        self.search_button.pack(side="left", padx=5)
        
        # Bouton Retour (initialement caché)
        self.back_button = ctk.CTkButton(
            right_frame,
            text="⬅️ Retour",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4a4a4a", "#2a2a2a"),
            hover_color=("#5a5a5a", "#3a3a3a"),
            command=self.go_back
        )
        self.back_button.pack(side="left", padx=5)
        self.back_button.pack_forget()  # Masquer initialement
        
        # Bouton Accueil
        self.home_button = ctk.CTkButton(
            right_frame,
            text="🏠 Accueil",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=self.show_home
        )
        self.home_button.pack(side="left", padx=5)
        
        # Bouton Admin
        self.admin_button = ctk.CTkButton(
            right_frame,
            text="⚙️ Admin",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=self.toggle_admin
        )
        self.admin_button.pack(side="left", padx=5)
        
        # ============= ZONE DE CONTENU =============
        self.content_frame = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True)
    
    def setup_background(self):
        """Configuration de l'arrière-plan avec background.png"""
        try:
            if os.path.exists("background.png"):
                from PIL import Image
                
                # Charger l'image de fond
                bg_image = Image.open("background.png")
                bg_image = bg_image.resize((1400, 900), Image.Resampling.LANCZOS)
                
                # Appliquer un overlay léger
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, 40))
                bg_image = bg_image.convert("RGBA")
                bg_image = Image.alpha_composite(bg_image, overlay)
                
                # Utiliser CTkImage
                self.bg_photo = ctk.CTkImage(
                    light_image=bg_image,
                    dark_image=bg_image,
                    size=(1400, 900)
                )
                
                # Label pour l'arrière-plan
                self.bg_label = ctk.CTkLabel(
                    self.root,
                    image=self.bg_photo,
                    text=""
                )
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()
                
                print("✅ Background.png chargé")
                
        except Exception as e:
            print(f"⚠️ Erreur chargement background.png: {e}")
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = 1400
        height = 900
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_navbar_logo(self, parent):
        """Créer le logo dans la navbar"""
        try:
            if os.path.exists("sntp.png"):
                from PIL import Image
                
                logo_image = Image.open("sntp.png")
                logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                
                # Utiliser CTkImage
                self.navbar_logo = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(50, 50)
                )
                
                logo_label = ctk.CTkLabel(
                    parent,
                    image=self.navbar_logo,
                    text=""
                )
                logo_label.pack(side="left", padx=(0, 15))
                return
                
        except Exception as e:
            print(f"⚠️ Erreur logo navbar: {e}")
        
        # Logo emoji de fallback
        logo_label = ctk.CTkLabel(
            parent,
            text="📁",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        logo_label.pack(side="left", padx=(0, 15))
    
    # ==================== NAVIGATION ====================
    
    def clear_content(self):
        """Nettoyer la zone de contenu"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home(self):
        """Afficher l'interface d'accueil"""
        print("🏠 Affichage de l'interface d'accueil")
        
        self.current_view = 'home'
        self.current_panel = None
        self.current_folder_id = None
        self.folder_history = []
        
        # Masquer le bouton retour
        self.back_button.pack_forget()
        
        # Nettoyer et créer l'accueil
        self.clear_content()
        
        home_view = HomeWindow(
            self.content_frame,
            self.db,
            self.file_handler,
            on_panel_select=self.show_panel,
            on_entete_click=self.show_entete_choice
        )
        home_view.pack(fill="both", expand=True)
    
    def show_panel(self, panel: str):
        """Afficher un panel spécifique"""
        print(f"📂 Affichage du panel: {panel}")
        
        self.current_view = 'panel'
        self.current_panel = panel
        self.current_folder_id = None
        self.folder_history = []
        
        # Masquer le bouton retour
        self.back_button.pack_forget()
        
        # Nettoyer et créer la vue du panel
        self.clear_content()
        
        panel_view = PanelView(
            self.content_frame,
            self.db,
            self.file_handler,
            panel,
            folder_id=None,
            on_folder_open=self.open_folder_in_panel,
            notification_manager=self.notification_manager
        )
        panel_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Afficher le bouton retour
        self.back_button.pack(side="left", padx=5)
    
    def open_folder_in_panel(self, folder_id: int):
        """Ouvrir un dossier dans le panel courant"""
        if self.current_folder_id is not None:
            self.folder_history.append(self.current_folder_id)
        
        self.current_folder_id = folder_id
        
        print(f"📁 Ouverture du dossier ID={folder_id} dans le panel {self.current_panel}")
        
        # Nettoyer et recréer la vue
        self.clear_content()
        
        panel_view = PanelView(
            self.content_frame,
            self.db,
            self.file_handler,
            self.current_panel,
            folder_id=folder_id,
            on_folder_open=self.open_folder_in_panel,
            notification_manager=self.notification_manager
        )
        panel_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Afficher le bouton retour
        self.back_button.pack(side="left", padx=5)
    
    def go_back(self):
        """Retourner à l'élément précédent"""
        if self.folder_history:
            # Retour au dossier parent
            previous_folder_id = self.folder_history.pop()
            self.current_folder_id = previous_folder_id
            
            print(f"⬅️ Retour au dossier ID={previous_folder_id}")
            
            self.clear_content()
            
            panel_view = PanelView(
                self.content_frame,
                self.db,
                self.file_handler,
                self.current_panel,
                folder_id=previous_folder_id,
                on_folder_open=self.open_folder_in_panel,
                notification_manager=self.notification_manager
            )
            panel_view.pack(fill="both", expand=True, padx=20, pady=20)
        else:
            # Retour à la racine du panel
            if self.current_folder_id is not None:
                self.current_folder_id = None
                self.show_panel(self.current_panel)
            else:
                # Retour à l'accueil
                self.show_home()
    
    def show_entete_choice(self):
        """Afficher le choix pour En-tête"""
        print("📋 Affichage du choix En-tête")
        
        EnteteChoiceWindow(
            self.root,
            self.open_pdf_viewer,
            self.notification_manager
        )
    
    def open_pdf_viewer(self, pdf_path: str, filename: str):
        """Ouvrir le viewer PDF"""
        try:
            from ui.pdf_viewer import PDFViewer
            pdf_window = ctk.CTkToplevel(self.root)
            PDFViewer(pdf_window, pdf_path, filename)
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'ouvrir le PDF:\n{e}"
            )
    
    # ==================== RECHERCHE (✅ MÉTHODE AJOUTÉE) ====================
    
    def open_search(self):
        """Ouvrir la fenêtre de recherche"""
        print("🔍 Ouverture de la fenêtre de recherche")
        
        try:
            # Créer une fenêtre TopLevel pour la recherche
            search_window = ctk.CTkToplevel(self.root)
            
            # Initialiser la fenêtre de recherche avec callback de navigation
            SearchWindow(
                search_window,
                self.db,
                self.file_handler,
                on_file_select=self.navigate_to_folder_from_search
            )
            
            print("✅ Fenêtre de recherche ouverte")
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'ouvrir la recherche:\n\n{e}"
            )
            print(f"❌ Erreur ouverture recherche: {e}")
            import traceback
            traceback.print_exc()
    
    def navigate_to_folder_from_search(self, folder_id: int):
        """Naviguer vers un dossier depuis la recherche"""
        print(f"🔍➡️ Navigation vers le dossier ID={folder_id} depuis la recherche")
        
        try:
            # Récupérer les infos du dossier
            folder = self.db.get_folder(folder_id)
            
            if not folder:
                messagebox.showerror(
                    "Erreur",
                    "❌ Dossier introuvable"
                )
                return
            
            # Déterminer le panel du dossier
            panel = folder.get('panel', 'interface_emp')
            
            # Afficher le panel et naviguer vers le dossier
            self.current_panel = panel
            self.current_view = 'panel'
            self.folder_history = []
            
            # Ouvrir directement le dossier
            self.open_folder_in_panel(folder_id)
            
            # Notification
            if self.notification_manager:
                self.notification_manager.show_app_notification(
                    "📂 Navigation",
                    f"Ouverture du dossier '{folder['name']}'"
                )
            
            print(f"✅ Navigation réussie vers le dossier '{folder['name']}'")
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible de naviguer:\n\n{e}"
            )
            print(f"❌ Erreur navigation: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== ADMINISTRATION ====================
    
    def toggle_admin(self):
        """Basculer entre connexion et déconnexion admin"""
        if self.is_admin_authenticated:
            self.show_admin_menu()
        else:
            self.open_admin_login()
    
    def open_admin_login(self):
        """Ouvrir la fenêtre de connexion admin"""
        try:
            LoginWindow(self.root, self.db, self.on_admin_success)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible d'ouvrir la connexion admin:\n{e}")
    
    def on_admin_success(self):
        """Callback de succès de connexion admin"""
        self.is_admin_authenticated = True
        self.admin_button.configure(
            text="⚙️ Admin ✓",
            fg_color=("#28a745", "#1e7e34")
        )
        
        if self.notification_manager:
            self.notification_manager.show_app_notification(
                "✅ Connexion",
                "Connexion administrateur réussie"
            )
        
        # Afficher le sélecteur de panel
        self.show_panel_selector()
    
    def show_admin_menu(self):
        """Afficher le menu admin"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("Menu Admin")
        menu_window.geometry("300x200")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        menu_window.update_idletasks()
        x = (menu_window.winfo_screenwidth() // 2) - 150
        y = (menu_window.winfo_screenheight() // 2) - 100
        menu_window.geometry(f'300x200+{x}+{y}')
        
        ctk.CTkLabel(
            menu_window,
            text="⚙️ Menu Administrateur",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkButton(
            menu_window,
            text="📊 Ouvrir Panel Admin",
            width=220,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            command=lambda: [menu_window.destroy(), self.show_panel_selector()]
        ).pack(pady=10)
        
        ctk.CTkButton(
            menu_window,
            text="🚪 Se Déconnecter",
            width=220,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=lambda: [menu_window.destroy(), self.logout_admin()]
        ).pack(pady=10)
    
    def logout_admin(self):
        """Déconnecter l'administrateur"""
        response = messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vous déconnecter du mode administrateur ?",
            icon='question'
        )
        
        if response:
            self.is_admin_authenticated = False
            self.admin_button.configure(
                text="⚙️ Admin",
                fg_color=("#dc3545", "#b02a37")
            )
            
            if self.notification_manager:
                self.notification_manager.show_app_notification(
                    "🚪 Déconnexion",
                    "Déconnexion administrateur"
                )
    
    def show_panel_selector(self):
        """Afficher le sélecteur de panel pour l'administration"""
        PanelSelectorWindow(
            self.root,
            on_panel_selected=self.open_panel_admin
        )
    
    def open_panel_admin(self, panel: str):
        """Ouvrir l'administration d'un panel spécifique"""
        try:
            admin_window = ctk.CTkToplevel(self.root)
            AdminWindow(
                admin_window,
                self.db,
                self.file_handler,
                panel,
                on_changes=self.refresh_content
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible d'ouvrir le panel admin:\n{e}")
            import traceback
            traceback.print_exc()
    
    def refresh_content(self):
        """Rafraîchir le contenu affiché"""
        print("🔄 Rafraîchissement du contenu")
        
        if self.notification_manager:
            self.notification_manager.show_app_notification(
                "🔄 Mise à jour",
                "Contenu rafraîchi"
            )
        
        # Rafraîchir selon la vue actuelle
        if self.current_view == 'panel' and self.current_panel:
            if self.current_folder_id is not None:
                self.open_folder_in_panel(self.current_folder_id)
            else:
                self.show_panel(self.current_panel)
        elif self.current_view == 'home':
            self.show_home()
    
    # ==================== EXÉCUTION ====================
    
    def run(self):
        """Démarrer l'application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️ Interruption par l'utilisateur")
            self.cleanup()
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
            messagebox.showerror("Erreur Fatale", str(e))
            self.cleanup()
    
    def cleanup(self):
        """Nettoyer les ressources avant de quitter"""
        if self.db:
            self.db.close()
        print("👋 Application fermée")


def main():
    """Point d'entrée principal de l'application"""
    print("=" * 80)
    print("  PORTAIL DOCUMENT - SNTP")
    print("  Application Desktop Moderne de Gestion de Documents")
    print("  Version 5.0 - Système Multi-Panels")
    print("  ")
    print("  📜 Certification")
    print("  📋 En-tête (Visualiser PDF / Télécharger DOCX)")
    print("  👥 Interface Employés")
    print("  📦 Autre")
    print("  ")
    print("  🔒 PDF : Lecture seule (non téléchargeable)")
    print("  💾 DOCX/XLSX : Visualisables et téléchargeables")
    print("=" * 80)
    print()
    
    try:
        app = PortalApplication()
        app.run()
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
