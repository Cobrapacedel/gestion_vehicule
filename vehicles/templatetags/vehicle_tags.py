from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# 🚗 Icône selon le type de véhicule
@register.simple_tag
def vehicle_icon(vehicle_type):
    icons = {
        "car": "🚗",
        "motorcycle": "🏍️",
        "truck": "🚚",
        "bus": "🚌",
    }
    return icons.get((vehicle_type or "").lower(), "🚘")


# 🟩 Badge du statut du véhicule
@register.filter(is_safe=True)
def vehicle_status_badge(status):
    labels = {
        "available": "Disponib",
        "rentals": "Lwaye",
        "sold": "Vann",
        "loaned": "Prete",
        "service": "Nan Garaj",
    }

    colors = {
        "available": "bg-green-200 text-green-800",
        "rentals": "bg-gray-200 text-gray-700",
        "sold": "bg-yellow-200 text-yellow-700",
        "loaned": "bg-blue-200 text-blue-700",
        "service": "bg-red-200 text-red-700",
    }

    if not status:
        status = "inconnu"

    label = labels.get(status.lower(), "Inconnu")
    color_class = colors.get(status.lower(), "bg-gray-100 text-gray-700")

    html = f'<span class="text-xs px-2 py-0.5 rounded-full font-semibold {color_class}">{label}</span>'
    return mark_safe(html)


# ⛽ Badge du type de carburant
@register.filter(is_safe=True)
def fuel_type_badge(fuel_type):
    """Retourne un badge coloré et une icône selon le type de carburant."""
    fuel_types = {
        "gasoline": {"label": "Gazolin", "icon": "⛽", "color": "bg-yellow-100 text-yellow-800"},
        "diesel": {"label": "Dizèl", "icon": "🚛", "color": "bg-gray-200 text-gray-800"},
        "electric": {"label": "Elektrik", "icon": "⚡", "color": "bg-blue-100 text-blue-800"},
        "hybrid": {"label": "Ibrid", "icon": "🌿", "color": "bg-green-100 text-green-800"},
        "gas": {"label": "Gaz", "icon": "🔥", "color": "bg-orange-100 text-orange-800"},
    }

    if not fuel_type:
        return mark_safe('<span class="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">N/A</span>')

    ft = fuel_types.get(fuel_type.lower(), {"label": fuel_type, "icon": "🚘", "color": "bg-gray-100 text-gray-700"})
    html = f'<span class="text-xs px-2 py-0.5 rounded-full font-medium {ft["color"]}">{ft["icon"]} {ft["label"]}</span>'
    return mark_safe(html)

# 🚗 Badge du type de voiture
@register.filter(is_safe=True)
def vehicle_type_badge(vehicle_type):
    """Retourne un badge coloré et une icône selon le type de voiture."""
    vehicle_types = {
        "car": {"label": "Vwati", "icon": "🚗", "color": "bg-yellow-100 text-yellow-800"},
        "truck": {"label": "Kamyon", "icon": "🚛", "color": "bg-gray-200 text-gray-800"},
        "bus": {"label": "Bis", "icon": "🚌", "color": "bg-blue-100 text-blue-800"},
        "motorcycle": {"label": "Motosiklèt", "icon": "🏍️", "color": "bg-green-100 text-green-800"},
    }

    if not vehicle_type:
        return mark_safe('<span class="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">N/A</span>')

    vt = vehicle_types.get(vehicle_type.lower(), {"label": vehicle_type, "icon": "🚘", "color": "bg-gray-100 text-gray-700"})
    html = f'<span class="text-xs px-2 py-0.5 rounded-full font-medium {vt["color"]}">{vt["icon"]} {vt["label"]}</span>'
    return mark_safe(html)
    

# 📄 Récupération des premiers contrats selon le type
@register.filter
def first_bought_contract(vehicle):
    """Retourne le premier contrat de type 'bought' pour un véhicule."""
    try:
        return vehicle.contracts.filter(contract_type="bought").first()
    except Exception:
        return None


@register.filter
def first_sold_contract(vehicle):
    """Retourne le premier contrat de type 'sold' pour un véhicule."""
    try:
        return vehicle.contracts.filter(contract_type="sold").first()
    except Exception:
        return None


@register.filter
def first_rental_contract(vehicle):
    """Retourne le premier contrat de location ('rental') pour un véhicule."""
    try:
        return vehicle.contracts.filter(contract_type="rental").first()
    except Exception:
        return None


# 🧾 Badge du type de contrat
@register.filter(is_safe=True)
def contract_badge(contract_type):
    """Affiche un badge coloré et une icône selon le type de contrat."""
    contracts = {
        "bought": {"label": "Achat", "icon": "🛒", "color": "bg-blue-100 text-blue-800"},
        "sold": {"label": "Vente", "icon": "💰", "color": "bg-green-100 text-green-800"},
        "rental": {"label": "Location", "icon": "📄", "color": "bg-yellow-100 text-yellow-800"},
        "loan": {"label": "Prêt", "icon": "🤝", "color": "bg-purple-100 text-purple-800"},
    }

    if not contract_type:
        return mark_safe('<span class="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">Aucun</span>')

    ct = contracts.get(contract_type.lower(), {"label": contract_type, "icon": "📑", "color": "bg-gray-100 text-gray-700"})
    html = f'<span class="text-xs px-2 py-0.5 rounded-full font-medium {ct["color"]}">{ct["icon"]} {ct["label"]}</span>'
    return mark_safe(html)