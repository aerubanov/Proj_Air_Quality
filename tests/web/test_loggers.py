import logging.config
import pytest

from src.web.client.logging_config import LOGGING_CONFIG as CLIENT_CONFIG
from src.web.bot.logging_config import LOGGING_CONFIG as BOT_CONFIG
from src.web.server.logging_config import LOGGING_CONFIG as SERVER_CONFIG


@pytest.fixture
def logging_file(tmpdir):
    dir_name = 'test_logs'
    d = tmpdir.mkdir(dir_name)
    f = d.join("log.txt")
    yield f


def test_client_logging(logging_file):
    f = logging_file

    CLIENT_CONFIG['handlers']['client_file_handler']['filename'] = f
    logging.config.dictConfig(CLIENT_CONFIG)
    logger = logging.getLogger('ClientLogger')
    logger.info('tests')

    assert len(f.readlines()) == 1


def test_bot_logging(logging_file):
    f = logging_file

    BOT_CONFIG['handlers']['bot_file_handler']['filename'] = f
    logging.config.dictConfig(BOT_CONFIG)
    logger = logging.getLogger('BotLogger')
    logger.info('tests')

    assert len(f.readlines()) == 1


def test_server_logging(logging_file):
    f = logging_file

    SERVER_CONFIG['handlers']['api_file_handler']['filename'] = f
    SERVER_CONFIG['handlers']['loader_file_handler']['filename'] = f
    SERVER_CONFIG['handlers']['ml_file_handler']['filename'] = f
    logging.config.dictConfig(SERVER_CONFIG)

    logger = logging.getLogger('ApiLogger')
    logger.info('tests')
    assert len(f.readlines()) == 1

    logger = logging.getLogger('LoaderLogger')
    logger.info('tests')
    assert len(f.readlines()) == 2

    logger = logging.getLogger('MLLogger')
    logger.info('test')
    assert len(f.readlines()) == 3
