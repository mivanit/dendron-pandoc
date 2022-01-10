# dendron-pandoc

[Dendron](https://wiki.dendron.so) is a markdown based note taking tool, and [Pandoc](https://pandoc.org/MANUAL.html) is a document conversion tool. However, they don't always play nice together. I wanted to be able to compile my Dendron vault into nice PDFs using pandoc, which is why this exists.

## Features:
- Pandoc filters for making Dendron links work properly
- a script for adding bibliography information (or other data) to all markdown files in a vault
- also, you should use [`pandoc-mermaid-filter`](https://github.com/timofurrer/pandoc-mermaid-filter)


# `dendron-links-filters`
Dendron links look like `[[link.to.a.file]]`, which does not work by default with Pandoc. Pandoc filters are provided to convert the links. 

## Files:

- `dendron_links_md.py`: parses the links into the Pandoc AST. 
- `dendron_links_pdf.py`: parses the links, but will additionally link to pdfs files of the same name instead of raw markdown files.
- `_dendron_link_tools.py` provides the utilities for working with the Pandoc AST.

## Requirements

- [`pandocfilters`](https://pypi.org/project/pandocfilters/) (a python package)
- [Pandoc](https://pandoc.org/MANUAL.html) itself

## Usage:

To convert a markdown file to a `.tex` file with working links to the original markdown:
```bash
pandoc my.dendron.file.md -o my.dendron.file.tex --filter dendron_links_md.py
```
Or, if you intent to compile every file into a pdf:
```bash
pandoc my.dendron.file.md -o my.dendron.file.tex --filter dendron_links_pdf.py
```

If you intent to compile many files, you may create a `defaults.yaml` file with the following:
```yaml
filters:
- dendron_links_pdf.py
```

and invoke it with
```bash
pandoc my.dendron.file.md -o my.dendron.file.tex --defaults defaults.yaml
```

> more information about pandoc filters: https://pandoc.org/filters.html

# `frontmatter`

To be able to cite things from a bibtex file in your notes, you need to set the bibliography in the frontmatter. `update_frontmatter.py` sets the same bibliography in the frontmatter in all files in a directory.

## Usage:
First, in `update_frontmatter.py` set `MY_REFS` equal to a list of paths (absolute, or relative to the *markdown file itself, **not** the python script*).

Then, run the script, pointing it to your Dendron vault
```bash
python update_frontmatter.py vault
```
(note: there may be some weirdness for joining paths)

> designed to work with the vscode extension [PandocCiter](https://github.com/notZaki/PandocCiter)

# mermaid

mermaid is a tool for making charts and diagrams that is used in Dendron. Thankfully, there already exists a filter for making this work with Pandoc: [`pandoc-mermaid-filter`](https://github.com/timofurrer/pandoc-mermaid-filter)


# planned features:

- somehow getting citations to look nice in the Dendron preview
- resolving LaTeX macros into raw LaTeX for the Dendron preview

