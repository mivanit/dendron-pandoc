from typing import *
import os

import yaml


MY_REFS : List[str] = ['../refs.bib']

def keylist_access_nested_dict(
		d : Dict[str,Any], 
		keys : List[str],
	) -> Tuple[dict,str]:
	"""given a keylist `keys`, return (x,y) where x[y] is d[keys]
	by pretending that `d` can be accessed dotlist-style, with keys in the list being keys to successive nested dicts, we can provide both read and write access to the element of `d` pointed to by `keys`
	
	### Parameters:
	 - `d : Dict[str,Any]`
	   dict to access
	 - `keys : List[str]`   
	   list of keys to nested dict `d`
	
	### Returns:
	 - `Tuple[dict,str]` 
	   dict is the final layer dict which contains the element pointed to by `keys`, and the string is the last key in `keys`
	"""
	
	fin_dict : dict = d
	for k in keys[:-1]:
		if k in fin_dict:
			fin_dict = fin_dict[k]
		else:
			fin_dict[k] = {}
			fin_dict = fin_dict[k]
	fin_key = keys[-1]

	return (fin_dict,fin_key)

def fm_add_to_list(
		data : dict,
		keylist : List[str],
		insert_data : list,
	) -> dict:
	"""add things to the frontmatter
	
	given `keylist`, append to `data[keylist[0]][keylist[1]][...]` if it exists and does not contain `insert_data`
	if `data[keylist[0]][keylist[1]][...]` does not exist, create it and set it to `insert_data`
	"""
	fin_dict,fin_key = keylist_access_nested_dict(data,keylist)
	if fin_key not in fin_dict:
		fin_dict[fin_key] = insert_data
	else:
		for item in insert_data:
			if item not in fin_dict[fin_key]:
				fin_dict[fin_key].append(item)

	return data


def fm_add_bib(
		data : dict, 
		bibfiles : List[str] = MY_REFS,
	) -> dict:
	"""add the bib files to the frontmatter
	
	we want it to look like
	```yaml
	bibliography: [../refs.bib]
	```
	"""

	return fm_add_to_list(
		data = data, 
		keylist = ['bibliography'], 
		insert_data = bibfiles,
	)

def fm_add_filters(
		data : dict, 
		filters : List[str] = ['$FILTERS$/get_markdown_links.py'],
	) -> dict:
	"""add the filters to the frontmatter

	NOTE: this is for a different tool which allows defaults to be set in the frontmatter,
	instead of a separate file. That tools is kind of a mess, but email me if you're interested.

	we want it to look like
	```yaml
	__defaults__:
		filters:
			- $FILTERS$/get_markdown_links.py
	```
	"""

	return fm_add_to_list(
		data = data, 
		keylist = ['__defaults__', 'filters'], 
		insert_data = filters,
	)


DEFAULT_KEYORDER : List[str] = [
	'title',
	'desc',
	'id',
	'created',
	'updated',
	'bibliography',
	'__defaults__',
	'traitIds',
]

class PandocMarkdown(object):
	def __init__(
			self, 
			delim : str = '---',
			loader : Callable[[str],dict] = yaml.safe_load,
			keyorder : List[str] = DEFAULT_KEYORDER,
			writer : Callable[[dict],str] = lambda x : yaml.dump(x, default_flow_style = None, sort_keys = False),
		) -> None:
		
		self.delim = delim
		self.loader = loader
		self.keyorder = keyorder
		self.writer = writer

		# get the first section and parse as yaml
		self.yaml_data : Dict[str, Any] = None
		# get the content
		self.content : str = None

	def load(self, filename : str) -> None:
		"""load a file into the pandoc markdown object
		
		### Parameters:
		 - `filename : str`   
		   the filename to load
		"""

		with open(filename, "r") as f:
			# split the document by yaml file front matter
			sections : List[str] = f.read().split(self.delim)

		# check the zeroth section is empty
		if sections[0].strip():
			raise ValueError(f"file does not start with yaml front matter, found at start of file: {sections[0]}")
		
		if len(sections) < 3:
			raise ValueError(f'missing sections in file {filename}, check delims')

		# get the first section and parse as yaml
		self.yaml_data : Dict[str, Any] = self.loader(sections[1])
		# get the content
		self.content : str = self.delim.join(sections[2:])
	
	def dumps(self) -> str:
		"""dumps both the front matter and content to a string

		NOTE: we want this to be on a single line for compatibility with https://github.com/notZaki/PandocCiter, since that tool parses the bibliography in a weird way. hence, `self.writer` has `default_flow_style = None`
		"""
		if (self.yaml_data is None) or (self.content is None):
			raise Exception('')

		self.keyorder = self.keyorder + [
			k for k in self.yaml_data
			if k not in self.keyorder
		]
		
		# for k in self.keyorder:
		# 	if not (k in self.yaml_data):
		# 		raise KeyError(f'key {k} found in keyorder but not in yaml_data')

		self.yaml_data = {
			k : self.yaml_data[k]
			for k in self.keyorder
			if k in self.yaml_data
		}

		return '\n'.join([
			self.delim,
			self.writer(self.yaml_data).strip(),
			self.delim,
			self.content.lstrip(),
		])


def modify_file_fm(file : str, apply_funcs : List[Callable]) -> None:
	pdm : PandocMarkdown = PandocMarkdown()
	pdm.load(file)

	for func in apply_funcs:
		pdm.yaml_data = func(pdm.yaml_data)
	
	with open(file, "w") as f:
		f.write(pdm.dumps())

def update_all_files_fm(
		dir : str,
		apply_funcs : List[Callable] = [fm_add_bib, fm_add_filters],
	) -> None:
	"""update the frontmatter of all files in a directory
	
	### Parameters:
	 - `dir : str`
	   the directory to update
	 - `apply_funcs : List[Callable]`   
	   list of functions to apply to the frontmatter
	"""

	for file in os.listdir(dir):
		if file.endswith(".md"):
			modify_file_fm(f'{dir.rstrip("/")}/{file}', apply_funcs)

if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print("Usage: python update_frontmatter.py <filename>")
		sys.exit(1)
	
	update_all_files_fm(
		dir = sys.argv[1],
		apply_funcs = [fm_add_bib],
	)