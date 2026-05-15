from aiogram import Router

from .menu import router as menu_router
from .start import router as start_router
from .finish import router as finish_router

router = Router()

router.include_router(menu_router)
router.include_router(start_router)
router.include_router(finish_router)