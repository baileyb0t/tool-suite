# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all: demo.html

clean:
	-rm -r output/*

demo.html: demo.ipynb
	jupyter nbconvert --to notebook --inplace --execute demo.ipynb
	jupyter nbconvert --to html --template pj demo.ipynb
