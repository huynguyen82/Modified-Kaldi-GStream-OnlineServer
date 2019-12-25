#! /bin/bash
BASE_DIR=/opt/Modified-Kaldi-GStream-OnlineServer
BACKUP_DIR=/mnt/data/asr

FILES_COUNT=$(ls "$BASE_DIR"/tmp | wc -w)
if [ $FILES_COUNT -gt 0 ]; then
    mv "$BASE_DIR"/tmp "$BASE_DIR"/data_tmp && mkdir "$BASE_DIR"/tmp
    chmod o+wr "$BASE_DIR"/tmp
    mv "$BASE_DIR"/data_tmp "$BACKUP_DIR"/$(date +%Y-%m-%d)
fi

