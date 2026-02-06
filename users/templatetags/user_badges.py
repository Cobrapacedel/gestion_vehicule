from django import template

register = template.Library()

@register.inclusion_tag('users/_user_badges.html')
def user_badges(user):
    """
    Template tag pour afficher les badges d'un utilisateur :
    - is_active
    - is_staff
    - is_mechanic
    - roles business : dealer, agency, garage
    """
    badges = []

    # Statut actif/inactif
    if user.is_active:
        badges.append({"label": "Aktif", "color": "bg-green-500 text-white"})
    else:
        badges.append({"label": "Inaktif", "color": "bg-gray-400 text-white"})

    # Staff
    if getattr(user, "is_staff", False):
        badges.append({"label": "Staf", "color": "bg-blue-500 text-white"})

    # Mécanicien
    if getattr(user, "is_mechanic", False):
        badges.append({"label": "Mekanisyen", "color": "bg-yellow-500 text-black"})

    # Roles business
    role_labels = {
        "dealer": ("Konsesyonè", "bg-indigo-500 text-white"),
        "agency": ("Ajans Lokasyon", "bg-yellow-500 text-black"),
        "garage": ("Garaj", "bg-green-700 text-white")
    }
    role = getattr(user, "role", None)
    if role in role_labels:
        label, color = role_labels[role]
        badges.append({"label": label, "color": color})

    return {"badges": badges}