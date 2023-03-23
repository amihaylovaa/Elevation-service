FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml .

# COPY <DEM-FILE> <DEM-FILE>
# ...

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "elevation-service", "/bin/bash", "-c"]

EXPOSE 5000
CMD ["python", "app.py"]