from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases

# Update this with your actual PostgreSQL credentials
POSTGRES_URL="postgresql+psycopg2://postgres.uhaeuuurtqzszopznvzm:nOCshsMrvT874syl@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
DATABASE_URL = POSTGRES_URL
# For async operations
database = databases.Database(DATABASE_URL)

# SQLAlchemy setup
Base = declarative_base()

class URL(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), unique=True, index=True)
    long_url = Column(String(2048))

# Engine to create tables
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
Base.metadata.create_all(bind=engine)

# Session maker (optional if you want to use ORM-style)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
