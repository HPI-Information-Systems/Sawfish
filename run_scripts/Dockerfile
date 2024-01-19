FROM python:3.10.5-slim

RUN apt-get update -y && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean

WORKDIR /app

COPY /run_scripts ./run_scripts
COPY /datasets ./datasets
COPY /results ./results
COPY /metanome ./metanome
COPY /target ./target

RUN chmod +x /app/run_scripts/run_scripts.sh

WORKDIR /app/run_scripts

CMD ["sh", "./run_scripts.sh"]
