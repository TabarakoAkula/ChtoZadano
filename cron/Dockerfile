FROM ubuntu:24.04

RUN apt-get update && apt-get install -y cron curl

COPY script.sh /cron/script.sh

COPY cron_task /etc/cron.d/cronjob

RUN chmod 0644 /etc/cron.d/cronjob

RUN crontab /etc/cron.d/cronjob

RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
