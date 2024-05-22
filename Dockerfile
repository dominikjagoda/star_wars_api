FROM python:3.10-slim


WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install .

WORKDIR /app/src/sw_world/

CMD  ["python", "sw_world.py", "--interval", "5"]