import customtkinter as ctk
from tkinter import messagebox
from typing import Callable
import os

class LoginWindow:
    """Fenêtre de connexion administrateur simplifiée avec logo SNTP"""
    
    def __init__(self, root: ctk.CTk, db, on_success: Callable):
        self.root = root
        self.db = db
        self.on_success = on_success
        
        # Créer la fenêtre de connexion
        self.create_login_window()
    
    def create_login_window(self):
        """Créer la fenêtre de connexion"""
        # Fenêtre modale
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Authentification Administrateur - SNTP")
        self.login_window.geometry("500x600")
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        self.login_window.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Configuration de l'arrière-plan avec image background.png si disponible
        self.setup_background()
        
        # Contenu principal
        self.create_content()
        
        # Focus sur le champ mot de passe
        self.password_entry.focus()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.login_window.update_idletasks()
        width = 500
        height = 600
        x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
        self.login_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_background(self):
        """Configuration de l'arrière-plan"""
        try:
            # Vérifier si background.png existe
            if os.path.exists("background.png"):
                from PIL import Image, ImageTk
                
                # Charger et redimensionner l'image
                bg_image = Image.open("background.png")
                bg_image = bg_image.resize((500, 600), Image.Resampling.LANCZOS)
                
                # Appliquer un filtre de transparence
                bg_image = bg_image.convert("RGBA")
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, 100))  # Overlay sombre
                bg_image = Image.alpha_composite(bg_image, overlay)
                
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                
                # Label pour l'arrière-plan
                bg_label = ctk.CTkLabel(
                    self.login_window,
                    image=self.bg_photo,
                    text=""
                )
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
            else:
                # Arrière-plan dégradé par défaut
                self.login_window.configure(fg_color=("#1a1a2e", "#0f0f23"))
                
        except ImportError:
            print("⚠️ Pillow non installé - arrière-plan par défaut")
            self.login_window.configure(fg_color=("#1a1a2e", "#0f0f23"))
        except Exception as e:
            print(f"⚠️ Erreur chargement background.png: {e}")
            self.login_window.configure(fg_color=("#1a1a2e", "#0f0f23"))
    
    def create_content(self):
        """Créer le contenu de la fenêtre"""
        # Frame principal
        main_frame = ctk.CTkFrame(
            self.login_window,
            width=400,
            height=500,
            fg_color=("gray95", "gray15"),
            corner_radius=20,
            border_width=2,
            border_color=("#1f538d", "#2563a8")
        )
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        main_frame.pack_propagate(False)
        
        # Logo SNTP
        self.create_logo(main_frame)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔒 Authentification",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#1f538d", "#2563a8")
        )
        title_label.pack(pady=(30, 10))
        
        # Sous-titre
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Administration du Portail Document",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Frame pour le formulaire
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(padx=50, pady=20, fill="x")
        
        # Label mot de passe
        password_label = ctk.CTkLabel(
            form_frame,
            text="🔑 Mot de passe administrateur:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 10))
        
        # Champ mot de passe
        self.password_entry = ctk.CTkEntry(
            form_frame,
            height=50,
            font=ctk.CTkFont(size=16),
            placeholder_text="Entrez votre mot de passe...",
            show="●",
            border_width=2,
            border_color=("#1f538d", "#2563a8")
        )
        self.password_entry.pack(fill="x", pady=(0, 30))
        
        # Bouton de connexion
        login_button = ctk.CTkButton(
            form_frame,
            text="🚀 Se Connecter",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#2563a8", "#1a4a7a"),
            corner_radius=25,
            command=self.authenticate
        )
        login_button.pack(fill="x", pady=(0, 20))
        
        # Bouton annuler
        cancel_button = ctk.CTkButton(
            form_frame,
            text="❌ Annuler",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            corner_radius=20,
            command=self.login_window.destroy
        )
        cancel_button.pack(fill="x")
        
        # Informations sécurité
        security_label = ctk.CTkLabel(
            main_frame,
            text="🔐 Authentification sécurisée avec bcrypt\n🔒 Données chiffrées",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        security_label.pack(pady=20)
        
        # Liaison des événements
        self.password_entry.bind('<Return>', lambda e: self.authenticate())
        self.login_window.bind('<Escape>', lambda e: self.login_window.destroy())
    
    def create_logo(self, parent):
        """Créer le logo SNTP"""
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        logo_frame.pack(pady=30)
        
        # Essayer de charger sntp.png
        try:
            if os.path.exists("sntp.png"):
                from PIL import Image, ImageTk
                
                logo_image = Image.open("sntp.png")
                # Redimensionner le logo
                logo_image = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = ctk.CTkLabel(
                    logo_frame,
                    image=self.logo_photo,
                    text=""
                )
                logo_label.pack()
                
            else:
                # Logo text si pas d'image
                logo_label = ctk.CTkLabel(
                    logo_frame,
                    text="🏢",
                    font=ctk.CTkFont(size=80)
                )
                logo_label.pack()
                
        except Exception as e:
            print(f"⚠️ Erreur chargement logo sntp.png: {e}")
            # Logo emoji de fallback
            logo_label = ctk.CTkLabel(
                logo_frame,
                text="🏢",
                font=ctk.CTkFont(size=80)
            )
            logo_label.pack()
        
        # Nom de l'organisation
        org_label = ctk.CTkLabel(
            logo_frame,
            text="SNTP",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1f538d", "#2563a8")
        )
        org_label.pack(pady=(10, 0))
        
        org_subtitle = ctk.CTkLabel(
            logo_frame,
            text="Société Nationale des Travaux Publics",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70")
        )
        org_subtitle.pack()
    
    def authenticate(self):
        """Authentifier l'utilisateur avec seulement le mot de passe"""
        password = self.password_entry.get().strip()
        
        if not password:
            messagebox.showerror(
                "Erreur",
                "❌ Veuillez entrer votre mot de passe",
                parent=self.login_window
            )
            self.password_entry.focus()
            return
        
        # Authentification avec email par défaut "admin"
        if self.db.authenticate_admin("admin", password):
            # Succès
            messagebox.showinfo(
                "Succès",
                "✅ Authentification réussie!\n\nBienvenue dans l'administration",
                parent=self.login_window
            )
            
            self.login_window.destroy()
            
            # Appeler le callback de succès
            if self.on_success:
                self.on_success()
                
        else:
            # Échec
            messagebox.showerror(
                "Erreur",
                "❌ Mot de passe incorrect\n\nVeuillez réessayer",
                parent=self.login_window
            )
            
            # Effacer et refocuser
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
            
            # Animation d'erreur (secouer la fenêtre)
            self.shake_window()
    
    def shake_window(self):
        """Animation de secousse pour indiquer une erreur"""
        original_x = self.login_window.winfo_x()
        
        def shake_step(step):
            if step < 6:
                offset = 10 if step % 2 == 0 else -10
                self.login_window.geometry(f"+{original_x + offset}+{self.login_window.winfo_y()}")
                self.login_window.after(50, lambda: shake_step(step + 1))
            else:
                self.login_window.geometry(f"+{original_x}+{self.login_window.winfo_y()}")
        
        shake_step(0)
