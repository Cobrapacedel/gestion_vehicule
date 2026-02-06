from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter(is_safe=True)
def document_type_badge(document_type):
    """
    Retourne un badge coloré avec icône selon le type de document.
    """

    document_types = {
        "insurance": {
            "label": _("Asirans"),
            "icon": "🛡️",
            "color": "bg-green-100 text-green-800",
        },
        "registration": {
            "label": _("Kat Griz"),
            "icon": "📄",
            "color": "bg-blue-100 text-blue-800",
        },
        "inspection": {
            "label": _("Kontwòl Teknik"),
            "icon": "🔧",
            "color": "bg-yellow-100 text-yellow-800",
        },
        "license": {
            "label": _("Lisand"),
            "icon": "🪪",
            "color": "bg-purple-100 text-purple-800",
        },
        "other": {
            "label": _("Lòt"),
            "icon": "📁",
            "color": "bg-gray-100 text-gray-700",
        },
    }

    default_badge = {
        "label": _("N/A"),
        "icon": "📎",
        "color": "bg-gray-100 text-gray-700",
    }

    if not document_type:
        dt = default_badge
    else:
        dt = document_types.get(
            document_type.lower(),
            {
                "label": escape(document_type),
                "icon": default_badge["icon"],
                "color": default_badge["color"],
            },
        )

    html = (
        f'<span class="inline-flex items-center gap-1 '
        f'text-xs px-2 py-0.5 rounded-full font-medium {dt["color"]}">'
        f'{dt["icon"]} {dt["label"]}</span>'
    )

    return mark_safe(html)