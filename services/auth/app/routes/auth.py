from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserUpdate, User,TokenData,Token
from app.database import get_db
from app.crud import CreateUser, DeleteUser,UdateUser,GetUserById,GetUserByEmail
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta,datetime,timezone
from typing import Annotated, Union
from jwt.exceptions import InvalidTokenError

import app.models
from app.config import settings
import jwt

# this function maps data from user model defined in models.py to the user schema defined in schema.py

def user_model_to_schema(user):
    UserSchema=User(id=user.id, 
                full_name=user.full_name, 
                email=user.email, 
                password=user.password,
                referral_code=user.referral_code,
                is_verified=user.is_verified,
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at,
                entitlements=user.entitlements)
    return UserSchema



router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")






#_____________________________________authorization functions________________________________________________________________


def authenticate_user(email: str, password: str, db: Session):
    user=GetUserByEmail(email,db)
    if not user:
        return False
    if password != user.password:
        return False
    return user_model_to_schema(user)



def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db : Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(1)
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        print(1)
        username: str = payload.get("sub")
        print(1)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = GetUserByEmail(email=token_data.username,db=db)
    if user is None:
        raise credentials_exception
    return user



#______________________________________Authorization Routes________________________________________________________________


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: Annotated[Session, Depends(get_db)]
) -> Token:
    
    user = authenticate_user(form_data.username, form_data.password, db=db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")



@router.post("/users/", response_model=User)
async def create_user(user: Annotated[app.models.User, Depends(CreateUser)]):
    return user_model_to_schema(user)


@router.get("/auth", response_model=User)
def read_user(user: Annotated[app.models.User, Depends(get_current_user)]):
    return user_model_to_schema(user)


@router.put("/users/{user_id}", response_model=User)
def update_user(user1: Annotated[app.models.User, Depends(get_current_user)],user2: Annotated[app.models.User, Depends(UdateUser)]):
    return user_model_to_schema(user2)


@router.get("/users/{user_id}", response_model=User)
def get_user(user: Annotated[app.models.User, Depends(GetUserById)]):
    return user_model_to_schema(user)


