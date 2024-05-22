import requests
import random
import json
import time
import argparse
import os
import yaml
import logging
from typing import Any, Literal

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SWWorld:
    def __init__(self, config_path, interval: int = 5):
        """Initialize the SWWorld instance with configuration and interval.

        Args:
            config_path (str): Path to the configuration file.
            interval (int, optional): Time interval between API requests.
                Defaults to 5.
        """
        self._config: dict[str, Any] = self._get_config(config_path)
        self.interval: int = interval
        self.people: list = []
        self.planets: list = []
        self.random_id: int = random.randint(1, self.config["max_person"])

    @property
    def config(self) -> dict[str, Any]:
        """Get the configuration dictionary.

        Returns:
            dict[str, Any]: Configuration dictionary.
        """
        return self._config

    def _get_config(self, config_path: str) -> dict[str, Any]:
        """Load the configuration from the given path.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict[str, Any]: Loaded configuration dictionary.
        """
        with open(config_path, "r") as f:
            return json.load(f)

    def _fetch_data(self, endpoint: Literal["people", "planets"]) -> dict[str, Any]:
        """Fetch data from the SWAPI for the given endpoint.

        Args:
            endpoint (Literal["people", "planets"]): API endpoint to fetch data from.
                Must be either "people" or "planets".

        Returns:
            dict[str, Any]: Fetched data as a dictionary.
        """
        url = f"https://swapi.dev/api/{endpoint}/{self.random_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.HTTPError(
                f"Failed to fetch data from {url}, status code: {response.status_code}"
            )

    def add_person(self):
        """Add a person to the people list."""
        people = self._fetch_data("people")
        self.people.append(people)

    def add_planet(self):
        """Add a planet to the planets list."""
        planets = self._fetch_data("planets")
        self.planets.append(planets)

    def to_json(self) -> dict[str, Any]:
        """Fetch and return the people and planets data as JSON.

        Returns:
            dict[str, Any]: Dictionary containing people and planets data.
        """
        self.add_person()
        time.sleep(self.interval)
        self.add_planet()

        return {"people": self.people, "planets": self.planets}

    def select_data_from_json(self) -> dict[str, Any]:
        """Select specific data from the fetched JSON.

        Returns:
            dict[str, Any]: Dictionary containing selected people and planets data.
        """
        data = self.to_json()
        people = data["people"][0]
        planet = data["planets"][0]

        people_data = {"name": people.get("name"), "height": people.get("height")}
        planet_data = {"name": planet.get("name"), "height": planet.get("terrain")}

        return {"people": [people_data], "planets": [planet_data]}

    def _check_if_yaml_field_exist(
        self, yaml_data: list[dict[str, str]], field_name: str
    ) -> bool:
        """Check if a field exists in the YAML data.

        Args:
            yaml_data (List[dict[str, Any]]): List of dictionaries representing YAML data.
            field_name (str): Field name to check for existence.

        Returns:
            bool: True if field exists, False otherwise.
        """
        for elemnet in yaml_data:
            if field_name in elemnet.values():
                logging.warning(f"Field {field_name} already exists.")
                return True

        return False

    def append_row(
        self, data: list[dict[str, str]], field_type: str
    ) -> tuple[list[dict[str, Any]], int]:
        """Append a row of data to the YAML file if it doesn't already exist.

        Args:
            data (list[dict[str, str]]): Data to append.
            field_type (str): Type of field to append (people or planets).

        Returns:
            tuple[list[dict[str, Any]], int]: Updated list of data and the number of elements.
        """
        yaml_path = self.config["output_path"]
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                yaml_data = yaml.safe_load(f)

            elemnets_number = len(yaml_data[field_type])
            # Checks if number of people or planet reach `count_of_people_and_planet`
            if elemnets_number >= self.config["count_of_people_and_planet"]:
                logging.warning(
                    f"Number of {field_type} reach `count_of_people_and_planet`."
                )
                return yaml_data[field_type], elemnets_number

            exist = self._check_if_yaml_field_exist(
                yaml_data=yaml_data[field_type], field_name=data[0]["name"]
            )
            if not exist:
                yaml_data[field_type].extend(data)

            return yaml_data[field_type], elemnets_number
        else:
            return (data, 0)

    def to_yaml(self, data: dict[str, Any]):
        """Write data to a YAML file.

        Args:
            data (dict[str, List[dict[str, Any]]]): Data to write to the YAML file.
        """
        yaml_path = self.config["output_path"]
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)


def main():
    """Main function to run the SWWorld data fetching and writing process."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, help="Interval number")
    args = parser.parse_args()
    interval = args.interval if args.interval else 5

    while True:
        sw = SWWorld(
            config_path=f"{os.getcwd()}/config.json",
            interval=interval,
        )
        sw_data = sw.select_data_from_json()
        sw_people, people_number = sw.append_row(
            data=sw_data["people"], field_type="people"
        )
        sw_planets, planets_number = sw.append_row(
            data=sw_data["planets"], field_type="planets"
        )
        elements_limit = sw._config["count_of_people_and_planet"]
        if (people_number >= elements_limit) and (planets_number >= elements_limit):
            break
        data = {"people": sw_people, "planets": sw_planets}
        sw.to_yaml(data=data)


if __name__ == "__main__":
    main()
