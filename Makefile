
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

../../Data/Asiaflux/FHK.csv: scripts/00_get_japanflux.py
	python $<

figures/__rolling_fukushima_uswrc.pdf: figures/rolling_fukushima.py ../../Data/Asiaflux/FHK.csv
	python $<

figures/__rolling_fleurus_belon.pdf: figures/rolling_fleurus.py \
	../../Data/Euroflux/BELon.csv ../../Data/Euroflux/BEBra.csv ../../Data/Euroflux/BEVie.csv
	python $<

figures/all.pdf: figures/__rolling_grid_be-lon.pdf figures/__map.pdf figures/__footprint.pdf \
	figures/__map_fukushima.pdf figures/__rolling_fukushima_uswrc.pdf figures/__rolling_fleurus_belon.pdf
	pdftk $(wildcard figures/__*.pdf) output $@

# ---
data/ameriflux_pnw.csv: scripts/00_get_ameriflux.R
	Rscript $<

figures/__map_fukushima.pdf: figures/fukushima.R data/ameriflux_pnw.csv
	Rscript $<

../../Data/Euroflux/BELon.csv: scripts/00_get_euroflux.py
	python $< --site_id BE-Lon --subfolder L2-L4_2004-2012

../../Data/Euroflux/BEBra.csv: scripts/00_get_euroflux.py
	python $< --site_id BE-Bra

../../Data/Euroflux/BEVie.csv: scripts/00_get_euroflux.py
	python $< --site_id BE-Vie

# ---
clean:
	-rm figures/figures.pdf
	-rm *.gpkg
	-rm test*.gpkg
	-rm test*.pdf
