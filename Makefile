VENV   ?= .venv
PYTHON := $(VENV)/bin/python
OUT    ?= $(HOME)/Desktop/taeuk_kim_resume.pdf
URL    ?= https://shellwedance.github.io/resume/

.PHONY: pdf clean-venv

# Print the published resume to an A4 PDF with per-item page breaks.
#   make pdf                      -> ~/Desktop/taeuk_kim_resume.pdf
#   make pdf OUT=out.pdf URL=http://127.0.0.1:4000/resume/
pdf: $(VENV)/.installed
	$(PYTHON) scripts/print_pdf.py "$(OUT)" --url "$(URL)"

$(VENV)/.installed:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet websocket-client
	touch $@

clean-venv:
	rm -rf $(VENV)
