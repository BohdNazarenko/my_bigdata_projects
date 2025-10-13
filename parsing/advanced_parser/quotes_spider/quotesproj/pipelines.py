from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from itemadapter import ItemAdapter

from .dbconfig import get_connection_string
from .models import Base, RawQuotes, RawAuthors


class DatabasePipeline:
    def __init__(self):
        # Initialize database engine and session
        self.engine = create_engine(
            get_connection_string(),
            pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600,  # connection pool settings
        )
        Base.metadata.create_all(self.engine)  # create tables if not exist
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    @contextmanager
    def session_scope(self):
        # Context manager for session handling (commit/rollback)
        s = self.Session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def process_item(self, item, spider):
        # Convert Scrapy item to dict-like adapter
        ad = ItemAdapter(item)

        # Convert parsed_at to datetime if it is a string
        parsed_at = ad.get("parsed_at")
        if isinstance(parsed_at, str):
            parsed_at = datetime.fromisoformat(parsed_at)

        # Open DB session and insert data
        with self.session_scope() as s:
            # Insert main quote record
            s.add(RawQuotes(
                url=ad.get("url"),
                parsed_at=parsed_at,
                text=ad.get("text"),
                author=ad.get("author"),
                tags=ad.get("tags"),
                author_url=ad.get("author_url"),
            ))

            # Insert or update author details if available
            if ad.get("author_url") and any(ad.get(k) for k in
                                            ["author_born_date", "author_born_location", "author_description"]):
                stmt = insert(RawAuthors).values(
                    author_url=ad.get("author_url"),
                    name=ad.get("author"),
                    born_date=ad.get("author_born_date"),
                    born_location=ad.get("author_born_location"),
                    description=ad.get("author_description"),
                )
                # Upsert (insert or update) logic on conflict by author_url
                stmt = stmt.on_conflict_do_update(
                    index_elements=[RawAuthors.author_url],
                    set_={
                        "name": stmt.excluded.name,
                        "born_date": stmt.excluded.born_date,
                        "born_location": stmt.excluded.born_location,
                        "description": stmt.excluded.description,
                    }
                )
                s.execute(stmt)

        return item

    def close_spider(self, spider):
        # Close DB connections when spider finishes
        self.engine.dispose()