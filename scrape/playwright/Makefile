# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

url := "https://cchcs.ca.gov/reports/ab2761/"
html := output/soup.html
lost := output/lost.yml
records := output/deaths.parquet

.PHONY: all clean

all: $(records)

clean:
	-rm -r output/*

$(records): \
	src/format.py \
	$(html)
	python $< \
		--input=$(html)\
		--lost=$(lost)\
		--output=$@

$(html): \
	src/scrape.py
	-mkdir output
	python $< \
		--url=$(url)\
		--output=$@

# done
