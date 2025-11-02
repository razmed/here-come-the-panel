import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil

class EnteteChoiceWindow:
    """Fenêtre de choix pour En-tête: Visualiser PDF ou Télécharger DOCX"""
    
    def __init__(self, parent, pdf_viewer_callback, notification_manager=None):
        self.parent = parent
        self.pdf_viewer_callback = pdf_viewer_callback
        self.notification_manager = notification_manager
        
        # Chemins des fichiers en-tête
        self.pdf_path = "entete/en-tete.pdf"
        self.docx_path = "entete/en-tete.docx"
        
        # Vérifier que le dossier entete existe
        self.ensure_entete_folder()
        
        # Créer la fenêtre de choix
        self.create_choice_window()
    
    def ensure_entete_folder(self):
        """S'assurer que le dossier entete existe"""
        if not os.path.exists("entete"):
            os.makedirs("entete")
            print("✅ Dossier 'entete' créé")
            
            # Message informatif
            messagebox.showinfo(
                "Configuration",
                "📁 Le dossier 'entete' a été créé.\n\n"
                "Veuillez y placer les fichiers:\n"
                "• en-tete.pdf (pour visualisation)\n"
                "• en-tete.docx (pour téléchargement)"
            )
    
    def create_choice_window(self):
        """Créer la fenêtre de choix"""
        self.choice_window = ctk.CTkToplevel(self.parent)
        self.choice_window.title("En-tête - Choix d'action")
        self.choice_window.geometry("600x400")
        self.choice_window.transient(self.parent)
        self.choice_window.grab_set()
        self.choice_window.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # En-tête
        header = ctk.CTkFrame(
            self.choice_window,
            height=80,
            fg_color=("#1f538d", "#14375e"),
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📋 Document En-tête",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=25)
        
        # Contenu principal
        content = ctk.CTkFrame(
            self.choice_window,
            fg_color="transparent"
        )
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Message
        message = ctk.CTkLabel(
            content,
            text="Comment souhaitez-vous accéder au document en-tête ?",
            font=ctk.CTkFont(size=16),
            wraplength=500
        )
        message.pack(pady=(0, 30))
        
        # Frame pour les boutons
        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.pack(expand=True)
        
        # Bouton Visualiser PDF
        visualiser_button = ctk.CTkButton(
            buttons_frame,
            text="👁️ Visualiser le PDF\n(Lecture seule)",
            width=240,
            height=100,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#32b349", "#229143"),
            command=self.visualize_pdf
        )
        visualiser_button.pack(side="left", padx=10)
        
        # Bouton Télécharger DOCX
        download_button = ctk.CTkButton(
            buttons_frame,
            text="📥 Télécharger le DOCX\n(Modifiable)",
            width=240,
            height=100,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#17a2b8", "#138496"),
            hover_color=("#20a9cc", "#1e91a6"),
            command=self.download_docx
        )
        download_button.pack(side="left", padx=10)
        
        # Bouton Annuler
        cancel_button = ctk.CTkButton(
            content,
            text="❌ Annuler",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=("#dc3545", "#b02a37"),
            hover_color=("#e04555", "#c03545"),
            command=self.choice_window.destroy
        )
        cancel_button.pack(pady=(30, 0))
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.choice_window.update_idletasks()
        width = 600
        height = 400
        x = (self.choice_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.choice_window.winfo_screenheight() // 2) - (height // 2)
        self.choice_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def visualize_pdf(self):
        """Visualiser le PDF avec le viewer intégré"""
        if not os.path.exists(self.pdf_path):
            messagebox.showerror(
                "Fichier manquant",
                f"❌ Le fichier PDF n'existe pas:\n\n{self.pdf_path}\n\n"
                "Veuillez placer 'en-tete.pdf' dans le dossier 'entete'",
                parent=self.choice_window
            )
            return
        
        try:
            # Notification
            if self.notification_manager:
                self.notification_manager.show_app_notification(
                    "📋 En-tête",
                    "Ouverture du document en-tête en mode lecture seule"
                )
            
            # Fermer la fenêtre de choix
            self.choice_window.destroy()
            
            # Ouvrir avec le PDF viewer
            from .pdf_viewer import PDFViewer
            pdf_window = ctk.CTkToplevel(self.parent)
            PDFViewer(pdf_window, self.pdf_path, "en-tete.pdf")
            
            print("✅ PDF en-tête ouvert en mode visualisation")
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'ouvrir le PDF:\n\n{e}",
                parent=self.choice_window
            )
            print(f"❌ Erreur ouverture PDF: {e}")
    
    def download_docx(self):
        """Télécharger le fichier DOCX"""
        if not os.path.exists(self.docx_path):
            messagebox.showerror(
                "Fichier manquant",
                f"❌ Le fichier DOCX n'existe pas:\n\n{self.docx_path}\n\n"
                "Veuillez placer 'en-tete.docx' dans le dossier 'entete'",
                parent=self.choice_window
            )
            return
        
        try:
            # Demander où sauvegarder
            save_path = filedialog.asksaveasfilename(
                title="Enregistrer le document en-tête",
                defaultextension=".docx",
                initialfile="en-tete.docx",
                filetypes=[("Document Word", "*.docx"), ("Tous les fichiers", "*.*")],
                parent=self.choice_window
            )
            
            if save_path:
                # Copier le fichier
                shutil.copy2(self.docx_path, save_path)
                
                # Notification
                if self.notification_manager:
                    self.notification_manager.show_app_notification(
                        "✅ Téléchargement réussi",
                        f"Le document en-tête a été enregistré"
                    )
                
                messagebox.showinfo(
                    "Succès",
                    f"✅ Document téléchargé avec succès!\n\n{save_path}",
                    parent=self.choice_window
                )
                
                print(f"✅ DOCX en-tête téléchargé: {save_path}")
                
                # Fermer la fenêtre
                self.choice_window.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible de télécharger le fichier:\n\n{e}",
                parent=self.choice_window
            )
            print(f"❌ Erreur téléchargement DOCX: {e}")