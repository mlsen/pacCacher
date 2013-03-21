import configparser
import re

config = configparser.ConfigParser()
config.read('paccacher.conf')

repo = configparser.ConfigParser()
repo.read('repos.conf')

# Define constants from config file
HOST = config['general'].get('host', '0.0.0.0')
PORT = config['general'].getint('port', 9001)
CHUNK_SIZE = 16 * 1024
LOG_LEVEL = config['general'].get('log_level', 'WARNING')

def get_list(s):
    return re.split(r'\W+', s)
