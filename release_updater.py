import requests
import re

response = requests.get('https://api.github.com/repos/totvslabs/filterable/releases/latest')
release_info = response.json()
latest_version = re.sub(r'[^0-9.]', '', release_info['tag_name'])

with open('setup.py', 'r') as f:
    setup_file = f.read()
    
setup_file = re.sub("__LATEST_VERSION__", latest_version, setup_file)

with open('setup.py', 'w') as f:
    f.write(setup_file)