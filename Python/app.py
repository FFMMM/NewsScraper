import sys
import sqlite3
from datetime import datetime as dt
import time
import Scrapers


def command_error_exit(msg):
	print(msg)
	print_full_help()
	exit(64)


def print_full_help():
	print("Usage: \"python app.py [options]\" With the following options.\r\n")
	print("-f <file path> \t| Specify path of database file to use.")
	print("-q \t| Only adds articles from each publisher to the queue, but does not download and parse them.")
	print("-r \t| Reparses all articles in queue, even those that have been downloaded and parsed before.")
	print("-n \t| Run without saving anything to a database.")
	print("-u <url> \t| Specify a URL to parse before the queue starts")
	print("-h \t| Prints this help message.\r\n")


def main():
	database_filename = 'news.db'

	one_url = None
	queue_only = False
	reparse = False
	no_db = False

	# Parse Command Line Arguments
	if len(sys.argv) > 1:
		args = sys.argv
		recognized_args = ["-q", "-r", "-n", "-f", "-u", "-h"]
		del args[0]  # Remove script name from arguments

		if '-h' in args:
			print_full_help()
			exit(0)
		if '-q' in args:
			queue_only = True
			print("Running in queue only mode")
		if '-n' in args:
			no_db = True
			print("Running with no database. No data will be stored!")
		if '-r' in args:
			reparse = True
			print("Running in reparse mode")
		if '-f' in args:
			filename = args.index("-f")
			if len(args) <= filename+1 or args[filename+1] in recognized_args:
				command_error_exit("Database filename must be specified!\r\n")
			database_filename = args[filename + 1]
		if '-u' in args:
			url = args.index("-u")
			if len(args) <= url+1 or args[url+1] in recognized_args:
				command_error_exit("URL must be specified!\r\n")
			one_url = args[url + 1]

		if not any(a in args for a in recognized_args):
			command_error_exit("Unrecognized argument!\r\n")
	else:
		print("Running with defaults\r\n")

	# If we are using a database, then verify or create it
	if not no_db:
		verify_db(database_filename)
		print("Running with database: " + database_filename)

	print("Queuing Today's Articles")

	q = []
	from Router import Router
	my_router = Router(database_filename)
	i = 0
	for s in my_router.get_scrapers():
		articles = s.get_article_list()
		for a in articles:
			q.append([i, a, dt.now()])
			i += 1
		if not no_db:
			s.queue_article_list(articles)

	print("Queuing Complete With " + str(i) + " Articles")
	if queue_only:
		return

	# If we are running with a database, overwrite the local q with one from the database which will already contain q
	if not no_db:
		q = Scrapers.Scrapers.read_article_queue(database_filename)

	print("Beginning Scraping and Parsing")
	print("==============================\r\n")

	if one_url is not None:
		print("Starting with user-specified URL")
		# Execute a single article with no sleeping, and reparse implicitly set to True
		# because if a user gives us a URL, they want it parsed, even without the -r flag
		execute_article_parse(one_url, database_filename, no_db, True, False)
		print("Continuing with Queued Articles\r\n")

	for a in q:
		execute_article_parse(a[1], database_filename, no_db, reparse, True)

	print("\r\n==============================")
	print("Program Complete!")


def execute_article_parse(url, database_filename, no_db, reparse, sleep=True):
	# Basic setup of objects
	from Router import Router
	my_router = Router(database_filename)
	sc = Scrapers.Scrapers(database_filename)
	sc.url = url
	sc.my_parser = my_router.get_parsers_by_url(sc.url)

	# Check if we should download and parse the article or not
	if no_db or reparse or not sc.is_already_analyzed():
		if not no_db and sc.is_already_analyzed():
			print("Reparsing: " + sc.url)
		else:
			print(sc.url)
		if sleep:
			time.sleep(1)
		sc.get_article_data()
		if not no_db:
			sc.save_data_to_db()


def is_sqlite3(filename):
	from os.path import isfile, getsize
	if not isfile(filename):
		return False
	if getsize(filename) < 100: # SQLite database file header is 100 bytes
		return False
	with open(filename, 'rb') as fd:
		header = fd.read(100)
	return header[:16] == 'SQLite format 3\x00'


def verify_db(file):
	# Verify the database
	if not is_sqlite3(file):
		conn = sqlite3.connect(file)
		c = conn.cursor()
		# Create Article Table
		c.execute('''CREATE TABLE `Articles` (
						`ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
						`ArticleURL` TEXT UNIQUE,
						`Headline` TEXT,
						`Subtitle` TEXT,
						`Author` TEXT,
						`Publisher` TEXT,
						`PublishDate` TEXT,
						`ArticleText` TEXT,
						`ArticleHTML` TEXT,
						`ArticleSources` TEXT,
						`RetrievalDate` TEXT,
						`ArticleSection` TEXT,
						`IsPrimarySource` INTEGER,
						`HasUpdates` INTEGER,
						`HasNotes` INTEGER
					);''')
		# Create Queue Table
		c.execute('''CREATE TABLE `Queue` (
						`ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
						`url` TEXT UNIQUE,
						`dateAdded` TEXT
					);''')
		conn.commit()

if __name__ == '__main__':
	# Execute the main program
	main()
