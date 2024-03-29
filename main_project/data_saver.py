import os
import json

def load_data(scrape_data, query):
    file_path = query + '.json'

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(scrape_data, file, indent=4)
    else:
        with open(file_path, 'r+') as file:
            data = json.load(file)
            data.extend(scrape_data)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()


