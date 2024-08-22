import pytest
from tests.testdata import CREATE_EVENT
from cryptomanga.handler.train_handler import TrainHandler


@pytest.fixture
def train_handler():
    return TrainHandler()

@pytest.fixture
def create_event():
    return CREATE_EVENT

