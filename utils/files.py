import os
import json


def find_cache_and_get_data(directory, prefix):
    matching_files = [filename for filename in os.listdir(directory) if filename.startswith(prefix)]

    for filename in matching_files:
        parts = filename.split('_')
        if len(parts) == 3 and parts[2].endswith('.json'):
            start = parts[1]
            end = parts[2][:-5]
            with open(os.path.join(directory, filename), 'r') as file:
                content = json.load(file)
            return content, start, end

    return None, None, None