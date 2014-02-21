#!/bin/bash
python manage.py sqootload firsttime --directload > 02_20_14_sqoot_directload.out
sleep 5m
python manage.py sqootload firsttime --cleanout > 02_20_14_sqoot_cleanout.out
sleep 5m
python manage.py sqootload firsttime --validate > 02_20_14_sqoot_validate.out
sleep 5m
python manage.py sqootload firsttime --deduphard > 02_20_14_sqoot_deduphard.out
