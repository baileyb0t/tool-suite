# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

link = "https://www.michigan.gov/mcoles/commission-info/revocations"
domain = "https://www.michigan.gov"
outdir := output/pdfs

file_prefix := 'mi-2023'
agents := hand/useragents.yml
names := hand/sitenames.yml
ref_out := output/$(file_prefix)-reference-post2018-index.csv
rev_out := output/$(file_prefix)-revocation-post2018-index.csv

.PHONY: all clean

all: $(rev_out)

clean:
	-rm -r output/*

$(rev_out): \
	src/scrape.py \
	$(hand)
	-mkdir $(outdir)
	python $< \
		--url=$(link) \
		--domain=$(domain) \
		--agents=$(agents) \
		--names=$(names) \
		--outdir=$(outdir) \
		--ref_out=$(ref_out) \
		--rev_out=$@

# done.
