# users/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def verified_required(view_func):
    """
    Vérifie si l'utilisateur est connecté ET que son compte est vérifié (is_verified=True ou session OTP active).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        # 🔒 Si non connecté
        if not user.is_authenticated:
            return redirect("login")

        # ✅ Si déjà vérifié en base
        if getattr(user, "is_verified", False):
            return view_func(request, *args, **kwargs)

        # ✅ Ou si l'utilisateur a validé l'OTP dans la session
        if request.session.get("otp_verified", False):
            return view_func(request, *args, **kwargs)

        # 🚫 Sinon, redirige vers la vérification OTP
        messages.warning(request, "Tanpri verifye kont ou ak kòd OTP anvan ou kontinye.")
        return redirect("otp:verify_otp")

    return _wrapped_view