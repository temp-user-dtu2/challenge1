''' #############
#### CLI Parsing ####
''' #############
import sys, os

if len(sys.argv) < 2:
    print("Please provide the path to file")
    exit(1)

database_path = sys.argv[1]

if ".xml" not in database_path:
    print("The file should have an xml format")
    exit(2)

''' ############
#### Processing ####
''' ############

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def save_article(database, index_file, processed_file):
    pageElement = "  <page>"
    while True:
        line = database.readline()
        if "#REDIRECT" in line:
            return

        pageElement = pageElement + line
        if "</page>" in line:
            break
    tree = ET.ElementTree(ET.fromstring(pageElement))
    text = tree.find(".//text")
    if text.text:
        post_processed = tree.find(".//text").text.lower().replace('\n', ' ') + '\n'
    else:
        return

    processed_file.write(post_processed)

    global file_size
    record = tree.find("title").text + ":" + str(file_size) + ":" + str(processed_file.tell() - file_size) + '\n'
    index_file.write(record)

    file_size = processed_file.tell()

file_size = 0

with open(database_path, 'r', encoding="utf-8") as database, \
     open("index.txt", 'w', encoding="utf-8") as index_file, \
     open("database.txt", 'w', encoding="utf-8") as processed_file:
    while True:
        line = database.readline()
        if not line:
            break # End when EOF is reached

        if "<page>" in line:
            save_article(database, index_file, processed_file)