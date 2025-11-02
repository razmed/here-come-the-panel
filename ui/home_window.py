import customtkinter as ctk
from tkinter import messagebox
import os
from typing import Callable

class HomeWindow(ctk.CTkFrame):
    """Interface d'accueil avec 4 boutons principaux"""
    
    def __init__(self, parent, db, file_handler, on_panel_select: Callable, on_entete_click: Callable):
        super().__init__(parent, fg_color="transparent")
        
        self.db = db
        self.file_handler = file_handler
        self.on_panel_select = on_panel_select
        self.on_entete_click = on_entete_click
        
        self.create_widgets()
    
    def create_widgets(self):
        """Créer l'interface d'accueil"""
        # Container principal avec l'image de fond
        main_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True)
        
        # Essayer de charger l'image interface.png en fond
        self.load_background(main_container)
        
        # Frame de contenu par-dessus le fond
        content_frame = ctk.CTkFrame(
            main_container,
            fg_color=("#ffffff", "#1a1a1a"),  # Semi-transparent
            corner_radius=20
        )
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titre principal
        title_label = ctk.CTkLabel(
            content_frame,
            text="🏢 PORTAIL DOCUMENT SNTP",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#1f538d", "#2563a8")
        )
        title_label.pack(pady=(40, 10))
        
        # Sous-titre
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text="Société Nationale des Travaux Publics",
            font=ctk.CTkFont(size=18),
            text_color=("gray40", "gray70")
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Grille de boutons (2x2)
        buttons_grid = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_grid.pack(padx=60, pady=(0, 40))
        
        # Définition des boutons
        buttons_config = [
            {
                'row': 0, 'col': 0,
                'text': '📜 Certification',
                'icon': '📜',
                'color': '#28a745',
                'hover': '#32b349',
                'command': lambda: self.on_panel_select('certification')
            },
            {
                'row': 0, 'col': 1,
                'text': '📋 En-tête',
                'icon': '📋',
                'color': '#1f538d',
                'hover': '#2563a8',
                'command': self.on_entete_click
            },
            {
                'row': 1, 'col': 0,
                'text': '👥 Interface Employés',
                'icon': '👥',
                'color': '#17a2b8',
                'hover': '#20a9cc',
                'command': lambda: self.on_panel_select('interface_emp')
            },
            {
                'row': 1, 'col': 1,
                'text': '📦 Autre',
                'icon': '📦',
                'color': '#6c757d',
                'hover': '#7c858d',
                'command': lambda: self.on_panel_select('autre')
            }
        ]
        
        # Créer les boutons
        for btn_config in buttons_config:
            self.create_main_button(
                buttons_grid,
                btn_config['row'],
                btn_config['col'],
                btn_config['text'],
                btn_config['icon'],
                btn_config['color'],
                btn_config['hover'],
                btn_config['command']
            )
        
        # Footer avec informations
        footer = ctk.CTkLabel(
            content_frame,
            text="Sélectionnez une catégorie pour commencer",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        footer.pack(pady=(0, 30))
    
    def load_background(self, parent):
        """Charger l'image de fond interface.png"""
        try:
            if os.path.exists("interface.png"):
                from PIL import Image
                
                # Charger l'image
                bg_image = Image.open("interface.png")
                
                # Obtenir la taille de l'écran
                screen_width = parent.winfo_screenwidth()
                screen_height = parent.winfo_screenheight()
                
                # Redimensionner l'image
                bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                
                # Appliquer un léger overlay pour améliorer la lisibilité
                overlay = Image.new('RGBA', bg_image.size, (255, 255, 255, 30))
                bg_image = bg_image.convert("RGBA")
                bg_image = Image.alpha_composite(bg_image, overlay)
                
                # Créer CTkImage
                self.bg_photo = ctk.CTkImage(
                    light_image=bg_image,
                    dark_image=bg_image,
                    size=(screen_width, screen_height)
                )
                
                # Label pour l'arrière-plan
                bg_label = ctk.CTkLabel(
                    parent,
                    image=self.bg_photo,
                    text=""
                )
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                bg_label.lower()
                
                print("✅ Interface.png chargé comme fond d'écran")
            else:
                print("⚠️ interface.png non trouvé")
                # Fond par défaut
                parent.configure(fg_color=("#f0f0f0", "#1a1a1a"))
                
        except Exception as e:
            print(f"⚠️ Erreur chargement interface.png: {e}")
            parent.configure(fg_color=("#f0f0f0", "#1a1a1a"))
    
    def create_main_button(self, parent, row: int, col: int, text: str, icon: str, 
                          color: str, hover_color: str, command: Callable):
        """Créer un bouton principal de l'interface"""
        # Frame pour le bouton
        button_frame = ctk.CTkFrame(
            parent,
            width=300,
            height=200,
            fg_color=(color, color),
            corner_radius=20,
            border_width=3,
            border_color=("white", "gray20")
        )
        button_frame.grid(row=row, column=col, padx=20, pady=20)
        button_frame.pack_propagate(False)
        
        # Icône
        icon_label = ctk.CTkLabel(
            button_frame,
            text=icon,
            font=ctk.CTkFont(size=60)
        )
        icon_label.pack(pady=(40, 20))
        
        # Texte
        text_label = ctk.CTkLabel(
            button_frame,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        text_label.pack()
        
        # Rendre le bouton cliquable
        def on_click(event):
            command()
        
        def on_enter(event):
            button_frame.configure(fg_color=hover_color, border_color=("#ffeb3b", "#ffc107"))
        
        def on_leave(event):
            button_frame.configure(fg_color=color, border_color=("white", "gray20"))
        
        # Lier les événements à tous les widgets
        for widget in [button_frame, icon_label, text_label]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.configure(cursor="hand2")