from django import template

register = template.Library()

@register.filter(name='tradui_erè')
def tradui_erè(error_msg):
    error_map = {
        "This field is required": "Champ sa obligatwa.",
        "Enter a valid email address": "Mete yon imel ki valab.",
        "Ensure this value has at least": "Valè sa a two kout.",
        "Ensure this value has at most": "Valè sa a two long.",
        "Enter a valid value": "Valè sa pa valab.",
        "Enter a valid URL": "URL sa pa valab.",
        "Enter a valid date": "Dat sa pa valab.",
        "Enter a valid time": "Lè sa pa valab.",
        "Enter a valid integer": "Antre yon chif ki pa gen desimal.",
        "Enter a number": "Antre yon chif.",
        "password": "Modpas ou pa bon.",
        "email": "Imel ou pa bon.",
        "username": "Non itilizatè pa valab.",
    }

    for key, msg in error_map.items():
        if key in error_msg:
            return msg

    return error_msg  # Retounen mesaj original si pa jwenn li
    
@register.simple_tag
def afficher_erè(form):
    if not form.errors:
        return ""

    html = '<div class="bg-red-600 text-white rounded p-3 text-sm mb-4">'
    html += '<p class="font-semibold mb-2">Gen kèk erè :</p>'
    html += '<ul class="list-disc list-inside">'

    error_map = {
        "This field is required": "Champ sa obligatwa.",
        "Enter a valid email address": "Mete yon imel ki valab.",
        "Ensure this value has at least": "Valè sa a two kout.",
        "Ensure this value has at most": "Valè sa a two long.",
        "Enter a valid value": "Valè sa pa valab.",
        "Enter a valid URL": "URL sa pa valab.",
        "Enter a valid date": "Dat sa pa valab.",
        "Enter a valid time": "Lè sa pa valab.",
        "Enter a valid integer": "Antre yon chif ki pa gen desimal.",
        "Enter a number": "Antre yon chif.",
        "password": "Modpas ou pa bon.",
        "email": "Imel ou pa bon.",
        "username": "Non itilizatè pa valab.",
    }

    for field, errors in form.errors.items():
        for err in errors:
            tradui = next((v for k, v in error_map.items() if k in err), err)
            html += f"<li>{tradui}</li>"

    html += "</ul></div>"
    return html