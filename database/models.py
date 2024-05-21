import sqlalchemy as sa

from sqlalchemy.orm import relationship

from database.engine import Base


class User(Base):
    __tablename__ = 'person'

    id = sa.Column(sa.Integer, primary_key=True)
    uuid = sa.Column(sa.String(20), nullable=False)
    gender = sa.Column(sa.String(20), nullable=False)
    interested = sa.Column(sa.String(20), nullable=False)
    age = sa.Column(sa.Integer, nullable=False)
    city = sa.Column(sa.String(30), nullable=False)
    username = sa.Column(sa.String(30), nullable=False)
    description = sa.Column(sa.Text)
    image = sa.Column(sa.String(255), nullable=False)
    state = sa.Column(sa.Boolean, default=False)
    user_rating_from = relationship(
        'UserRating',
        back_populates='user_from',
        cascade='all, delete-orphan',
        foreign_keys='UserRating.user_from_id',
    )
    user_rating_to = relationship(
        'UserRating',
        back_populates='user_to',
        cascade='all, delete-orphan',
        foreign_keys='UserRating.user_to_id',
    )
    report_from = relationship(
        'Report',
        back_populates='report_from',
        cascade='all, delete-orphan',
        foreign_keys='Report.report_from_id',
    )
    report_to = relationship(
        'Report',
        back_populates='report_to',
        cascade='all, delete-orphan',
        foreign_keys='Report.report_to_id',
    )


class UserRating(Base):
    __tablename__ = 'rating'

    id = sa.Column(sa.Integer, primary_key=True)
    user_from_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(User.id, ondelete='CASCADE'),
    )
    user_to_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(User.id, ondelete='CASCADE'),
    )
    user_from = relationship(
        'User',
        back_populates='user_rating_from',
        foreign_keys=[user_from_id],
    )
    user_to = relationship(
        'User',
        back_populates='user_rating_to',
        foreign_keys=[user_to_id],
    )


class Report(Base):
    __tablename__ = 'report'

    id = sa.Column(sa.Integer, primary_key=True)
    report_from_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(User.id, ondelete='CASCADE'),
    )
    report_to_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(User.id, ondelete='CASCADE'),
    )
    reason = sa.Column(sa.String(30), nullable=False)
    report_from = relationship(
        'User',
        back_populates='report_from',
        foreign_keys=[report_from_id],
    )
    report_to = relationship(
        'User',
        back_populates='report_to',
        foreign_keys=[report_to_id],
    )
