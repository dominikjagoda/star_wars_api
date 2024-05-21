import requests
import random
import json
import time
import os
import yaml
import logging
from typing import Any

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SWWorld:
    def __init__(self, config_path, interval: int = 5):
        self._config = self._get_config(config_path)
        self.interval: int = interval
        self.people = []
        self.planets = []

    # powwinno być property
    def _get_config(self, config_path) -> dict[str, Any]:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config

    def _fetch_data(self, endpoint: str, max_id: int) -> dict[str, Any]:
        random_id = random.randint(1, max_id)
        url = f"https://swapi.dev/api/{endpoint}/{random_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("erros")

    def add_person(self):
        max_people_id = self._config["max_person"]
        people = self._fetch_data("people", max_people_id)
        self.people.append(people)

    def add_planet(self):
        max_planet_id = self._config["max_planets"]
        planets = self._fetch_data("planets", max_planet_id)
        self.planets.append(planets)

    def to_json(self) -> dict[str, Any]:
        self.add_person()
        self.add_planet()

        return {"people": self.people, "planets": self.planets}

    def select_data_from_json(self):
        data = self.to_json()
        people = data["people"][0]
        planet = data["planets"][0]

        people_data = {"name": people.get("name"), "height": people.get("height")}
        planet_data = {"name": planet.get("name"), "height": planet.get("terrain")}

        return {"people": [people_data], "planets": [planet_data]}

    def _check_if_yaml_field_exist(self, yaml_data, field_name):
        for elemnet in yaml_data:
            if field_name in elemnet.values():
                logging.warning(f"Field {field_name} already exists.")
                return True
            else:
                return False

    def append_row(self, data, field_type):
        yaml_path = self._config["output_path"]
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                yaml_data = yaml.safe_load(f)

            elemnets_number = len(yaml_data[field_type])
            # Checks if number of people or planet reach `count_of_people_and_planet`
            if elemnets_number >= self._config["count_of_people_and_planet"]:
                logging.warning(
                    f"Number of {field_type} reach `count_of_people_and_planet`."
                )
                return yaml_data[field_type]

            exist = self._check_if_yaml_field_exist(
                yaml_data=yaml_data[field_type], field_name=data[0]["name"]
            )

            if not exist:
                yaml_data[field_type].extend(data)

            return yaml_data[field_type]
        else:
            return data

    def to_yaml(self, data):
        yaml_path = self._config["output_path"]
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)


def main():
    sw = SWWorld(config_path="/home/domino/star_wars_api/src/sw_world/config.json")
    data = sw.select_data_from_json()
    data1 = sw.append_row(data=data["people"], field_type="people")
    data2 = sw.append_row(data=data["planets"], field_type="planets")
    data = {"people": data1, "planets": data2}
    sw.to_yaml(data=data)


if __name__ == "__main__":
    main()
