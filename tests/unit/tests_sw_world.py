import pytest
from sw_world import SWWorld


DATASET_1 = [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}]
DATA_FIELD_1 = "value2"


@pytest.fixture()
def sw_word():
    sw = SWWorld(
        config_path="/home/domino/star_wars_api/src/sw_world/config.json",
        interval=1,
    )
    yield sw


def test__check_if_yaml_field_exist(sw_word):
    result = sw_word._check_if_yaml_field_exist(
        yaml_data=DATASET_1, field_name=DATA_FIELD_1
    )
    assert result
