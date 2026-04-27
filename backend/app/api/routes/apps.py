import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from ..core.database import get_db
from ..models.app import App
from ..core.security import get_current_user, get_api_key
from ...shared.schemas.user_schema import UserOut

router = APIRouter(prefix="/apps", tags=["apps"])


def generate_api_credentials():
    api_key = secrets.token_urlsafe(32)
    secret_key = secrets.token_urlsafe(32)
    return api_key, secret_key


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_app(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key, secret_key = generate_api_credentials()
    
    app = App(
        name=name,
        api_key=api_key,
        secret_key=secret_key,
        user_id=str(current_user.id) if hasattr(current_user, 'id') else None
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {
        "id": str(app.id),
        "name": app.name,
        "api_key": app.api_key,
        "secret_key": app.secret_key
    }


@router.get("/{app_id}")
def get_app(
    app_id: str,
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    if str(app.id) != app_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return {
        "id": str(app.id),
        "name": app.name,
        "api_key": app.api_key,
        "is_active": app.is_active
    }


@router.get("/")
def list_apps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apps = db.query(App).all()
    return [
        {
            "id": str(app.id),
            "name": app.name,
            "is_active": app.is_active
        }
        for app in apps
    ]