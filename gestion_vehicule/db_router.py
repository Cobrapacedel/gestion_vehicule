class DeletedFineRouter:
    """
    Routeur personnalisé pour gérer les amendes supprimées dans une base de données séparée (archive).
    """
    def db_for_read(self, model, **hints):
        """
        Lors de la lecture des amendes supprimées, on les dirige vers la base de données 'archive'.
        """
        if model._meta.model_name == 'deletedfine':  # Vérifie si le modèle est 'DeletedFine'
            return 'archive'
        return None

    def db_for_write(self, model, **hints):
        """
        Lors de l'écriture d'une amende supprimée, on l'enregistre dans la base de données 'archive'.
        """
        if model._meta.model_name == 'deletedfine':  # Vérifie si le modèle est 'DeletedFine'
            return 'archive'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Autorise ou bloque les migrations sur la base 'archive' pour le modèle 'DeletedFine'.
        """
        if model_name == 'deletedfine':  # Vérifie si on travaille sur 'DeletedFine'
            return db == 'archive'  # La migration ne se fait que sur la base 'archive'
        return db == 'default'  # Les autres modèles migrent dans la base par défaut