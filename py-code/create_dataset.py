import re
import glob
import json
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split

def replace_text(text, signs, pattern):
	for sign in signs:
		text = re.sub(re.compile(f'{sign}.*?{sign}', re.DOTALL), pattern, text)

	return text

def remove_comments(text, signs):
	for one, first, second in signs:
		text = re.sub(re.compile(f'{first}.*?{second}', re.DOTALL), '', text)
		text = re.sub(re.compile(f'{one}.*?\n'), '', text)

	return text

def split_text(text):
	return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def save_dataset(filename, dataset):
	with open(filename, 'w') as f:
		for label, text in dataset:
			f.write(f'{label} {text}\n')

if __name__ == '__main__':
	signs = [
		['//', '/\*', '\*/'],
		['#', '"""', '"""'],
		['--', '<!--', '-->']
	]

	github_name = 'github/'
	stackoverflow_name = 'stackoverflow/'

	train_filename = '../../fastText/train.txt'
	test_filename = '../../fastText/test.txt'

	dataset = []

	for filename in glob.iglob(github_name + '/**/*/*', recursive=True):
		language = filename.split('/')[1]

		with open(filename, 'r') as f:
			source_code = f.read()
			clean_code = remove_comments(replace_text(source_code, '\'"', ' strv '), signs)
			text = ' '.join(split_text(clean_code))
			label = '__label__' + language.replace(' ', '_')
			dataset.append(tuple((label, text)))

	for filename in glob.iglob(stackoverflow_name + '/*.txt'):
		with open(filename, 'r') as f:
			markdown_text = f.read()
			soup = BeautifulSoup(markdown_text, 'html.parser')
			plain_text = soup.get_text()
			text = ' '.join(split_text(plain_text))
			label = '__label__Other'
			dataset.append(tuple((label, text)))

	labels = [x[0] for x in dataset]
	train_dataset, test_dataset = train_test_split(dataset, stratify=labels,
		                                           train_size=0.8, random_state=42)

	save_dataset(train_filename, train_dataset)
	save_dataset(test_filename, test_dataset)

	print(f'Train set: {len(train_dataset)}.')
	print(f'Test set: {len(test_dataset)}.')
