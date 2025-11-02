import customtkinter as ctk
from typing import Callable

class PanelSelectorWindow:
    """Fenêtre de sélection du panel pour l'administration"""
    
    PANELS = [
        {
            'id': 'certification',
            'name': 'Certification',
            'icon': '📜',
            'color': '#28a745',
            'hover': '#32b349',
            'description': 'Gérer les fichiers de certification'
        },
        {
            'id': 'entete',
            'name': 'En-tête',
            'icon': '📋',
            'color': '#1f538d',
            'hover': '#2563a8',
            'description': 'Gérer les fichiers d\'en-tête'
        },
        {
            'id': 'interface_emp',
            'name': 'Interface Employés',
            'icon': '👥',
            'color': '#17a2b8',
            'hover': '#20a9cc',
            'description': 'Gérer les fichiers de l\'interface employés'
        },
        {
            'id': 'autre',
            'name': 'Autre',
            'icon': '📦',
            'color': '#6c757d',
            'hover': '#7c858d',
            'description': 'Gérer les autres fichiers'
        }
    ]
    
    def __init__(self, parent, on_panel_selected: Callable):
        self.parent = parent
        self.on_panel_selected = on_panel_selected
        
        self.create_window()
    
    def create_window(self):
        """Créer la fenêtre de sélection"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Administration - Sélection du Panel")
        self.window.geometry("900x650")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Centrer
        self.center_window()
        
        # En-tête
        header = ctk.CTkFrame(
            self.window,
            height=100,
            fg_color=("#1a1a1a", "#0d0d0d"),
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Titre
        ctk.CTkLabel(
            header,
            text="⚙️ Administration - Sélection du Panel",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=30)
        
        # Bouton fermer
        ctk.CTkButton(
            header,
            text="✖️ Fermer",
            width=120,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=self.window.destroy
        ).pack(side="right", padx=30)
        
        # Message d'instructions
        instructions = ctk.CTkFrame(
            self.window,
            fg_color=("#e7f3ff", "#1a3a52"),
            corner_radius=15
        )
        instructions.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            instructions,
            text="📌 Sélectionnez le panel que vous souhaitez administrer",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1f538d", "#2563a8")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            instructions,
            text="Chaque panel possède ses propres dossiers et fichiers",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        ).pack(pady=(0, 20))
        
        # Grille de panels (2x2)
        panels_container = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        panels_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Créer les cartes de panels
        for i, panel in enumerate(self.PANELS):
            row = i // 2
            col = i % 2
            self.create_panel_card(panels_container, panel, row, col)
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.window.update_idletasks()
        width = 900
        height = 650
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_panel_card(self, parent, panel: dict, row: int, col: int):
        """Créer une carte de panel"""
        card = ctk.CTkFrame(
            parent,
            width=400,
            height=200,
            fg_color=(panel['color'], panel['color']),
            corner_radius=20,
            border_width=3,
            border_color=("white", "gray20")
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        card.pack_propagate(False)
        
        # Configuration de la grille
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Contenu de la carte
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True)
        
        # Icône
        ctk.CTkLabel(
            content,
            text=panel['icon'],
            font=ctk.CTkFont(size=60)
        ).pack(pady=(20, 15))
        
        # Nom
        ctk.CTkLabel(
            content,
            text=panel['name'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(0, 10))
        
        # Description
        ctk.CTkLabel(
            content,
            text=panel['description'],
            font=ctk.CTkFont(size=12),
            text_color=("white", "white"),
            wraplength=350
        ).pack(pady=(0, 20))
        
        # Rendre cliquable
        def on_click(event):
            self.select_panel(panel['id'])
        
        def on_enter(event):
            card.configure(
                fg_color=panel['hover'],
                border_color=("#ffeb3b", "#ffc107")
            )
        
        def on_leave(event):
            card.configure(
                fg_color=panel['color'],
                border_color=("white", "gray20")
            )
        
        # Lier les événements
        for widget in [card, content]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.configure(cursor="hand2")
    
    def select_panel(self, panel_id: str):
        """Sélectionner un panel et ouvrir l'administration"""
        print(f"✅ Panel sélectionné: {panel_id}")
        
        # Fermer la fenêtre
        self.window.destroy()
        
        # Appeler le callback
        if self.on_panel_selected:
            self.on_panel_selected(panel_id)