from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import user, image

    Base.metadata.create_all(bind=engine)

    # Optional: Create default admin user if explicitly enabled via environment variables
    # This is disabled by default for security reasons
    if settings.CREATE_DEFAULT_ADMIN and settings.DEFAULT_ADMIN_USERNAME and settings.DEFAULT_ADMIN_PASSWORD:
        from app.core.security import get_password_hash

        db = SessionLocal()
        try:
            admin_user = db.query(user.User).filter(user.User.username == settings.DEFAULT_ADMIN_USERNAME).first()
            if not admin_user:
                default_admin = user.User(
                    username=settings.DEFAULT_ADMIN_USERNAME,
                    email=settings.DEFAULT_ADMIN_EMAIL or "admin@example.com",
                    hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                    is_active=True
                )
                db.add(default_admin)
                db.commit()
                print(f"Default admin user created: {settings.DEFAULT_ADMIN_USERNAME}")
        finally:
            db.close()
