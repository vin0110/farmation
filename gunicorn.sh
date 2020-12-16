#!/bin/bash
source /home/vwfreeh/env
/home/vwfreeh/.local/share/virtualenvs/farmation-Ms0p1mkM/bin/gunicorn \
    --pid /run/gunicorn/pid   \
    --bind unix:/run/gunicorn/socket farmation.wsgi
