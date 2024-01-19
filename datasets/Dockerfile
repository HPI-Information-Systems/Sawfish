FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y unzip && \
    rm -rf /var/lib/apt/lists/*

COPY /datasets /datasets

WORKDIR /datasets

CMD unzip -o "SawfishDatasets.zip" && rm "SawfishDatasets.zip"
