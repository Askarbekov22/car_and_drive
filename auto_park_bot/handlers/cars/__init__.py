from aiogram import Router

from .menu import router as menu_router
from .create import router as create_router
from .list import router as list_router
from .edit import router as edit_router

router = Router()

router.include_router(menu_router)
router.include_router(create_router)
router.include_router(list_router)
router.include_router(edit_router)