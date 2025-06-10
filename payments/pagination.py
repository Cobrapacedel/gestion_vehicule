# payments/pagination.py

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Permet de modifier la taille de la page via un paramètre de requête
    max_page_size = 100  # Limite maximale du nombre d'éléments par page