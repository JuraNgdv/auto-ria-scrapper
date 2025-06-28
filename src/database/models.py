from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime, UTC

from src.utils.helpers import safe_str


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, index=True, unique=True)
    title: Mapped[str] = mapped_column(String)
    price_usd: Mapped[int] = mapped_column(Integer)
    odometer: Mapped[int] = mapped_column(BIGINT, nullable=True)
    username: Mapped[str] = mapped_column(String)
    phone_number: Mapped[int] = mapped_column(BIGINT, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    images_count: Mapped[int] = mapped_column(Integer)
    car_number: Mapped[str] = mapped_column(String, nullable=True)
    car_vin: Mapped[str] = mapped_column(String, nullable=True)
    datetime_found: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __str__(self):
        return f"Car {self.url} {self.car_vin}"


    def as_table_row(self) -> str:
        return "{:<100} {:<35} {:<10} {:>10} {:<30} {:^16} {:^15} {:^25}".format(
            safe_str(self.url),
            safe_str(self.title, length=34),
            safe_str("$", self.price_usd, length=9),
            safe_str(self.odometer, "km", length=9),
            safe_str(self.username, length=29),
            safe_str("+", self.phone_number, length=15),
            safe_str(self.car_number, length=14),
            safe_str(self.car_vin, length=24),
        )
