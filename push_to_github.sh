#!/data/data/com.termux/files/usr/bin/bash

# 📁 Vérifie que tu es dans un projet
echo "📂 Dossier courant : $(pwd)"
if [ ! -f "manage.py" ]; then
    echo "❌ Ce dossier ne semble pas contenir un projet Django (manage.py manquant)."
    exit 1
fi

# 🧱 Initialisation de Git si nécessaire
if [ ! -d ".git" ]; then
    echo "⚙️ Initialisation de Git..."
    git init
fi

# 📝 Ajout des fichiers
echo "🧩 Ajout des fichiers au suivi Git..."
git add .

# 🧾 Commit initial
read -p "📝 Message de commit : " commit_msg
[ -z "$commit_msg" ] && commit_msg="Initial commit"
git commit -m "$commit_msg"

# 🔗 Lien vers le dépôt distant
read -p "🔗 URL du dépôt GitHub (SSH ou HTTPS) : " repo_url

# Vérifie si le remote 'origin' existe déjà
if git remote | grep -q origin; then
    echo "🔄 Remote 'origin' déjà existant, remplacement..."
    git remote remove origin
fi

git remote add origin "$repo_url"

# 📤 Envoi vers GitHub
git branch -M main
git push -u origin main

echo -e "\n✅ Projet Django envoyé sur GitHub avec succès !"
