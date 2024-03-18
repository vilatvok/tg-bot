from sqlalchemy import delete, insert, select, update, func, union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.models import User, UserRating, Report


### Get data
async def get_all_users(session: AsyncSession):
    users = await session.execute(select(User))
    return users.scalars().all()


async def get_users(session: AsyncSession, uuid):
    user, _ = await get_user(session, uuid)
    users = await session.execute(
        select(User, func.count(UserRating.id)).
        select_from(UserRating).
        outerjoin(User.user_rating_to).
        where(
            (User.uuid != uuid) & 
            (User.gender == user.interested) & 
            (User.state == True)
        ).group_by(User).order_by(func.random())
    )
    return users.first()


async def get_user(session: AsyncSession, uuid):
    user = await session.execute(
        select(User, func.count(UserRating.id)).
        select_from(UserRating).
        outerjoin(User.user_rating_to).
        where(User.uuid == uuid).
        group_by(User)
    )
    return user.first()


async def get_popular_users(session: AsyncSession, uuid):
    try:
        user, _ = await get_user(session, uuid)
    except TypeError:
        user = None
    
    if user:
        users = await session.execute(
            select(User, func.count(UserRating.id)).
            select_from(UserRating).
            outerjoin(User.user_rating_to).
            where(
                (User.uuid != uuid) & 
                (User.gender == user.interested) & 
                (User.state == True)
            ).group_by(User).order_by(func.count(UserRating.id).desc())
        )
        return users.fetchall()


async def get_reports(session: AsyncSession):
    user1 = aliased(User)
    user2 = aliased(User)
    reports = await session.execute(
        select(user1.username, user2.username, user2.uuid, Report.reason).
        join(user1, user1.id == Report.report_from_id).
        join(user2, user2.id == Report.report_to_id))
    return reports.fetchall()


async def get_rating(
    session: AsyncSession, 
    user_from_uuid, 
    user_to_uuid
):
    user_from = (await session.execute(
        select(User).where(User.uuid == user_from_uuid)
    )).scalar()

    user_to = (await session.execute(
        select(User).where(User.uuid == user_to_uuid)
    )).scalar()

    rating_exist = await session.execute(
        select(UserRating).where(
            (UserRating.user_from_id == user_from.id) & 
            (UserRating.user_to_id == user_to.id)
        )
    )
    return rating_exist.scalar()


async def get_statistics(session: AsyncSession):
    all_users = await session.execute(
        select(func.count()).select_from(User)
    )
    active_users = await session.execute(
        select(func.count()).select_from(User).where(User.state == True)
    )
    gender = await session.execute(
        select(User.gender, func.count()).select_from(User).group_by(User.gender)
    )
    return {
        'all_users': all_users.scalar(), 
        'active_users': active_users.scalar(), 
        'gender': gender.fetchall()
    }


### Edit data
async def add_user(session: AsyncSession, uuid, data):
    data = await session.execute(
        insert(User).values(uuid=uuid, **data).returning(User)
    )
    await session.commit()
    return data.scalar()


async def update_user(session: AsyncSession, uuid, data):
    data = await session.execute(
        update(User).where(User.uuid == uuid).values(**data).returning(User)
    )
    await session.commit()
    return data.scalar()


async def delete_user(session: AsyncSession, uuid):
    await session.execute(
        delete(User).where(User.uuid == uuid)
    )
    await session.commit()


async def set_rating(
    session: AsyncSession, 
    user_from_uuid, 
    user_to_uuid
):
    user1 = (await session.execute(
        select(User).where(User.uuid == user_from_uuid)
    )).scalar()

    user2 = (await session.execute(
        select(User).where(User.uuid == user_to_uuid)
    )).scalar()

    await session.execute(
        insert(UserRating).values(user_from_id=user1.id, user_to_id=user2.id)
    )
    await session.commit()


async def send_report(    
    session: AsyncSession, 
    user_from_uuid, 
    user_to_uuid,
    reason
):
    report_from = (await session.execute(
        select(User).where(User.uuid == user_from_uuid)
    )).scalar()

    report_to = (await session.execute(
        select(User).where(User.uuid == user_to_uuid)
    )).scalar()

    await session.execute(
        insert(Report).values(
            report_from_id=report_from.id, 
            report_to_id=report_to.id,
            reason=reason
        )
    )
    await session.commit()
