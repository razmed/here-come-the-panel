import sqlite3
import os
import hashlib

def migrate_database(db_path="portal.db"):
    """Migrer la base de données pour ajouter les nouvelles colonnes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ajouter file_size si elle n'existe pas
        if 'file_size' not in columns:
            print("Ajout de la colonne file_size...")
            cursor.execute("ALTER TABLE files ADD COLUMN file_size INTEGER DEFAULT 0")
            
            # Calculer les tailles des fichiers existants
            cursor.execute("SELECT id, filepath FROM files")
            files = cursor.fetchall()
            
            for file_id, filepath in files:
                try:
                    if os.path.exists(filepath):
                        size = os.path.getsize(filepath)
                        cursor.execute("UPDATE files SET file_size = ? WHERE id = ?", (size, file_id))
                        print(f"Taille mise à jour pour le fichier ID {file_id}: {size} bytes")
                except Exception as e:
                    print(f"Erreur calcul taille pour {filepath}: {e}")
        
        # Ajouter file_hash si elle n'existe pas
        if 'file_hash' not in columns:
            print("Ajout de la colonne file_hash...")
            cursor.execute("ALTER TABLE files ADD COLUMN file_hash TEXT DEFAULT ''")
            
            # Calculer les hash des fichiers existants
            cursor.execute("SELECT id, filepath FROM files")
            files = cursor.fetchall()
            
            for file_id, filepath in files:
                try:
                    if os.path.exists(filepath):
                        file_hash = calculate_file_hash(filepath)
                        cursor.execute("UPDATE files SET file_hash = ? WHERE id = ?", (file_hash, file_id))
                        print(f"Hash calculé pour le fichier ID {file_id}: {file_hash[:16]}...")
                except Exception as e:
                    print(f"Erreur calcul hash pour {filepath}: {e}")
        
        # Vérifier la table admins pour bcrypt
        cursor.execute("PRAGMA table_info(admins)")
        admin_columns = [column[1] for column in cursor.fetchall()]
        
        if 'password' in admin_columns and 'password_hash' not in admin_columns:
            print("Migration des mots de passe vers bcrypt...")
            
            # Ajouter la nouvelle colonne
            cursor.execute("ALTER TABLE admins ADD COLUMN password_hash TEXT")
            
            # Migrer les mots de passe existants
            import bcrypt
            cursor.execute("SELECT id, password FROM admins WHERE password_hash IS NULL")
            admins = cursor.fetchall()
            
            for admin_id, old_password in admins:
                password_hash = bcrypt.hashpw(old_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE admins SET password_hash = ? WHERE id = ?", (password_hash, admin_id))
                print(f"Mot de passe migré pour admin ID {admin_id}")
        
        # Créer les index pour optimiser la recherche
        print("Création des index...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size)")
            print("Index créés avec succès")
        except Exception as e:
            print(f"Erreur lors de la création des index: {e}")
        
        conn.commit()
        print("✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def calculate_file_hash(filepath: str) -> str:
    """Calculer le hash SHA256 d'un fichier"""
    try:
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""

if __name__ == "__main__":
    migrate_database()
