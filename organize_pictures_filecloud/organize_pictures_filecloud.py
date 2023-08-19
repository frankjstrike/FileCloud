#!/usr/bin/env python3

import requests
import argparse
import sys
import logging
import time
import xml.etree.ElementTree as ET
import re

def get_parameters():
    parser = argparse.ArgumentParser(description="Purpose: Organize files by year and month on FileCloud")
    parser.add_argument("-u", "--username", help="FileCloud username", required=True)
    parser.add_argument("-p", "--password", help="FileCloud password", required=True)
    parser.add_argument("-s", "--server_url", help="FileCloud server's URL", required=True)   
    parser.add_argument("-f", "--source_folder", help="FileCloud source folder", required=True)
    parser.add_argument("-d", "--target_folder", help="FileCloud Pictures folder", required=False)
    
    """If ran without arguments, print help menu"""
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    return args

def get_logger():
    """setup logging"""
    logging.basicConfig(stream = sys.stdout, level=logging.INFO)
    logger = logging.getLogger("Default")
    return logger

def login(username, password, server_url):
    login_url = server_url + "/core/loginguest"
    login_data = {
        "userid": username,
        "password": password,
        "no2facode": 1
    }

    login_response = requests.post(login_url, data=login_data)

    if login_response.status_code == 200:
        logger.info("Login successful!")
    else:
        print("Login failed. Exiting script now.")
        sys.exit()

    return login_response.cookies

def search_files(cookies, source_folder, server_url):

    search_url = server_url + "/core/search"
    search_data = {
        'location': source_folder
    }

    search_response = requests.post(search_url, data=search_data, cookies=cookies)

    """Return a list of files with their full path"""
    xml_data = ET.fromstring(search_response.text)
    
    """Get all 'entry' elements"""
    entries = xml_data.findall('.//entry')

    files = [entry.find('path').text for entry in entries]

    return files

def extract_date_from_name(file_name):
    """Extract the date from the file name"""
    date = re.search(r'\d{8}', file_name).group(0)

    """Check if the date is in the format YYYYMMDD"""
    if date is not None and date.startswith("20") and len(date) == 8:
        return date
    else:
        raise Exception("Date is not in the format YYYYMMDD")


"""Move files to the target folder, if it doesnt exists, create it"""""
def move_files(cookies, files, target_folder, server_url):

    logger.info("> Moving files to the target folder")

    month_map = {
        "01": "01-January",
        "02": "02-February",
        "03": "03-March",
        "04": "04-April",
        "05": "05-May",
        "06": "06-June",
        "07": "07-July",
        "08": "08-August",
        "09": "09-September",
        "10": "10-October",
        "11": "11-November",
        "12": "12-December"
    }

    for file in files:
        try:
            """Get the file name"""
            file_name = file.split("/")[-1]
            file_name_date = extract_date_from_name(file_name)
            
            """Get the file's year and month"""
            file_year = file_name_date[0:4]
            file_month = month_map[file_name_date[4:6]]

            """Create the year folder if it exists"""
            logger.info(f"> Checking if the '{target_folder}{file_year}' folder exists")
            check_year_folder_exists = server_url + "/core/fileexists"
            search_data = {
                'file' : target_folder + file_year,
                'caseinsensitive' : 1
            }

            search_response = requests.post(check_year_folder_exists, data=search_data, cookies=cookies)
            xml_data = ET.fromstring(search_response.text)
            result_element = xml_data.find('.//result')

            if result_element is not None:
                if result_element.text == "0":
                    logger.info(f"> {target_folder}{file_year} folder does not exist. Creating it now.")
                    create_folder(cookies, target_folder + file_year, server_url)
                elif result_element.text == "1":
                    logger.info(f"> {target_folder}{file_year} folder exists.")
            else:
                print("No 'result' element found in the response.") 

            """Checking if the month folder exists"""
            logger.info(f"> Checking if the '{target_folder}{file_year}/{file_month}' folder exists")

            check_month_folder_exists = server_url + "/core/fileexists"
            search_data = {
                'file' : target_folder + file_year + "/" + file_month,
                'caseinsensitive' : 1
            }

            search_response = requests.post(check_month_folder_exists, data=search_data, cookies=cookies)
            xml_data = ET.fromstring(search_response.text)
            result_element = xml_data.find('.//result')

            if result_element is not None:
                if result_element.text == "0":
                    logger.info(f"> {target_folder}{file_year}/{file_month} folder does not exist. Creating it now.")
                    create_folder(cookies, target_folder + file_year + "/" + file_month, server_url)
                elif result_element.text == "1":
                    logger.info(f"> {target_folder}{file_year}/{file_month} folder exists.")

            """Checking if file already exists"""
            logger.info(f"> Checking if file exists in destination")

            dest_file = target_folder + file_year + "/" + file_month + "/" + file_name

            check_file_exists = server_url + "/core/fileexists"
            search_data = {
                'file' : dest_file,
                'caseinsensitive' : 1
            }

            search_response = requests.post(check_file_exists, data=search_data, cookies=cookies)
            xml_data = ET.fromstring(search_response.text)
            result_element = xml_data.find('.//result')

            if result_element is not None:
                if result_element.text == "0":
                    """Move the file to the target folder"""
                    logger.info(f"> Moving file '{file}' to '{target_folder}{file_year}/{file_month}'")
                    move_file_url = server_url + "/core/renameormove"
                    move_file_data = {
                        'fromname' : file,
                        'toname' : dest_file
                    }

                    move_file_response = requests.post(move_file_url, data=move_file_data, cookies=cookies)

                    if move_file_response.status_code == 200:
                        logger.info(f"> File '{file}' moved successfully!")
                    else:
                        logger.info(f"> File '{file}' could not be moved")
                elif result_element.text == "1":
                    logger.info(f"> {dest_file} exists. Deleting it from source")

                    path = file.rsplit('/', 1)[0]
                    file_name = file.split('/')[-1]

                    """Delete the file from the source folder"""
                    delete_file_url = server_url + "/core/deletefile"
                    delete_file_data = {
                        'path' : path,
                        'name' : file_name
                    }

                    delete_file_response = requests.post(delete_file_url, data=delete_file_data, cookies=cookies)

                    if delete_file_response.status_code == 200:
                        logger.info(f"> File '{file}' deleted successfully!")
                    else:
                        logger.info(f"> File '{file}' could not be deleted")
        except Exception as e:
            logger.error(f"> Exception: {e}")


def create_folder(cookies, folder, server_url):

    """Remove last element after /"""
    path = folder.rsplit('/', 1)[0]
    folder_name = folder.split('/')[-1]

    create_folder_url = server_url + "/core/createfolder"
    create_folder_data = {
        'name' : folder_name,
        'path' : path
    }

    try:
        create_folder_response = requests.post(create_folder_url, data=create_folder_data, cookies=cookies)

        if create_folder_response.status_code == 200:
            logger.info(f"> Folder '{folder}' created successfully!")
        else:
            logger.info(f"> Folder '{folder}' could not be created")
    except Exception as e:
        logger.info(f"> Exception: {e}")

def main():

    args = get_parameters()

    username = args.username
    password = args.password
    source_folder = args.source_folder
    server_url = args.server_url
    target_folder = args.target_folder

    """Login to FileCloud and get cookies"""
    cookies = login(username, password, server_url)

    """Get a list of files in the source folder"""
    files = search_files(cookies, source_folder, server_url)

    """If there are no file, dont do anything, else move the files"""
    if len(files) == 0:
        logger.info("No Files to move")
    else:
        move_files(cookies, files, target_folder, server_url)        

if __name__ == "__main__":
    start_time = time.time()    
    """setup logging"""
    logger = get_logger()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))