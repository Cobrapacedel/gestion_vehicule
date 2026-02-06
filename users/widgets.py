from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

class CustomClearableFileInput(ClearableFileInput):
    """Widget personnalisé pour un champ de fichier avec un libellé plus clair"""
    template_name = "widgets/custom_clearable_file_input.html"

    initial_text = _("Fichier actuel")
    input_text = _("Changer")
    clear_checkbox_label = _("Supprimer")