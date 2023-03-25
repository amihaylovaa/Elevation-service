FROM continuumio/miniconda3

WORKDIR /app

COPY . /app

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "elevation-service", "/bin/bash", "-c"]

ENV FLASK_APP=app.py

CMD ["flask", "run"]