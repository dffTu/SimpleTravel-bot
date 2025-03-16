from .search import search_router
from .post import post_router
from .start import start_router
from .account import account_router

# Экспортируем все роутеры
__all__ = [
    'search_router',
    'post_router',
    'start_router',
    'account_router'
]
