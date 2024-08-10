FROM ubuntu:24.04

RUN apt update && apt install cron -y
RUN apt install curl -y

RUN mkdir -p cron

ADD delete_old_hw_script.sh cron/delete_old_hw_script.sh

RUN chmod 0755 cron/delete_old_hw_script.sh

ADD cron_task /etc/cron.d/cron_task

RUN chmod 0644 /etc/cron.d/cron_task

RUN touch cron/cron_task.log

CMD cron && tail -f cron/cron_task.log
