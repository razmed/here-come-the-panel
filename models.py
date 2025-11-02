from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import bcrypt

@dataclass
class Admin:
    """Modèle pour un administrateur avec sécurité bcrypt"""
    id: int
    email: str
    password_hash: str
    created_at: datetime
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hasher un mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Vérifier un mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

@dataclass
class Folder:
    """Modèle pour un dossier"""
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime
    
    def __str__(self):
        return self.name

@dataclass
class File:
    """Modèle pour un fichier avec métadonnées de recherche"""
    id: int
    folder_id: int
    filename: str
    filepath: str
    uploaded_at: datetime
    file_size: int = 0
    file_hash: str = ""
    
    def __str__(self):
        return self.filename
    
    @property
    def extension(self) -> str:
        """Récupérer l'extension du fichier"""
        return self.filename.rsplit('.', 1)[-1].lower() if '.' in self.filename else ''
    
    @property
    def size(self) -> int:
        """Récupérer la taille du fichier en octets"""
        import os
        try:
            return os.path.getsize(self.filepath) if os.path.exists(self.filepath) else self.file_size
        except:
            return self.file_size
    
    @property
    def size_formatted(self) -> str:
        """Récupérer la taille du fichier formatée"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

@dataclass
class SearchFilter:
    """Modèle pour les filtres de recherche"""
    filename: str = ""
    extension: str = ""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    folder_id: Optional[int] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
