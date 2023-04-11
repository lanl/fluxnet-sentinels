
all: figures/all.pdf

figures/figures.pdf: figures/figures.Rmd
	Rscript -e 'rmarkdown::render("$<")'
	-pdftk $@ cat 2-end output figures2.pdf
	-mv figures2.pdf $@

figures/__rolling_heatmap.pdf: scripts/kelsey.py
	python $<

figures/all.pdf: figures/figures.pdf
	pdftk $< $(wildcard figures/__*.pdf) output $@

clean:
	rm figures/figures.pdf
