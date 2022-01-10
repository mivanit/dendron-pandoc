from pandocfilters import toJSONFilter
from _dendron_link_tools import dendron_to_markdown_factory

if __name__ == "__main__":
	toJSONFilter(dendron_to_markdown_factory(
		linktext_gen = lambda x : x.split('.')[-1],
		pref = '',
		ext = 'md',
	))