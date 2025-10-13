from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP

# Base class for all ORM models
Base = declarative_base()

# Table for storing parsed quotes
class RawQuotes(Base):
    __tablename__ = "quotes"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    url = Column(Text, nullable=False)                          # Quote page URL
    parsed_at = Column(TIMESTAMP, nullable=False)               # Parsing timestamp
    text = Column(Text)                                         # Quote text
    author = Column(Text)                                       # Author name
    tags = Column(JSON)                                         # Tags (JSON array)
    author_url = Column(Text)                                   # Link to author details

# Table for storing author details
class RawAuthors(Base):
    __tablename__ = "raw_authors"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    author_url = Column(Text, unique=True, nullable=False)      # Unique author URL
    name = Column(Text)                                         # Author name
    born_date = Column(Text)                                    # Date of birth
    born_location = Column(Text)                                # Place of birth
    description = Column(Text)                                  # Short author bio