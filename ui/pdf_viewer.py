import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image
import fitz  # PyMuPDF
from customtkinter import CTkImage
import io

class PDFViewer(ctk.CTkToplevel):
    """Viewer PDF modernisé avec CustomTkinter - Lecture seule"""

    def __init__(self, parent, filepath: str, filename: str):
        super().__init__(parent)

        self.filepath = filepath
        self.filename = filename
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.page_images = {}

        # Configuration de la fenêtre
        self.title(f"🔒 Lecture seule - {filename}")
        self.geometry("1200x900")
        self.resizable(True, True)
        
        # Rendre la fenêtre modale
        self.transient(parent)
        self.grab_set()

        # Centrer
        self.center_window()

        # Charger le PDF
        if not self.load_pdf():
            self.destroy()
            return

        # Créer l'interface
        self.create_widgets()

        # Afficher la première page
        self.display_page(0)

        # Désactiver les raccourcis dangereux
        self.disable_save_shortcuts()
        
        # Focus pour les raccourcis clavier
        self.focus()

    def center_window(self):
        """Centrer la fenêtre"""
        self.update_idletasks()
        width = 1200
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_pdf(self) -> bool:
        """Charger le document PDF"""
        try:
            self.pdf_document = fitz.open(self.filepath)
            self.total_pages = len(self.pdf_document)
            print(f"✅ PDF chargé: {self.total_pages} pages - {self.filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement PDF: {e}")
            messagebox.showerror(
                "Erreur PDF", 
                f"❌ Impossible de charger le PDF:\n\n{str(e)}\n\nVérifiez que PyMuPDF est installé:\npip install PyMuPDF",
                parent=self
            )
            return False

    def create_widgets(self):
        """Créer l'interface"""
        # ============= EN-TÊTE AVEC AVERTISSEMENT SÉCURISÉ =============
        header = ctk.CTkFrame(
            self,
            height=90,
            corner_radius=0,
            fg_color=("#dc3545", "#b02a37")
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # Frame gauche avec icône de sécurité
        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", padx=30, pady=20)

        # Conteneur pour icône + texte
        title_container = ctk.CTkFrame(left_header, fg_color="transparent")
        title_container.pack(anchor="w")

        # Icône de sécurité
        ctk.CTkLabel(
            title_container,
            text="🔒",
            font=ctk.CTkFont(size=24),
            text_color=("#ffffff", "#ffffff")
        ).pack(side="left", padx=(0, 10))

        # Conteneur pour les textes
        text_container = ctk.CTkFrame(title_container, fg_color="transparent")
        text_container.pack(side="left")

        # Titre du fichier
        ctk.CTkLabel(
            text_container,
            text=self.filename,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w"
        ).pack(anchor="w")

        # Avertissement sécurité
        ctk.CTkLabel(
            text_container,
            text="🚫 MODE LECTURE SEULE • Téléchargement, impression et copie DÉSACTIVÉS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#ffeb3b", "#ffee58"),
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        # Bouton fermer sécurisé
        ctk.CTkButton(
            header,
            text="✖️ Fermer",
            width=120,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#000000", "#1a1a1a"),
            hover_color=("#1a1a1a", "#2a2a2a"),
            text_color=("#ffffff", "#ffffff"),
            command=self.close_viewer
        ).pack(side="right", padx=30)

        # ============= BARRE DE NAVIGATION AMÉLIORÉE =============
        navbar = ctk.CTkFrame(
            self,
            height=80,
            corner_radius=0,
            fg_color=("#f8f9fa", "#2b2b2b")
        )
        navbar.pack(fill="x")
        navbar.pack_propagate(False)

        # Frame centrale pour navigation
        nav_center = ctk.CTkFrame(navbar, fg_color="transparent")
        nav_center.pack(expand=True, pady=15)

        # Boutons de navigation avec icônes
        nav_buttons = ctk.CTkFrame(nav_center, fg_color="transparent")
        nav_buttons.pack(side="left", padx=20)

        # Groupe boutons gauche
        buttons_data = [
            ("⏮️ Première", self.first_page, "#6c757d"),
            ("⬅️ Précédente", self.previous_page, "#495057"),
        ]

        for text, command, color in buttons_data:
            ctk.CTkButton(
                nav_buttons,
                text=text,
                width=120,
                height=45,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=(color, "#343a40"),
                hover_color=("#5a6268", "#454d55"),
                command=command
            ).pack(side="left", padx=3)

        # Indicateur de page centré et amélioré
        page_container = ctk.CTkFrame(nav_buttons, fg_color=("#e9ecef", "#343a40"), corner_radius=8)
        page_container.pack(side="left", padx=20)

        self.page_label = ctk.CTkLabel(
            page_container,
            text=f"📄 Page 1 / {self.total_pages}",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=160,
            text_color=("#495057", "#ffffff")
        )
        self.page_label.pack(padx=15, pady=10)

        # Groupe boutons droite
        buttons_data2 = [
            ("Suivante ➡️", self.next_page, "#495057"),
            ("Dernière ⏭️", self.last_page, "#6c757d"),
        ]

        for text, command, color in buttons_data2:
            ctk.CTkButton(
                nav_buttons,
                text=text,
                width=120,
                height=45,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=(color, "#343a40"),
                hover_color=("#5a6268", "#454d55"),
                command=command
            ).pack(side="left", padx=3)

        # Contrôles de zoom améliorés
        zoom_frame = ctk.CTkFrame(nav_center, fg_color="transparent")
        zoom_frame.pack(side="left", padx=30)

        ctk.CTkLabel(
            zoom_frame,
            text="🔍 Zoom:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#495057", "#ffffff")
        ).pack(side="left", padx=(0, 10))

        # Bouton zoom out
        ctk.CTkButton(
            zoom_frame,
            text="➖",
            width=45,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#32b349", "#229143"),
            command=self.zoom_out
        ).pack(side="left", padx=2)

        # Indicateur zoom
        self.zoom_label = ctk.CTkLabel(
            zoom_frame,
            text="100%",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=60,
            fg_color=("#e9ecef", "#343a40"),
            corner_radius=6,
            text_color=("#495057", "#ffffff")
        )
        self.zoom_label.pack(side="left", padx=5)

        # Bouton zoom in
        ctk.CTkButton(
            zoom_frame,
            text="➕",
            width=45,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#32b349", "#229143"),
            command=self.zoom_in
        ).pack(side="left", padx=2)

        # Bouton reset zoom
        ctk.CTkButton(
            zoom_frame,
            text="🎯",
            width=45,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#17a2b8", "#138496"),
            hover_color=("#20a9cc", "#1e91a6"),
            command=self.reset_zoom
        ).pack(side="left", padx=8)

        # ============= ZONE D'AFFICHAGE AVEC SCROLLBARS =============
        display_container = ctk.CTkFrame(
            self,
            fg_color=("gray90", "gray10")
        )
        display_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Canvas avec couleur de fond adaptée au thème
        self.canvas = Canvas(
            display_container,
            bg="#f8f9fa" if ctk.get_appearance_mode() == "Light" else "#1a1a1a",
            highlightthickness=0,
            relief="flat"
        )

        # Scrollbars CustomTkinter
        v_scrollbar = ctk.CTkScrollbar(
            display_container,
            orientation="vertical",
            command=self.canvas.yview
        )
        h_scrollbar = ctk.CTkScrollbar(
            display_container,
            orientation="horizontal", 
            command=self.canvas.xview
        )

        # Configuration du canvas
        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # Pack avec ordre correct
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame pour contenir l'image dans le canvas
        self.canvas_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_window = self.canvas.create_window(0, 0, window=self.canvas_frame, anchor="nw")

        # Label pour l'image de la page
        self.image_label = ctk.CTkLabel(
            self.canvas_frame,
            text="📄 Chargement...",
            font=ctk.CTkFont(size=16),
            fg_color="transparent"
        )
        self.image_label.pack(padx=20, pady=20)

        # Événements de scroll et redimensionnement
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.bind('<Configure>', self.on_window_configure)

    def on_canvas_configure(self, event):
        """Ajuster la taille du canvas"""
        # Mettre à jour la région de scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Centrer le contenu si plus petit que le canvas
        canvas_width = event.width
        frame_width = self.canvas_frame.winfo_reqwidth()
        
        if frame_width < canvas_width:
            # Centrer horizontalement
            x = (canvas_width - frame_width) // 2
            self.canvas.coords(self.canvas_window, x, 0)
        else:
            self.canvas.coords(self.canvas_window, 0, 0)

    def on_window_configure(self, event):
        """Ajuster lors du redimensionnement de la fenêtre"""
        if event.widget == self:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def display_page(self, page_num: int):
        """Afficher une page du PDF"""
        if page_num < 0 or page_num >= self.total_pages:
            return

        try:
            self.current_page = page_num

            # Clé de cache avec zoom
            cache_key = f"{page_num}_{self.zoom_level}"
            if cache_key in self.page_images:
                ctk_image = self.page_images[cache_key]
                print(f"📋 Page {page_num + 1} chargée depuis le cache")
            else:
                # Afficher un message de chargement
                self.image_label.configure(
                    image=None,
                    text=f"⏳ Chargement de la page {page_num + 1}...",
                    text_color=("#6c757d", "#adb5bd")
                )
                self.update()

                # Rendre la page avec PyMuPDF
                page = self.pdf_document[page_num]
                mat = fitz.Matrix(self.zoom_level, self.zoom_level)
                pix = page.get_pixmap(matrix=mat)

                # Convertir en image PIL
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))

                # Créer CTkImage avec support High DPI
                ctk_image = CTkImage(
                    light_image=img, 
                    dark_image=img, 
                    size=(img.width, img.height)
                )

                # Mettre en cache (limiter à 3 pages pour la mémoire)
                if len(self.page_images) >= 3:
                    # Supprimer l'entrée la plus ancienne
                    oldest_key = next(iter(self.page_images))
                    del self.page_images[oldest_key]
                
                self.page_images[cache_key] = ctk_image
                print(f"✅ Page {page_num + 1} rendue et mise en cache (zoom: {int(self.zoom_level * 100)}%)")

            # Afficher l'image dans le CTkLabel
            self.image_label.configure(image=ctk_image, text="")

            # Mettre à jour la région de scroll après un court délai
            self.after(100, self.update_scroll_region)

            # Mettre à jour l'indicateur de page
            self.page_label.configure(text=f"📄 Page {page_num + 1} / {self.total_pages}")

        except Exception as e:
            print(f"❌ Erreur affichage page {page_num + 1}: {e}")
            self.image_label.configure(
                image=None,
                text=f"❌ Erreur d'affichage\nPage {page_num + 1}\n\n{str(e)}",
                text_color=("#dc3545", "#e04555")
            )

    def update_scroll_region(self):
        """Mettre à jour la région de scroll"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def first_page(self):
        """Aller à la première page"""
        print("⏮️ Première page")
        self.display_page(0)

    def previous_page(self):
        """Page précédente"""
        if self.current_page > 0:
            print(f"⬅️ Page précédente: {self.current_page}")
            self.display_page(self.current_page - 1)

    def next_page(self):
        """Page suivante"""
        if self.current_page < self.total_pages - 1:
            print(f"➡️ Page suivante: {self.current_page + 2}")
            self.display_page(self.current_page + 1)

    def last_page(self):
        """Aller à la dernière page"""
        print("⏭️ Dernière page")
        self.display_page(self.total_pages - 1)

    def zoom_in(self):
        """Augmenter le zoom"""
        if self.zoom_level < 3.0:
            self.zoom_level = min(3.0, self.zoom_level + 0.25)
            self.page_images.clear()
            self.display_page(self.current_page)
            self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
            print(f"🔍+ Zoom: {int(self.zoom_level * 100)}%")

    def zoom_out(self):
        """Diminuer le zoom"""
        if self.zoom_level > 0.5:
            self.zoom_level = max(0.5, self.zoom_level - 0.25)
            self.page_images.clear()
            self.display_page(self.current_page)
            self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
            print(f"🔍- Zoom: {int(self.zoom_level * 100)}%")

    def reset_zoom(self):
        """Réinitialiser le zoom à 100%"""
        self.zoom_level = 1.0
        self.page_images.clear()
        self.display_page(self.current_page)
        self.zoom_label.configure(text="100%")
        print("🎯 Zoom réinitialisé à 100%")

    def on_mousewheel(self, event):
        """Gérer le scroll avec la molette"""
        # Scroll vertical
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def disable_save_shortcuts(self):
        """Désactiver TOUS les raccourcis dangereux"""
        dangerous_shortcuts = [
            '<Control-s>', '<Control-S>',  # Sauvegarder
            '<Control-p>', '<Control-P>',  # Imprimer
            '<Control-c>', '<Control-C>',  # Copier
            '<Control-a>', '<Control-A>',  # Sélectionner tout
            '<Control-x>', '<Control-X>',  # Couper
            '<Control-v>', '<Control-V>',  # Coller
            '<F5>',                        # Actualiser
            '<Control-d>', '<Control-D>',  # Dupliquer
            '<Control-o>', '<Control-O>',  # Ouvrir
            '<Control-n>', '<Control-N>',  # Nouveau
        ]
        
        for shortcut in dangerous_shortcuts:
            self.bind(shortcut, self.block_action)

        # Raccourcis de navigation autorisés
        navigation_shortcuts = [
            ('<Left>', lambda e: self.previous_page()),
            ('<Right>', lambda e: self.next_page()),
            ('<Up>', lambda e: self.canvas.yview_scroll(-1, "units")),
            ('<Down>', lambda e: self.canvas.yview_scroll(1, "units")),
            ('<Home>', lambda e: self.first_page()),
            ('<End>', lambda e: self.last_page()),
            ('<Prior>', lambda e: self.previous_page()),  # Page Up
            ('<Next>', lambda e: self.next_page()),       # Page Down
            ('<Escape>', lambda e: self.close_viewer()),
            ('<Control-plus>', lambda e: self.zoom_in()),
            ('<Control-minus>', lambda e: self.zoom_out()),
            ('<Control-0>', lambda e: self.reset_zoom()),
        ]
        
        for shortcut, command in navigation_shortcuts:
            self.bind(shortcut, command)

        print("🚫 Raccourcis de sécurité désactivés")

    def block_action(self, event=None):
        """Bloquer une action dangereuse"""
        messagebox.showwarning(
            "🔒 Action Bloquée",
            "Cette action est désactivée en mode lecture seule.\n\n"
            "🚫 Sauvegarde interdite\n"
            "🚫 Impression interdite\n" 
            "🚫 Copie interdite\n\n"
            "Ce document est protégé contre le téléchargement.",
            parent=self
        )
        print(f"🚫 Action bloquée: {event}")
        return "break"  # Empêcher la propagation

    def close_viewer(self):
        """Fermer le viewer proprement"""
        print("🚪 Fermeture du viewer PDF...")
        try:
            # Libérer les ressources
            if self.pdf_document:
                self.pdf_document.close()
                print("✅ Document PDF fermé")
            
            # Vider le cache d'images
            self.page_images.clear()
            print("✅ Cache images vidé")
            
            # Fermer la fenêtre
            self.destroy()
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la fermeture: {e}")
            self.destroy()
