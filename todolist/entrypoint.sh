#!/bin/bash
# Проверяем, есть ли миграции
python manage.py migrate --check
status=$?
if [[ $status != 0 ]]; then
  python manage.py migrate
fi
exec "$@"
