FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "elevation-service", "/bin/bash", "-c"]

EXPOSE 5000
ENV FLASK_APP=app.py