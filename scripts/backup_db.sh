#!/bin/bash

# Constants
BACKUP_DIR="/Volumes/Data/Business/scootdr/db_backups"
DATE=$(date +%F)
FILENAME="scooter_backup_$DATE.sql.gz"
DB_NAME="scooter_db2"
DB_USER="scooteruser"
DB_HOST="localhost"
DB_PORT="5432"
LOGFILE="$BACKUP_DIR/backup.log"
EMAIL_SUCCESS="mmhussein13@gmail.com"
EMAIL_FAILURE="mmhusein13@gmail.com"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Start logging
{
  echo "----- $(date '+%Y-%m-%d %H:%M:%S') -----"
  echo "Starting backup for $DB_NAME..."

  # Export password
  export PGPASSWORD="Flexiblepony@12"

  # Run pg_dump and compress it
  if pg_dump -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"; then
    echo "Backup successful: $FILENAME"

    # Optional email on success
    echo "PostgreSQL backup succeeded: $FILENAME" | mail -s "Backup SUCCESS" "$EMAIL_SUCCESS"
  else
    echo "Backup FAILED!"

    # Optional email on failure
    echo "PostgreSQL backup FAILED on $(date)" | mail -s "Backup FAILED" "$EMAIL_FAILURE"
  fi

  # Cleanup old compressed backups
  echo "Cleaning up backups older than 3 days..."
  find "$BACKUP_DIR" -name "scooter_backup_*.sql.gz" -type f -mtime +3 -delete

  echo "Done."
  echo
} >> "$LOGFILE" 2>&1

