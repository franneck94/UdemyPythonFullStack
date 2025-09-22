FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p /app/database

VOLUME /app/database

COPY pyproject.toml .

COPY gw2tp gw2tp

RUN cd gw2tp && pip install -e .

RUN pip install .

COPY . .

EXPOSE 8000

RUN chmod 777 /app/database

RUN pip install debugpy

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
