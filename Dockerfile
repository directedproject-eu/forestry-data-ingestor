FROM python:3.13-slim

#
# Fight OS CVEs and install dependencies
#
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get dist-upgrade -y \
 && apt-get clean \
 && apt autoremove -y  \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY forestry_data_ingestor ./forestry_data_ingestor

ENTRYPOINT [ "python", "/app/forestry_data_ingestor/ingestor.py"]
