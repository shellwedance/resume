VENV   ?= .venv
PYTHON := $(VENV)/bin/python
OUT    ?= $(HOME)/Desktop/taeuk_kim_resume.pdf
URL    ?= https://shellwedance.github.io/resume/

.PHONY: pdf clean-venv

# Print the resume to an A4 PDF with per-item page breaks.
#
#   make pdf                      -> ~/Desktop/taeuk_kim_resume.pdf
#   make pdf OUT=out.pdf          -> custom output path
#
# NOTE: URL defaults to the *published* GitHub Pages site, so local edits only
# show up in the PDF after they are pushed to gh-pages and the Pages build has
# finished (usually 1-2 min). To print uncommitted local changes, run a local
# Jekyll server in another terminal and point URL at it:
#
#   bundle exec jekyll serve
#   make pdf URL=http://127.0.0.1:4000/resume/
#
# Page-break rules live in scripts/paginate.js; the Chrome driver is
# scripts/print_pdf.py. First run creates .venv and installs websocket-client.
pdf: $(VENV)/.installed
	$(PYTHON) scripts/print_pdf.py "$(OUT)" --url "$(URL)"

$(VENV)/.installed:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet websocket-client
	touch $@

clean-venv:
	rm -rf $(VENV)
