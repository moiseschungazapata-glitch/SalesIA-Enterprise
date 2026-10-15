"""Regression checks for browser cross-origin requests."""

from fastapi.middleware.cors import CORSMiddleware

from app.main import app


def test_seller_profile_update_allows_put_preflight() -> None:
    cors = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls is CORSMiddleware
    )

    assert "PUT" in cors.kwargs["allow_methods"]
