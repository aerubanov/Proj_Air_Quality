import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


@pytest.fixture()
def database_session():
    from src.web.server.common.model import Base
    engine = create_engine('sqlite:///test_db.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()

    yield sess
    sess.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def bot_db_session():
    from src.web.bot.application.model import Base
    engine = create_engine('sqlite:///test_db.db')
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    yield Session
    Session.remove()
    Base.metadata.drop_all(engine)
