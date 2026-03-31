from sqlalchemy import (
    create_engine, Column, String,
    Integer, DateTime, Text, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()

class AuthorizationRecord(Base):
    """Stores every authorization analysis run."""
    __tablename__ = "authorization_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    procedure = Column(String(500), nullable=False)
    approval_likelihood = Column(Integer, nullable=True)
    approval_likelihood_after = Column(Integer, nullable=True)
    policy_analysis = Column(Text, nullable=True)
    clinical_analysis = Column(Text, nullable=True)
    gap_analysis = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine(
            config.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info("Database initialized")

    def save_authorization(self, result: dict) -> int:
        """Save authorization analysis result to database."""
        session = self.SessionLocal()
        try:
            record = AuthorizationRecord(
                procedure=result.get("procedure", ""),
                approval_likelihood=result.get("approval_likelihood"),
                approval_likelihood_after=result.get(
                    "approval_likelihood_after"
                ),
                policy_analysis=result.get("policy_analysis"),
                clinical_analysis=result.get("clinical_analysis"),
                gap_analysis=result.get("gap_analysis"),
                recommendations=result.get("recommendations"),
                status=result.get("status", "completed")
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            logger.info(f"Saved authorization record ID: {record.id}")
            return record.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save record: {e}")
            raise
        finally:
            session.close()

    def get_recent_records(self, limit: int = 10) -> list:
        """Get recent authorization records."""
        session = self.SessionLocal()
        try:
            records = session.query(AuthorizationRecord)\
                .order_by(AuthorizationRecord.created_at.desc())\
                .limit(limit)\
                .all()
            return [
                {
                    "id": r.id,
                    "procedure": r.procedure,
                    "approval_likelihood": r.approval_likelihood,
                    "approval_likelihood_after": r.approval_likelihood_after,
                    "status": r.status,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ]
        finally:
            session.close()

db = Database()