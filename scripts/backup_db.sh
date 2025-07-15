#!/bin/bash

# Set constants
BACKUP_DIR="/Volumes/Data/Business/scootdr/db_backups"
DATE=$(date +%F)
FILENAME="scooter_backup_$DATE.sql"
DB_NAME="scooter_db2"
DB_USER="scooteruser"
DB_HOST="localhost"
DB_PORT="5432"

# Create backup using .pgpass for authentication
pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT -f "$BACKUP_DIR/$FILENAME" $DB_NAME

# Remove backups older than 3 days
find "$BACKUP_DIR" -name "scooter_backup_*.sql" -type f -mtime +3 -exec rm {} \;
