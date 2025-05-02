from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

DB_USER = settings.POSTGRES_USER
DB_PASS = settings.POSTGRES_PASSWORD
DB_NAME = settings.POSTGRES_DB
DB_HOST = settings.POSTGRES_HOST
DB_PORT = settings.POSTGRES_PORT

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        'client_encoding': 'utf8',
        'options': '-c client_encoding=utf8'
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# with engine.connect() as connection:
#     print(connection.execute(text(f"select * from users where email = 'admin@mail.ru'")).fetchone())

# def test_db_connection():
#     try:
#         with engine.connect() as connection:
#             print("\nTesting database connection...")
#
#             # Выполняем простой запрос для проверки версии PostgreSQL
#             version_query = text("SELECT version()")
#             version_result = connection.execute(version_query)
#             print("PostgreSQL version:", version_result.scalar())
#
#             # Пытаемся получить данные из таблицы users
#             users_query = text("SELECT * FROM users")
#             users_result = connection.execute(users_query)
#
#             print("\nUsers in database:")
#             for row in users_result:
#                 print(row)
#
#             return True
#     except Exception as e:
#         print("\nDatabase connection error:", str(e))
#         return False
#
#
# # Проверяем подключение при запуске файла
# if __name__ == "__main__":
#     if test_db_connection():
#         print("\nDatabase connection successful!")
#     else:
#         print("\nDatabase connection failed!")
