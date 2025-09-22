FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

ADD gw2tp gw2tp

RUN cd gw2tp && pip install -e .

RUN pip install .

COPY . .

EXPOSE 5000

RUN pip install debugpy

CMD ["uvicorn", "frontend.app:app", "--host", "0.0.0.0", "--port", "5000"]
