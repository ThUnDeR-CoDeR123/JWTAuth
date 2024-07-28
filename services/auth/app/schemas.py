from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Schemas for Entitlement
class EntitlementBase(BaseModel):
    label: str
    description: Optional[str] = None

class EntitlementCreate(EntitlementBase):
    pass

class EntitlementUpdate(EntitlementBase):
    pass

class Entitlement(EntitlementBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Schemas for User
class UserBase(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    referral_code: Optional[str] = None
    is_verified: Optional[bool] = None
    last_login: Optional[datetime] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    entitlements: List[Entitlement] = []
    wallets: List["Wallet"] = []

    class Config:
        orm_mode = True

# Schemas for Wallet
class WalletBase(BaseModel):
    ammy: float
    meta: Optional[str] = None

class WalletCreate(WalletBase):
    pass

class WalletUpdate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None