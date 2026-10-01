"""Authentication routes."""

from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])
