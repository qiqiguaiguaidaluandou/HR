from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserCreateAdmin, PasswordChange, Token
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    oauth2_scheme,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# 管理员权限依赖
def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )

    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/password")
def change_password(
    password_data: PasswordChange,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 验证旧密码
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # 更新密码
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# ============ 管理员 API ============

@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).all()
    return users


@router.post("/admin/users", response_model=UserResponse)
def create_user_by_admin(
    user_data: UserCreateAdmin,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """创建新用户（仅管理员）"""
    # Check if user exists
    db_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """删除用户（仅管理员）"""
    # 不能删除自己
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
