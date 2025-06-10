# 🚗 Gestion de Véhicules - Django

Une application web complète de gestion de véhicules développée avec Django.

## 📌 Fonctionnalités principales

- 🔐 Authentification JWT avec gestion des utilisateurs
- 🚘 Gestion des véhicules (voiture, moto, camion, etc.)
- 💸 Paiements, recharges et transactions automatisées
- 📄 Documents : carte grise, assurance, contrôle technique, renouvellement
- 📡 OTP pour la validation des connexions
- 📍 Péages et localisation
- 📬 Notifications automatiques
- 👮 Amendes avec paiement et recharge automatique
- 🔁 Prêts, transferts et ventes de véhicules
- 📊 Tableau de bord avec statistiques

## 🛠️ Technologies

- **Backend** : Django, Django REST Framework
- **Base de données** : PostgreSQL / SQLite
- **Frontend** : HTML, Tailwind CSS, HTMX
- **Sécurité** : Authentification JWT, Django Signals, OTP, GeoIP

## ⚙️ Installation

```bash
git clone git@github.com:Cobrapacedel/gestion_vehicule.git
cd gestion_vehicule
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver![avatar_cobra_rounded](https://github.com/user-attachments/assets/34fcd414-c0d1-4174-906e-8dc6034c92ff)
