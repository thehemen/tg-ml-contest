import os
import json
import shutil
from stackapi import StackAPI

if __name__ == '__main__':
    dirname = 'stackoverflow/'

    SITE = StackAPI('stackoverflow')
    SITE.page_size = 100
    SITE.max_pages = 20
    result = SITE.fetch('questions', filter='withbody')
    questions = result['items']

    if os.path.exists(dirname):
        shutil.rmtree(dirname)

    os.mkdir(dirname)

    for i, question in enumerate(questions):
        filename = f'Question_{i + 1}.txt'
        body = question['body']

        with open(f'{dirname}{filename}', 'w') as f:
            f.write(body)

    print(f'Quota: {result["quota_remaining"]}')
    print(f'Questions: {len(questions)}')
