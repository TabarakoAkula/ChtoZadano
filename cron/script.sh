#!/bin/bash

curl "web:8000/api/v1/delete_old_homework/" --request POST --header "Content-Type: application/json" --data '{"api_key": "{your_api_key}", "telegram_id": {superuser_tg_id} }'
echo "Delete old homework and todo at $(date)" >> /var/log/cron.log
echo "Delete old homework at $(date)"
