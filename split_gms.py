import glob
import os

from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.silence import detect_nonsilent

LANGUAGES = {
	'ENCA': ('EN', 'CA'),
	'ENDE': ('EN', 'DE'),
	'ENEL': ('EN', 'EL'),
	'ENES': ('EN', 'ES'),
	'ENESM': ('EN', 'ESM'),
	'ENRU': ('EN', 'RU'),
	'ENTGL': ('EN', 'TGL'),
	'ENTR': ('EN', 'TR'),
	'ENUKR': ('EN', 'UKR'),
	'ENZS': ('EN', 'ZS'),
	'ENZT': ('EN', 'ZT'),
	'PBESM': ('PB', 'ESM'),
	'PBENFR': ('PB', 'EN', 'FR'),
}


class FileInfo:
	def __init__(self, filename: str, book: str, first_sentence: int, languages: str):
		self.filename = filename
		self.book = book
		self.first_sentence = first_sentence
		self.languages = languages

	def __repr__(self):
		return self.filename


def extract_sentences(file_info: FileInfo):
	# this extracts all sentences from an mp3 file and exports it to its own individual file
	print("Analyzing '{}'".format(file_info))
	track = AudioSegment.from_mp3(file_info.filename)
	chunks = split_on_silence(
		track,
		min_silence_len=1800,
		silence_thresh=-60,
		keep_silence=25
	)

	languages = LANGUAGES[file_info.languages]

	# if it's GMS C, it'll have more than 100 sentences (100 + the intro and outro)
	if len(chunks) > 100:
		# skip intro + all language names
		chunks = chunks[len(languages):-2]
	else:
		# skip intro + target language name
		chunks = chunks[2:-2]

	if not len(chunks) % 50 == 0 or len(chunks) == 0:
		print("** ERR: INVALID NUMBER OF CHUNKS ({}), SKIPPING **".format(len(chunks)))
		return

	for i, sentence in enumerate(chunks):
		if len(chunks) > 50:
			num = int(i / len(languages))
			language = languages[i % len(languages)]
		else:
			num = i
			language = languages[-1]

		filename = "{} - {} - {num:04d}.mp3".format(language, file_info.book,
													num=num + file_info.first_sentence)
		directory = os.path.join('output', language, file_info.book)
		if not os.path.exists(directory):
			os.makedirs(directory)
		export_path = os.path.join(directory, filename)
		# print("Extracting '{}'".format(export_path))
		sentence.export(export_path, codec='mp3')


def get_file_info(mp3_file) -> FileInfo:
	parts = mp3_file.split('-')
	languages = parts[0].split('/')[-1]
	book = parts[1]
	sentence_num = int(parts[-1].rstrip('.mp3'))
	return FileInfo(filename=mp3_file, book=book, first_sentence=sentence_num, languages=languages)


def main():
	path = os.path.join('files', '*.mp3')
	mp3_files = glob.glob(path)
	mp3_files.sort()

	for mp3_file in mp3_files:
		file_info = get_file_info(mp3_file)
		extract_sentences(file_info)


if __name__ == '__main__':
	main()
