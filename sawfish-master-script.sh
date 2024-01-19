#!/bin/bash

docker-compose up --build sawfish-datasets-extraction
docker-compose up --build sawfish-result-generation
docker-compose up --build sawfish-plot-generation
docker-compose up --build sawfish-paper-generation