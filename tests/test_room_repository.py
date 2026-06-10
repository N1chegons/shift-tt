import pytest
import pytest_asyncio
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from src.room.models import Room, Slot, Booking
from src.user.models import User
from src.room.repository import RoomRepository, SlotRepository, BookingRepository
from src.database import Base
import src.database

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    test_engine = create_async_engine(TEST_DB_URL)

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    original_engine = src.database.async_engine
    original_session = src.database.async_session

    src.database.async_engine = test_engine
    src.database.async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    import importlib
    importlib.reload(src.room.repository)

    async with src.database.async_session() as session:
        yield session

    src.database.async_engine = original_engine
    src.database.async_session = original_session
    importlib.reload(src.room.repository)

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_get_rooms(db_session: AsyncSession):
    room1 = Room(name="Переговорная А")
    room2 = Room(name="Переговорная Б")
    db_session.add_all([room1, room2])
    await db_session.flush()

    slot1 = Slot(room_id=room1.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room1.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.commit()

    rooms = await RoomRepository.get_rooms()

    assert len(rooms) == 2
    assert rooms[0].name == "Переговорная А"
    assert len(rooms[0].slots_room) == 2


@pytest.mark.asyncio
async def test_is_slot(db_session: AsyncSession):
    room = Room(name="Тестовая")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.commit()

    found = await SlotRepository.is_slot(slot.id)
    assert found is not None
    assert found.id == slot.id

    not_found = await SlotRepository.is_slot(99999)
    assert not_found is None


@pytest.mark.asyncio
async def test_get_slots(db_session: AsyncSession):
    room = Room(name="Тестовая")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.commit()

    slots = await SlotRepository.get_slots()
    assert len(slots) == 2


@pytest.mark.asyncio
async def test_is_bookings(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Тестовая")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.flush()

    booking1 = Booking(slot_id=slot1.id, user_id=user.id, date=datetime.date.today())
    booking2 = Booking(slot_id=slot2.id, user_id=user.id, date=datetime.date.today())
    db_session.add_all([booking1, booking2])
    await db_session.commit()

    bookings = await BookingRepository.is_bookings()
    assert len(bookings) == 2


@pytest.mark.asyncio
async def test_slot_is_free(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Тестовая")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.flush()

    date_today = datetime.date.today()
    date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    booking = Booking(slot_id=slot.id, user_id=user.id, date=date_today)
    db_session.add(booking)
    await db_session.commit()

    booked = await BookingRepository.slot_is_free(slot.id, date_today)
    assert booked is not None

    free = await BookingRepository.slot_is_free(slot.id, date_tomorrow)
    assert free is None


@pytest.mark.asyncio
async def test_get_bookings(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Переговорная")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    slot3 = Slot(room_id=room.id, start_time="14:00", end_time="16:00")
    db_session.add_all([slot1, slot2, slot3])
    await db_session.flush()

    date = datetime.date.today()

    booking = Booking(slot_id=slot2.id, user_id=user.id, date=date)
    db_session.add(booking)
    await db_session.commit()

    free_slots = await BookingRepository.get_bookings(room.id, date)

    assert len(free_slots) == 2
    assert free_slots[0].id == slot1.id
    assert free_slots[1].id == slot3.id


@pytest.mark.asyncio
async def test_get_bookings_by_user_id(db_session: AsyncSession):
    user1 = User(
        username="user1",
        surname="Иванов",
        email="user1@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    user2 = User(
        username="user2",
        surname="Петров",
        email="user2@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    room = Room(name="Конференц-зал")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.flush()

    date = datetime.date.today()

    booking1 = Booking(slot_id=slot1.id, user_id=user1.id, date=date)
    booking2 = Booking(slot_id=slot2.id, user_id=user1.id, date=date)
    booking3 = Booking(slot_id=slot2.id, user_id=user2.id, date=date)
    db_session.add_all([booking1, booking2, booking3])
    await db_session.commit()

    user1_bookings = await BookingRepository.get_bookings_by_user_id(user1.id)

    assert len(user1_bookings) == 2
    assert user1_bookings[0]["room_name"] == "Конференц-зал"
    assert "booking_id" in user1_bookings[0]


@pytest.mark.asyncio
async def test_get_booking_details(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="VIP комната")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.flush()

    date = datetime.date.today()
    booking = Booking(slot_id=slot.id, user_id=user.id, date=date)
    db_session.add(booking)
    await db_session.commit()

    details = await BookingRepository.get_booking_details(booking.id)

    assert details is not None
    assert details.room_name == "VIP комната"
    assert details.start_time == "10:00"
    assert details.end_time == "12:00"


@pytest.mark.asyncio
async def test_create_booking(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Тестовая комната")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.commit()

    booking_data = {
        "slot_id": slot.id,
        "date": datetime.date.today()
    }

    booking_id = await BookingRepository.create_booking(booking_data, user.id)

    assert booking_id is not None
    assert isinstance(booking_id, int)


@pytest.mark.asyncio
async def test_delete_all_bookings(db_session: AsyncSession):
    user1 = User(
        username="user1",
        surname="Иванов",
        email="user1@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    user2 = User(
        username="user2",
        surname="Петров",
        email="user2@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    room = Room(name="Тестовая комната")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.flush()

    date = datetime.date.today()

    booking1 = Booking(slot_id=slot1.id, user_id=user1.id, date=date)
    booking2 = Booking(slot_id=slot2.id, user_id=user1.id, date=date)
    booking3 = Booking(slot_id=slot2.id, user_id=user2.id, date=date)
    db_session.add_all([booking1, booking2, booking3])
    await db_session.commit()

    result = await BookingRepository.delete_all_bookings(user1.id)
    assert result is True

    user1_bookings = await BookingRepository.get_bookings_by_user_id(user1.id)
    user2_bookings = await BookingRepository.get_bookings_by_user_id(user2.id)

    assert len(user1_bookings) == 0
    assert len(user2_bookings) == 1


@pytest.mark.asyncio
async def test_delete_booking_for_admin(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Тестовая комната")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.flush()

    booking = Booking(slot_id=slot.id, user_id=user.id, date=datetime.date.today())
    db_session.add(booking)
    await db_session.commit()

    result = await BookingRepository.delete_booking_for_admin(booking.id)
    assert result is True

    deleted = await BookingRepository.is_booking(booking.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_bookings_for_admin(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Тестовая комната")
    db_session.add(room)
    await db_session.flush()

    slot1 = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    slot2 = Slot(room_id=room.id, start_time="12:00", end_time="14:00")
    db_session.add_all([slot1, slot2])
    await db_session.flush()

    date = datetime.date.today()

    booking1 = Booking(slot_id=slot1.id, user_id=user.id, date=date)
    booking2 = Booking(slot_id=slot2.id, user_id=user.id, date=date)
    db_session.add_all([booking1, booking2])
    await db_session.commit()

    result = await BookingRepository.delete_bookings_for_admin()
    assert result is True

    bookings = await BookingRepository.is_bookings()
    assert len(bookings) == 0


@pytest.mark.asyncio
async def test_get_bookings_for_admin(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Иванов",
        email="test@test.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()

    room = Room(name="Конференц-зал")
    db_session.add(room)
    await db_session.flush()

    slot = Slot(room_id=room.id, start_time="10:00", end_time="12:00")
    db_session.add(slot)
    await db_session.flush()

    date = datetime.date.today()
    booking = Booking(slot_id=slot.id, user_id=user.id, date=date)
    db_session.add(booking)
    await db_session.commit()

    bookings = await BookingRepository.get_bookings_for_admin(date=date, page=1, limit=10)

    assert len(bookings) >= 1
    assert bookings[0].username == "testuser"
    assert bookings[0].surname == "Иванов"
    assert bookings[0].room_name == "Конференц-зал"
    assert bookings[0].start_time == "10:00"
    assert bookings[0].end_time == "12:00"