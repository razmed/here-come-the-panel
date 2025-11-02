import os
import shutil
import subprocess
import platform
from typing import Tuple, Optional
from pathlib import Path

class FileHandler:
    """Gestionnaire de fichiers avec support complet de l'arborescence et des panels"""
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.doc', '.xls'}
    
    # Icônes par extension
    FILE_ICONS = {
        'pdf': '📕',
        'docx': '📘',
        'doc': '📘',
        'xlsx': '📗',
        'xls': '📗',
        'txt': '📄',
        'default': '📄'
    }
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """S'assurer que le répertoire d'upload existe"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            print(f"✅ Répertoire d'upload créé: {self.upload_dir}")
        else:
            print(f"✅ Répertoire d'upload existant: {self.upload_dir}")
    
    def get_file_icon(self, extension: str) -> str:
        """Récupérer l'icône correspondant à une extension"""
        return self.FILE_ICONS.get(extension.lower(), self.FILE_ICONS['default'])
    
    def is_allowed_file(self, filename: str) -> bool:
        """Vérifier si le fichier est autorisé"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.ALLOWED_EXTENSIONS
    
    def count_files_to_import(self, folder_path: str) -> int:
        """
        Compter le nombre total de fichiers valides à importer dans un dossier (récursif)
        
        Args:
            folder_path: Chemin du dossier à analyser
            
        Returns:
            Nombre total de fichiers importables
        """
        total_count = 0
        
        try:
            if not os.path.exists(folder_path):
                print(f"⚠️ Dossier introuvable: {folder_path}")
                return 0
            
            if not os.path.isdir(folder_path):
                print(f"⚠️ Le chemin n'est pas un dossier: {folder_path}")
                return 0
            
            # Parcourir récursivement tous les fichiers
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if self.is_allowed_file(filename):
                        total_count += 1
            
            print(f"📊 Total de fichiers à importer: {total_count}")
            return total_count
            
        except Exception as e:
            print(f"❌ Erreur lors du comptage des fichiers: {e}")
            return 0
    
    def save_file(self, source_path: str, filename: str, subfolder: str = "") -> Tuple[bool, str]:
        """
        Enregistrer un fichier dans le répertoire d'upload
        
        Args:
            source_path: Chemin source du fichier
            filename: Nom du fichier
            subfolder: Sous-dossier optionnel
            
        Returns:
            Tuple (succès, chemin_destination)
        """
        try:
            # Vérifier que le fichier source existe
            if not os.path.exists(source_path):
                print(f"❌ Fichier source introuvable: {source_path}")
                return False, ""
            
            # Créer le chemin de destination
            if subfolder:
                dest_dir = os.path.join(self.upload_dir, subfolder)
                os.makedirs(dest_dir, exist_ok=True)
            else:
                dest_dir = self.upload_dir
            
            dest_path = os.path.join(dest_dir, filename)
            
            # Gérer les doublons
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(dest_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                filename = f"{base}_{counter}{ext}"
                dest_path = os.path.join(dest_dir, filename)
            
            # Copier le fichier
            shutil.copy2(source_path, dest_path)
            print(f"✅ Fichier copié: {filename} -> {dest_path}")
            
            return True, dest_path
            
        except Exception as e:
            print(f"❌ Erreur lors de la copie du fichier {filename}: {e}")
            return False, ""
    
    def save_files_from_folder(self, folder_path: str, db, parent_folder_id: Optional[int] = None) -> int:
        """
        Importer un dossier complet avec TOUS ses fichiers et sous-dossiers
        (Version compatible avec ancienne base de données sans panel)
        
        Args:
            folder_path: Chemin du dossier à importer
            db: Instance de la base de données
            parent_folder_id: ID du dossier parent dans la BDD
            
        Returns:
            Nombre total de fichiers importés
        """
        return self.save_files_from_folder_with_panel(folder_path, db, parent_folder_id, 'interface_emp')
    
    def save_files_from_folder_with_panel(self, folder_path: str, db, 
                                          parent_folder_id: Optional[int] = None,
                                          panel: str = 'interface_emp',
                                          progress_callback=None,
                                          total: int = 0) -> int:
        """
        Importer un dossier complet avec TOUS ses fichiers et sous-dossiers dans un panel spécifique
        
        Args:
            folder_path: Chemin du dossier à importer
            db: Instance de la base de données
            parent_folder_id: ID du dossier parent dans la BDD
            panel: Panel cible pour l'import
            progress_callback: Fonction de callback pour la progression (current, total)
            total: Nombre total de fichiers (pour la progression)
            
        Returns:
            Nombre total de fichiers importés
        """
        total_files = 0
        current_progress = [0]  # Liste mutable pour partager entre fonctions récursives
        
        try:
            folder_name = os.path.basename(folder_path)
            print(f"\n📁 Importation du dossier: {folder_name} dans panel {panel}")
            
            # Créer le dossier dans la base de données avec le panel
            current_folder_id = db.create_folder(folder_name, parent_folder_id, panel)
            print(f"   ✅ Dossier créé en BDD (ID: {current_folder_id}, Panel: {panel})")
            
            # Lister tous les éléments du dossier
            items = os.listdir(folder_path)
            
            # Traiter les fichiers
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    # C'est un fichier
                    if self.is_allowed_file(item):
                        print(f"   📄 Importation du fichier: {item}")
                        
                        # Copier le fichier physiquement
                        success, dest_path = self.save_file(item_path, item, folder_name)
                        
                        if success:
                            # Enregistrer dans la base de données
                            db.add_file(current_folder_id, item, dest_path)
                            total_files += 1
                            current_progress[0] += 1
                            
                            # Appeler le callback de progression
                            if progress_callback and total > 0:
                                progress_callback(current_progress[0], total)
                            
                            print(f"      ✅ Fichier importé avec succès ({current_progress[0]}/{total})")
                        else:
                            print(f"      ❌ Échec de l'importation du fichier")
                    else:
                        print(f"   ⚠️ Fichier ignoré (extension non autorisée): {item}")
            
            # Traiter les sous-dossiers récursivement
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    # C'est un sous-dossier, traiter récursivement
                    print(f"   📂 Sous-dossier détecté: {item}")
                    sub_count = self._import_subfolder_recursive(
                        item_path, 
                        db, 
                        current_folder_id, 
                        panel, 
                        progress_callback, 
                        total, 
                        current_progress
                    )
                    total_files += sub_count
            
            print(f"✅ Dossier '{folder_name}' importé: {total_files} fichier(s)")
            return total_files
            
        except Exception as e:
            print(f"❌ Erreur lors de l'importation du dossier: {e}")
            import traceback
            traceback.print_exc()
            return total_files
    
    def _import_subfolder_recursive(self, folder_path: str, db, 
                                   parent_folder_id: int,
                                   panel: str,
                                   progress_callback,
                                   total: int,
                                   current_progress: list) -> int:
        """
        Fonction auxiliaire pour importer récursivement un sous-dossier
        
        Args:
            folder_path: Chemin du dossier
            db: Instance BDD
            parent_folder_id: ID du parent
            panel: Panel
            progress_callback: Callback de progression
            total: Total de fichiers
            current_progress: Liste mutable [count] pour partager la progression
            
        Returns:
            Nombre de fichiers importés
        """
        total_files = 0
        
        try:
            folder_name = os.path.basename(folder_path)
            
            # Créer le sous-dossier
            current_folder_id = db.create_folder(folder_name, parent_folder_id, panel)
            
            # Lister les éléments
            items = os.listdir(folder_path)
            
            # Traiter les fichiers
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    if self.is_allowed_file(item):
                        success, dest_path = self.save_file(item_path, item, folder_name)
                        
                        if success:
                            db.add_file(current_folder_id, item, dest_path)
                            total_files += 1
                            current_progress[0] += 1
                            
                            # Callback de progression
                            if progress_callback and total > 0:
                                progress_callback(current_progress[0], total)
            
            # Traiter les sous-dossiers récursivement
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    sub_count = self._import_subfolder_recursive(
                        item_path, 
                        db, 
                        current_folder_id, 
                        panel, 
                        progress_callback, 
                        total, 
                        current_progress
                    )
                    total_files += sub_count
            
            return total_files
            
        except Exception as e:
            print(f"❌ Erreur import sous-dossier: {e}")
            return total_files
    
    def open_file(self, filepath: str) -> bool:
        """
        Ouvrir un fichier avec l'application par défaut du système
        
        Args:
            filepath: Chemin du fichier à ouvrir
            
        Returns:
            True si succès, False sinon
        """
        try:
            if not os.path.exists(filepath):
                print(f"❌ Fichier introuvable: {filepath}")
                return False
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            
            print(f"✅ Fichier ouvert: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ouverture du fichier: {e}")
            return False
    
    def delete_file(self, filepath: str) -> bool:
        """
        Supprimer un fichier physique
        
        Args:
            filepath: Chemin du fichier à supprimer
            
        Returns:
            True si succès, False sinon
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Fichier supprimé: {filepath}")
                return True
            else:
                print(f"⚠️ Fichier déjà absent: {filepath}")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du fichier: {e}")
            return False
    
    def get_file_size(self, filepath: str) -> int:
        """Récupérer la taille d'un fichier en octets"""
        try:
            return os.path.getsize(filepath) if os.path.exists(filepath) else 0
        except:
            return 0
    
    def format_file_size(self, size: int) -> str:
        """Formater la taille d'un fichier"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def is_pdf(self, filename: str) -> bool:
        """Vérifier si un fichier est un PDF"""
        return filename.lower().endswith('.pdf')
    
    def is_downloadable(self, filename: str) -> bool:
        """Vérifier si un fichier est téléchargeable (pas PDF)"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in {'.docx', '.xlsx', '.doc', '.xls'}
