class Article(object):
	url = ""
	title = ""
	subtitle = ""
	author = ""
	publisher = ""
	publish_date = ""
	article_text = ""
	full_html = ""
	sources = []
	fetch_date = ""
	updates = False
	editor_notes = False
	corrections = False
	section = []

	def __init__(self):
		pass
