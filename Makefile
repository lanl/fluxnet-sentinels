
all: figures/all.pdf

figures/figures.pdf: figures/figures.Rmd
	Rscript -e 'rmarkdown::render("$<")'
	-pdftk $@ cat 2-end output figures2.pdf
	-mv figures2.pdf $@

figures/__rolling_heatmap.pdf: scripts/kelsey.py
	python $<

figures/__rolling_grid.pdf: scripts/kelsey.py
	python $<
	echo \\\\pagenumbering{gobble}| cat - mdtable.md > temp && mv temp mdtable.md
	pandoc mdtable.md -V fontsize=14pt -o $@
	pdfcrop $@ $@

figures/all.pdf: figures/figures.pdf figures/__rolling_grid.pdf
	pdftk $< $(wildcard figures/__*.pdf) output $@

clean:
	rm figures/figures.pdf
