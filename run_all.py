"""Run every notebook in order (needs Jupyter):  python run_all.py
Each notebook is executed in place, so its saved outputs are always from the latest run."""
import subprocess, sys
from pathlib import Path

ORDER = ['00_overview_and_sources', '01_depots_and_supply_areas', '02_grid_capacity_and_congestion', '03_hourly_grid_load',
         '03b_multi_year_grid_load', '04_bus_energy_per_depot', '05_charging_and_grid_comparison',
         '05b_uncertainty_and_variants', '07_results_and_conclusion', '06_checks_and_dictionary']   # 06 last: it checks all outputs
here = Path(__file__).parent / 'notebooks'
for nb in ORDER:
    print('running', nb)
    subprocess.run([sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace',
                    '--ExecutePreprocessor.timeout=-1',      # no time limit: downloads can take minutes
                    str(here / f'{nb}.ipynb')], check=True)
print('all notebooks ran without errors')
