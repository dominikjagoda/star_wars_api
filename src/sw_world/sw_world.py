import requests
import random
import json
import time
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

        return {"people": people_data, "planets": planet_data}

    def check_if_yaml_field_exist(self, field_name, field_type, yaml_path):
        with open(yaml_path, "r") as f:
            yaml_data = yaml.safe_load(f)
            for field in yaml_data[field_type]:
                if field_name in field.values():
                    logging.warning(f"Field {field_name} already exists in {yaml_path}")
                    return True
                else:
                    return False

    def to_yaml(self, data, yaml_path):
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)


def main():
    sw = SWWorld(config_path="/home/domino/star_wars_api/src/sw_world/config.json")
    data = sw.select_data_from_json()
    result = sw.check_if_yaml_field_exist(
        field_name=data["people"]["name"],
        yaml_path="/home/domino/star_wars_api/src/test.yaml",
    )
    sw.to_yaml(data=data, yaml_path="/home/domino/star_wars_api/src/test.yaml")


if __name__ == "__main__":
    main()
