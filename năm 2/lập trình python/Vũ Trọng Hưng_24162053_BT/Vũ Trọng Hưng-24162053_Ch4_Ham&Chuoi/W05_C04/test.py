# pip install sqlalchemy
from __future__ import annotations

from datetime import date
from typing import Optional, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# =========================
# Base
# =========================
class Base(DeclarativeBase):
    pass


# =========================
# Entities
# =========================
class ExamYear(Base):
    """
    Năm dự thi (giả sử mỗi năm chỉ tổ chức 1 kỳ thi)
    """
    __tablename__ = "exam_year"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)  # NAMDUTHI

    candidates: Mapped[list["Candidate"]] = relationship(back_populates="exam_year")
    cutoffs: Mapped[list["CutoffScore"]] = relationship(back_populates="exam_year")


class Major(Base):
    """
    Ngành dự thi
    """
    __tablename__ = "major"

    ma_nganh: Mapped[str] = mapped_column(String(20), primary_key=True)  # MANGANH
    ten_nganh: Mapped[str] = mapped_column(String(200), nullable=False)  # TENNGANH

    candidates: Mapped[list["Candidate"]] = relationship(back_populates="major")
    major_subjects: Mapped[list["MajorSubject"]] = relationship(back_populates="major")
    cutoffs: Mapped[list["CutoffScore"]] = relationship(back_populates="major")


class Subject(Base):
    """
    Môn thi
    tinh_chat: 1 nếu là môn ngoại ngữ, 0 nếu không
    """
    __tablename__ = "subject"

    ma_mt: Mapped[str] = mapped_column(String(20), primary_key=True)  # MAMT
    ten_mt: Mapped[str] = mapped_column(String(200), nullable=False)  # TENMT
    tinh_chat: Mapped[int] = mapped_column(Integer, nullable=False)   # TINHCHAT (0/1)

    __table_args__ = (
        CheckConstraint("tinh_chat IN (0, 1)", name="ck_subject_tinh_chat_01"),
    )

    major_subjects: Mapped[list["MajorSubject"]] = relationship(back_populates="subject")
    scores: Mapped[list["Score"]] = relationship(back_populates="subject")


class Candidate(Base):
    """
    Thí sinh
    """
    __tablename__ = "candidate"

    sobd: Mapped[str] = mapped_column(String(30), primary_key=True)     # SOBD
    ho_ten: Mapped[str] = mapped_column(String(200), nullable=False)    # HOTEN
    ngay_sinh: Mapped[date] = mapped_column(Date, nullable=False)      # NGAYSINH
    noi_sinh: Mapped[str] = mapped_column(String(200), nullable=False)  # NOISINH

    ma_nganh: Mapped[str] = mapped_column(ForeignKey("major.ma_nganh"), nullable=False)
    nam_du_thi: Mapped[int] = mapped_column(ForeignKey("exam_year.year"), nullable=False)

    major: Mapped["Major"] = relationship(back_populates="candidates")
    exam_year: Mapped["ExamYear"] = relationship(back_populates="candidates")
    scores: Mapped[list["Score"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")


# =========================
# Relationships (Associations)
# =========================
LoaiMon = Literal["COBAN", "COSONGANH", "NGOAINGU"]

class MajorSubject(Base):
    """
    Danh sách môn áp dụng cho từng ngành, kèm loại môn:
    - COBAN
    - COSONGANH
    - NGOAINGU
    """
    __tablename__ = "major_subject"

    ma_nganh: Mapped[str] = mapped_column(ForeignKey("major.ma_nganh"), primary_key=True)
    ma_mt: Mapped[str] = mapped_column(ForeignKey("subject.ma_mt"), primary_key=True)

    loai_mon: Mapped[str] = mapped_column(String(20), nullable=False)  # loại môn theo ngành

    __table_args__ = (
        CheckConstraint(
            "loai_mon IN ('COBAN','COSONGANH','NGOAINGU')",
            name="ck_major_subject_loai_mon",
        ),
    )

    major: Mapped["Major"] = relationship(back_populates="major_subjects")
    subject: Mapped["Subject"] = relationship(back_populates="major_subjects")


class CutoffScore(Base):
    """
    Điểm tuyển theo ngành trong từng năm
    """
    __tablename__ = "cutoff_score"

    ma_nganh: Mapped[str] = mapped_column(ForeignKey("major.ma_nganh"), primary_key=True)
    year: Mapped[int] = mapped_column(ForeignKey("exam_year.year"), primary_key=True)

    diem_tuyen: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    major: Mapped["Major"] = relationship(back_populates="cutoffs")
    exam_year: Mapped["ExamYear"] = relationship(back_populates="cutoffs")


class Score(Base):
    """
    Điểm thi của thí sinh theo môn.
    Nếu vắng thi => diem_thi = 0 và ghi chú "Vắng thi ..."
    """
    __tablename__ = "score"

    sobd: Mapped[str] = mapped_column(ForeignKey("candidate.sobd"), primary_key=True)
    ma_mt: Mapped[str] = mapped_column(ForeignKey("subject.ma_mt"), primary_key=True)

    diem_thi: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0)
    vang_thi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ghi_chu: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        # Nếu vắng thi thì điểm phải = 0
        CheckConstraint(
            "(vang_thi = 0) OR (diem_thi = 0)",
            name="ck_score_vangthi_diem0",
        ),
    )

    candidate: Mapped["Candidate"] = relationship(back_populates="scores")
    subject: Mapped["Subject"] = relationship(back_populates="scores")


# =========================
# Create DB + example usage
# =========================
def main() -> None:
    engine = create_engine("sqlite:///tuyensinh.db", echo=False)
    Base.metadata.create_all(engine)

    # Ví dụ nhỏ: tạo dữ liệu mẫu
    with Session(engine) as session:
        # Năm
        session.merge(ExamYear(year=2026))

        # Ngành
        session.merge(Major(ma_nganh="KHM", ten_nganh="Khoa học máy tính"))
        session.merge(Major(ma_nganh="HTT", ten_nganh="Hệ thống thông tin"))
        session.merge(Major(ma_nganh="KTM", ten_nganh="Kỹ thuật mạng máy tính"))

        # Môn
        session.merge(Subject(ma_mt="TH01", ten_mt="Cơ sở dữ liệu", tinh_chat=0))
        session.merge(Subject(ma_mt="CB01", ten_mt="Toán cơ bản", tinh_chat=0))
        session.merge(Subject(ma_mt="NN01", ten_mt="Tiếng Anh", tinh_chat=1))

        # Môn áp dụng cho ngành (ví dụ TH01 là cơ sở ngành cho 3 ngành)
        session.merge(MajorSubject(ma_nganh="KHM", ma_mt="TH01", loai_mon="COSONGANH"))
        session.merge(MajorSubject(ma_nganh="HTT", ma_mt="TH01", loai_mon="COSONGANH"))
        session.merge(MajorSubject(ma_nganh="KTM", ma_mt="TH01", loai_mon="COSONGANH"))

        # Điểm tuyển
        session.merge(CutoffScore(ma_nganh="KHM", year=2026, diem_tuyen=12.00))

        # Thí sinh
        ts = Candidate(
            sobd="A001",
            ho_ten="Nguyen Van A",
            ngay_sinh=date(2000, 1, 1),
            noi_sinh="TP.HCM",
            ma_nganh="KHM",
            nam_du_thi=2026,
        )
        session.merge(ts)

        # Điểm (3 môn)
        session.merge(Score(sobd="A001", ma_mt="CB01", diem_thi=6.50, vang_thi=False))
        session.merge(Score(sobd="A001", ma_mt="TH01", diem_thi=6.00, vang_thi=False))
        # vắng thi ngoại ngữ -> điểm = 0, ghi chú
        session.merge(Score(sobd="A001", ma_mt="NN01", diem_thi=0, vang_thi=True, ghi_chu="Vắng thi môn NN01"))

        session.commit()

    print("OK: created sqlite db at tuyensinh.db")


if __name__ == "__main__":
    main()
