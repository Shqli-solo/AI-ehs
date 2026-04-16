# apps/ehs-ai/src/adapters/primary/auth.py
"""JWT 认证中间件 - Primary Adapter"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import settings


# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", settings.APP_NAME + "_default_secret_change_in_prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


class JWTBearer(HTTPBearer):
    """
    JWT Bearer 认证

    使用方式：
    @app.get("/protected")
    async def protected_route(request: Request, credentials: JWTBearer = Depends()):
        payload = credentials
        user_id = payload.get("sub")
    """

    def __init__(self, auto_error: bool = True, required: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.required = required

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if not credentials:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未提供认证信息",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return None

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证方案错误，请使用 Bearer Token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        payload = await self._verify_jwt(credentials.credentials)
        if payload is None and self.required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 无效或已过期",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return payload

    async def _verify_jwt(self, token: str) -> Optional[dict]:
        """验证 JWT Token"""
        try:
            # 解码 token
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )

            # 检查过期时间
            expires_at = payload.get("exp")
            if expires_at and datetime.fromtimestamp(expires_at) < datetime.utcnow():
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None


def create_jwt_token(
    subject: str,
    extra_data: Optional[dict] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT Token

    Args:
        subject: Token 主体（通常是用户 ID）
        extra_data: 额外数据
        expires_delta: 过期时间增量

    Returns:
        JWT Token 字符串
    """
    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }

    if extra_data:
        to_encode.update(extra_data)

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# 可选认证装饰器
def optional_auth(func):
    """
    可选认证装饰器

    用于允许匿名访问但提供认证信息的端点
    """
    from functools import wraps
    from fastapi import Depends

    @wraps(func)
    async def wrapper(request: Request, credentials: JWTBearer = Depends(JWTBearer(auto_error=False))):
        return await func(request, credentials)

    return wrapper
