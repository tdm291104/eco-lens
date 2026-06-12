"""
SQLAlchemy ORM models.

- UserImpact: tổng hợp tác động môi trường + gamification theo user_id
  (total_co2_kg, total_points, scan_count, streak, last_scan_date).
  Được cập nhật bởi skill award_green_points và đọc bởi get_user_impact.
"""

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class UserImpact(Base):
    """Tác động môi trường + điểm xanh tích lũy của một user."""

    __tablename__ = "user_impacts"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    total_co2_kg: Mapped[float] = mapped_column(Float, default=0.0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    scan_count: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_scan_date: Mapped[str | None] = mapped_column(String, nullable=True)
