import os
import json
import math
import time
import requests
from drs import drs
from getpass import getpass

def get_language_nums(stats, languages):
    language_score = {}

    for language_key in languages.keys():
        if language_key in stats.keys():
            language_score[language_key] = stats[language_key]
        else:
            language_score[language_key] = min(stats.values())

    language_score = {k: v / sum(language_score.values()) for k, v in language_score.items()}
    n = len(language_score)

    lower_bounds = []
    upper_bounds = []

    for score in language_score.values():
        lower_bounds.append(max(min_num_per_language, int(round(num * score * lower_coeff))))
        upper_bounds.append(max(min_num_per_language, int(round(num * score * upper_coeff))))

    nums = drs(n, num, upper_bounds, lower_bounds)
    nums = [int(round(x)) for x in nums]
    return language_score.keys(), nums

def get_source_code(html_url):
    tokens = html_url.split('/')
    repo_author, repo_name, source_name = tokens[3], tokens[4], tokens[-1]
    filename = f'({repo_author}\\{repo_name}) {source_name}'
    raw_url = html_url.replace('github.com', 'raw.githubusercontent.com')
    raw_url = raw_url.replace('blob/', '')
    source_code = requests.get(raw_url).text
    return filename, source_code

def get_source_codes(access_token, directory_name, language, num):
    page = 0

    while num > 0:
        page += 1

        per_page = 100 if num > 100 else num
        num -= per_page

        query_parameter = f'+language:{language}' if '.' not in language else f'+extension:{language[1:]}'

        url = f'https://api.github.com/search/code?page={page}&per_page={per_page}&q= +in:file {query_parameter}'
        headers = {
            'Authorization': f'Token {access_token}'
        }

        response = json.loads(requests.request('GET', url, headers=headers).text)
        source_codes = [get_source_code(item['html_url']) for item in response['items']]

        for filename, source_code in source_codes:
            with open(f'{directory_name}{filename}', 'w') as f:
                f.write(source_code)

        time.sleep(8)

if __name__ == '__main__':
    github_dirname = 'github/'

    num = 8000
    min_num_per_language = 2

    lower_coeff = 0.9
    upper_coeff = 1.1

    with open('github.json', 'r') as f:
        stats = json.load(f)

    with open('languages.json', 'r') as f:
        languages = json.load(f)

    language_keys, nums = get_language_nums(stats, languages)
    access_token = getpass('')

    if not os.path.exists(github_dirname):
        os.mkdir(github_dirname)

    for language_key, num in zip(language_keys, nums):
        language_dirname = f'{github_dirname}{language_key}/'

        if os.path.exists(language_dirname):
            continue

        os.mkdir(language_dirname)

        language = languages[language_key]
        get_source_codes(access_token, language_dirname, language, num)
        print(language_key, num)
