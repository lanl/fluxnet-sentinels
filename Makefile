
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

figures/__rolling_fleurus_belon_10_7_0.95.pdf: scripts/01_fit_rolling.py ../../Data/Euroflux/BELon.csv
	python $< --site BE-Lon --date_event 2008-08-23 --path_in ../../Data/Euroflux/BELon.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 235 --tolerance 10 --n_days 7  --event_quantile 0.95 --run_detailed

figures/__rolling_fleurus_bebra_10_7_0.5.pdf: scripts/01_fit_rolling.py ../../Data/Euroflux/BEBra.csv
	python $< --site BE-Bra --date_event 2008-08-23 --path_in ../../Data/Euroflux/BEBra.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 180 --tolerance 10 --n_days 7  --event_quantile 0.5 --run_detailed --event_effect 33.14

figures/__rolling_fleurus_bevie_10_7_0.5.pdf: scripts/01_fit_rolling.py ../../Data/Euroflux/BEVie.csv
	python $< --site BE-Vie --date_event 2008-08-23 --path_in ../../Data/Euroflux/BEVie.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 280 --tolerance 10 --n_days 7  --event_quantile 0.5 --run_detailed --event_effect 33.14

figures/__interaction.pdf: figures/interaction.py
	python $<
 
figures/all.pdf: figures/__rolling_grid_be-lon.pdf figures/__map.pdf figures/__footprint.pdf \
	figures/__map_fukushima.pdf figures/__rolling_fukushima_uswrc.pdf \
	figures/__rolling_fleurus_belon.pdf figures/__rolling_fleurus_bebra.pdf \
	figures/__rolling_fleurus_bevie.pdf
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
