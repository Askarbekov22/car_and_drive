from aiogram import Router

from .menu import router as menu_router
from .create import router as create_router
from .search import router as search_router
from .history import router as history_router
from .rating import router as rating_router
from .edit import router as edit_router

router = Router()

router.include_router(menu_router)
router.include_router(create_router)
router.include_router(search_router)
router.include_router(history_router)
router.include_router(rating_router)
router.include_router(edit_router)