FROM python:alpine

WORKDIR /app
COPY reqs.txt ./
RUN mkdir venv && \
    python3 -m venv venv && \
    source ./venv/bin/activate && \
    python3 -m pip install -r reqs.txt

COPY main.py config.toml secrets.toml entrypoint.sh ./
ENTRYPOINT ["./entrypoint.sh"]
