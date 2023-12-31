# organize_pictures_filecloud.py
-----------------

## Script Function
-----------------

The purpose of this script is to organize files by year and month on FileCloud.

This script assumes that the pictures in the source folder have the date in YYYYMMDD format anywhere in the name

E.g. 20230419-mypicture.png, 20230419.png, IMG-20230318-WAH.mp4 are all acceptable file formats. 

## Parameters
-----------------
* `-h`, `--help` : Show this help message and exit.
* `-u USERNAME`, `--username USERNAME` : Your FileCloud username.
* `-p PASSWORD`, `--password PASSWORD` : Your FileCloud password.
* `-s SERVER_URL`, `--server_url SERVER_URL` : The URL of the FileCloud server.
* `-f SOURCE_FOLDER`, `--source_folder SOURCE_FOLDER` : The source folder in FileCloud where the files are located.
* `-d TARGET_FOLDER`, `--target_folder TARGET_FOLDER` : The target folder in FileCloud where you want to move the files.

## Usage
-----------------


```bash
./organize_pictures_filecloud.py -u USERNAME -p PASSWORD -s SERVER_URL -f SOURCE_FOLDER -d TARGET_FOLDER
```
