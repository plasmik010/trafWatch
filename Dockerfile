FROM python:3.11-slim
# FROM python:alpine AS builder

RUN apt-get update
RUN apt-get install -y cron

# Copy everything
COPY app/ /app/
COPY config.toml /app/config.toml
COPY crontab /etc/cron.d/trafwatch
COPY run.sh /app/run.sh

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install  -r reqs.txt

RUN chmod +x /app/run.sh && chmod 0644 /etc/cron.d/trafwatch
# ENTRYPOINT ["./entrypoint.sh"]

# Register crontab
RUN crontab /etc/cron.d/trafwatch

# Log location
RUN touch /var/log/cron.log

# CMD cron && tail -f /var/log/cron.log

# Automatically reload crontab on start
CMD crontab /etc/cron.d/trafwatch && cron && tail -f /var/log/cron.log
