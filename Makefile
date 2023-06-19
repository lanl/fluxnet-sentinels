
all: figures/all.pdf

# ---
figures/figures.pdf: figures/figures.Rmd
	Rscript -e 'rmarkdown::render("$<")'
	-pdftk $@ cat 2-end output figures2.pdf
	-mv figures2.pdf $@

# ---
figures/__rolling_heatmap.pdf: figures/rolling_fig.py
	python $<

figures/__rolling_grid_be-lon.pdf: figures/rolling_fig.py
	python $<	

figures/__map.pdf: figures/maps.R
	Rscript $<

figures/__footprint.pdf: figures/footprint.py
	python $<

figures/all.pdf: figures/__rolling_grid_be-lon.pdf figures/__map.pdf figures/__footprint.pdf figures/__map_fukushima.pdf
	pdftk $(wildcard figures/__*.pdf) output $@

# ---
data/ameriflux_ak.csv: scripts/00_get_ameriflux.R
	Rscript $<

figures/__map_fukushima.pdf: figures/fukushima.R data/ameriflux_ak.csv
	Rscript $<

# ---
clean:
	rm figures/figures.pdf
