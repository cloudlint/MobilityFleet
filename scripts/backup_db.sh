#!/bin/bash

# === CONFIGURATION ===
DB_NAME="scooter_db2"
DB_USER="scooteruser"
DB_HOST="localhost"
BACKUP_DIR="/Volumes/Data/Business/scootdr/db_backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
FILENAME="scooter_db2_${DATE}.sql"

# === CREATE BACKUP ===
pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" > "$BACKUP_DIR/$FILENAME"

# === DELETE OLD BACKUPS (OLDER THAN 3 DAYS) ===
find "$BACKUP_DIR" -name "*.sql" -type f -mtime +3 -exec rm {} \;

# === LOGGING ===
echo "[$(date)] Backup created: $FILENAME" >> "$BACKUP_DIR/backup.log"
