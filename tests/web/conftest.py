import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def database_session():
    from src.web.models.model import Base
    engine = create_engine('sqlite:///test_db.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()

    yield sess
    sess.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def bot_db_session():
    from src.web.bot.model import Base
    engine = create_engine('sqlite:///test_db.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()

    yield sess
    sess.close()
    Base.metadata.drop_all(engine)
