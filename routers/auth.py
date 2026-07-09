from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UserCreate, UserLogin, UserResponse, Token
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_refresh_token
)
import crud

router = APIRouter(prefix="/auth", tags=["认证"])


# ========== 1. 用户注册 ==========
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册接口

    - 检查用户名是否已存在
    - 密码加密后存入数据库
    - 返回用户信息（不含密码）
    """
    # 检查用户名是否已存在
    existing_user = await crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 密码加密
    hashed_password = hash_password(user.password)

    # 创建用户
    new_user = await crud.create_user(db, user.username, hashed_password)

    return new_user


# ========== 2. 用户登录 ==========
@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录接口

    - 验证用户名和密码
    - 返回 access token (30分钟) 和 refresh token (7天)
    """
    # 查询用户
    db_user = await crud.get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # 验证密码
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # 生成双 token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ========== 3. 刷新 Access Token ==========
@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    """
    刷新 access token 接口

    - 客户端发送 refresh token
    - 验证通过后返回新的 access token 和 refresh token
    - 无需重新输入密码
    """
    # 验证 refresh token 并提取 user_id
    user_id = verify_refresh_token(refresh_token)

    # 检查用户是否存在
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # 生成新的双 token
    new_access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user_id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# ========== 4. 获取当前用户信息（测试用）==========
@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """
    获取当前登录用户信息

    - 需要在请求头带上 Authorization: Bearer <access_token>
    - 返回当前用户信息
    """
    return current_user
