import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from config import settings

from jose import jwt
from datetime import datetime, timedelta

from models import User, Confirm
from schemas import UserCreate, UserResponse, Token, LoginRequest, UserBase, CodeRequest
from database import get_db

load_dotenv()

# JWT
SECRET_KEY = os.getenv('SECRET')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def send_email(to_email: str, body: str):
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = "Ваш код подтверждения"

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Установка TLS
            server.login(smtp_user, smtp_password)  # Вход в почтовый ящик
            server.send_message(msg)  # Отправка сообщения
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")


def generate_and_save_confirm_code(user_id: int, db: Session):
    code = random.randint(100000, 999999)

    new_confirm_code = Confirm(
        user_id=user_id,
        code=str(code)
    )

    db.add(new_confirm_code)

    return {"code": new_confirm_code.code}


@router.get("/", tags=["root"])
async def root():
    return {"message": "Главная страница"}


@router.post("/users", response_model=List[UserResponse])
def get_users(user: Optional[UserBase] = None, db: Session = Depends(get_db)):
    if user:
        users = db.query(User).filter(User.email == user.email).all()
    else:
        users = db.query(User).all()
    return users


@router.post("/confirm", response_model=dict)
def confirm(user: UserBase, db: Session = Depends(get_db)):
    users = get_users(user, db)
    if len(users) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email не найден"
        )

    return generate_and_save_confirm_code(users[0].id, db)


@router.post("/confirm_profile")
def confirm_profile(request: CodeRequest, db: Session = Depends(get_db)):
    with db.begin():
        db_confirm = db.query(Confirm).filter(
            Confirm.code == request.code,
            Confirm.user_id == request.user_id
        ).first()

        if not db_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код подтверждения"
            )

        db.delete(db_confirm)

        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        user.blocked = False
        db.add(user)

    return {
        "confirmed": True,
        "message": "Учетная запись подтверждена"
    }


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        with db.begin():
            db_user = db.query(User).filter(User.email == user.email).first()
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже зарегистрирован"
                )

            hashed_password = get_password_hash(user.password)

            new_user = User(
                email=user.email,
                password=hashed_password,  # Сохраняем хеш вместо пароля
                blocked=True
            )

            db.add(new_user)
            db.flush()

            send_code_response = generate_and_save_confirm_code(new_user.id, db)
            send_email(new_user.email, f'Код подтверждения: {send_code_response.get("code")}')

            return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password

    user = db.query(User).filter(User.email == email).first()

    # check user
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check block
    if user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учетная запись не подтверждена"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
