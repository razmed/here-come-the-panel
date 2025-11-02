import customtkinter as ctk
from tkinter import messagebox
import threading
import time
from typing import Optional
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class NotificationManager:
    """Gestionnaire de notifications système"""
    
    def __init__(self, parent_window: Optional[ctk.CTk] = None):
        self.parent = parent_window
        self.notification_queue = []
        self.is_showing = False
    
    def show_system_notification(self, title: str, message: str, timeout: int = 5):
        """Afficher une notification système native"""
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Portail Document SNTP",
                    timeout=timeout
                )
            except Exception as e:
                print(f"⚠️ Erreur notification système: {e}")
                self.show_app_notification(title, message)
        else:
            self.show_app_notification(title, message)
    
    def show_app_notification(self, title: str, message: str, duration: int = 3000):
        """Afficher une notification dans l'application"""
        if not self.parent:
            messagebox.showinfo(title, message)
            return
        
        # Créer une notification toast personnalisée
        notification_window = ctk.CTkToplevel(self.parent)
        notification_window.title("")
        notification_window.geometry("350x120")
        notification_window.resizable(False, False)
        notification_window.attributes("-topmost", True)
        notification_window.overrideredirect(True)
        
        # Position en haut à droite
        screen_width = notification_window.winfo_screenwidth()
        notification_window.geometry(f"350x120+{screen_width-370}+20")
        
        # Style moderne
        main_frame = ctk.CTkFrame(
            notification_window,
            fg_color=("#1a1a1a", "#0d0d0d"),
            corner_radius=15,
            border_width=2,
            border_color=("#0066cc", "#0088ee")
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#ffffff", "#ffffff")
        )
        title_label.pack(pady=(15, 5))
        
        # Message
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=("#a0a0a0", "#808080"),
            wraplength=300
        )
        message_label.pack(pady=(0, 15))
        
        # Auto-fermeture
        def close_notification():
            time.sleep(duration / 1000)
            try:
                notification_window.destroy()
            except:
                pass
        
        threading.Thread(target=close_notification, daemon=True).start()
        
        # Fermeture au clic
        notification_window.bind("<Button-1>", lambda e: notification_window.destroy())
        main_frame.bind("<Button-1>", lambda e: notification_window.destroy())
    
    def notify_file_added(self, filename: str):
        """Notification d'ajout de fichier"""
        self.show_system_notification(
            "📄 Fichier ajouté",
            f"Le fichier '{filename}' a été ajouté avec succès"
        )
    
    def notify_file_deleted(self, filename: str):
        """Notification de suppression de fichier"""
        self.show_system_notification(
            "🗑️ Fichier supprimé",
            f"Le fichier '{filename}' a été supprimé"
        )
    
    def notify_folder_created(self, foldername: str):
        """Notification de création de dossier"""
        self.show_system_notification(
            "📁 Dossier créé",
            f"Le dossier '{foldername}' a été créé"
        )
    
    def notify_folder_deleted(self, foldername: str):
        """Notification de suppression de dossier"""
        self.show_system_notification(
            "🗑️ Dossier supprimé",
            f"Le dossier '{foldername}' a été supprimé"
        )
    
    def notify_import_complete(self, count: int):
        """Notification d'import terminé"""
        self.show_system_notification(
            "✅ Import terminé",
            f"{count} fichier(s) importé(s) avec succès"
        )
