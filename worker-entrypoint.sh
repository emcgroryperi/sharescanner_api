#!/bin/sh

celery -A sharescanner_api worker -l info --concurrency=3