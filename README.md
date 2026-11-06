# Electric bus charging and Utrecht's evening grid peak

Group 22 · TIL6022 TIL Python Programming · TU Delft, 2026/27

**Team (Group 22)**

Daniël Oosterink - [@doosterink](https://github.com/doosterink)

Nick Wong - [@nwtud](https://github.com/nwtud)

Shubham Behera - [@shubham5behera](https://github.com/shubham5behera)

Rakesh Chandrikasing - [@rchandrikasing](https://github.com/rchandrikasing)

Most of the work was done together in a shared Google Drive folder (Google Colab notebooks and data files); the final
versions were committed to this repository by the members who made them. The contribution of each member is described
in section 2 of the report.

**Repository contents**

- [Group22_final_report.ipynb](Group22_final_report.ipynb) - the report: research question, data pipeline, results, discussion and conclusion
- [Group22_final_report.html](Group22_final_report.html) - the same report as a web page, readable without running Python
- [TIL6022_Group22_proposal.pdf](TIL6022_Group22_proposal.pdf) - our research proposal (the research question was adjusted afterwards, see the report)
- [Script busline remise assignment with comments.ipynb](Script%20busline%20remise%20assignment%20with%20comments.ipynb) - bus side: lines, depots, bus models, energy use and the night-charging check
- [Distribution of the busses in Utrecht.xlsx](Distribution%20of%20the%20busses%20in%20Utrecht.xlsx) - fleet file read by the bus script
- [notebooks](notebooks) - grid side, one notebook per step; begin with `00_overview_and_sources.ipynb`
- [congestion data](congestion%20data) - grid datasets read by the bus script
- [data](data) - `raw` (files Python cannot fetch), `backup` (offline copies of the open data), `processed` (our results)
- [src](src) - settings, web helpers and the charging model
- [figures](figures) - all charts

---

# Background and research question

Every city bus in Utrecht runs on a battery and is charged at one of three large depots. The regional grid that feeds
these depots is congested: new connections end up on a waiting list, and demand is highest between 16:00 and 20:00.
Buses that come back in the late afternoon and are plugged in at once add their charging to exactly that busy window,
competing with the homes and companies that were connected first. Moving the charging to quieter hours might give
those existing users more room, provided that every bus is still full before its next shift.

**Research question**

> How can the charging of Utrecht's electric buses be shifted to other moments, so that the original users of the grid
> around the bus depots are not restricted in their electricity use?

Our approach has three parts:
1. For the grid around each depot: find its capacity, its peak demand and the capacity others have requested (the queue).
2. For each depot: calculate how much energy its buses need, using the timetable and the fleet.
3. Test several charging strategies against the room that is left in the grid, for every hour.

We look at the three depots of the city network: **Westraven, Nieuwegein Remiseweg and Lage Weide**. They have
different fleets, different grid connections and grids that are full to different degrees, so the benefit of moving
the charging differs per depot as well.

---

# Study design

Each depot is treated as its own case, with its buses, its grid connection and the grid supply area (voedingsgebied)
that feeds it. Two parts of the project work together:
- **Grid side (notebooks):** hourly demand in each supply area for a whole year, plus four charging strategies.
- **Bus side (script):** lines, buses and energy per depot, and a check of whether charging at night fits.

### Assumptions we rely on

- Demand in a supply area has the same hourly shape as the **national demand of 2025**, scaled to the area's published peak.
- Capacity, peak and queue are the published figures for **2026**; demand does not grow between 2025 and 2026.
- Bus demand is based on a single weekday from the timetable: **4 November 2026**.
- A line is run from the depot with the **fewest empty kilometres**.
- In the night check, each bus is filled **from empty to full once**, evenly between **22:00 and 06:00** (an upper estimate).
- Westraven has a **10 MVA** connection (Statenvoorstel 2020MM80); for the other two depots we assume the same **71.4 kVA per bus**.

![Peak day per depot](figures/07_peak_day_load_queue_capacity.png)

*Figure 1 - On the busiest grid day: demand, demand plus queue, and capacity in each depot's supply area.*

### The three depots at a glance

| Depot | Supply area | Buses | Grid connection (MW) | Area capacity / peak (MW) | Used + queue | Night charging power (MW) |
|:------|:------------|:------|:---------------------|:--------------------------|:-------------|:--------------------------|
| **Westraven** | CM39 Nieuwegein (estimated) | 197 | 9.5 | 141 / 130 | 126.5% | 10.7 |
| **Nieuwegein Remiseweg** | CM10 Oudenrijn | 57 | 3.9 (assumed) | 45 / 39.1 | 100.2% | 3.4 |
| **Lage Weide** | CM60 Utrecht Lage Weide | 54 | 3.7 (assumed) | 360 / 310.8 | 94.1% | 2.5 |

*Buses* is the number of buses per depot in the bus team's line–depot file (308 in total), which the grid notebooks use.
*Used + queue* adds the capacity that others are waiting for to the peak demand and divides by the capacity. A value
above 100% means nothing is left: any MW the buses use at the peak is a MW that a waiting household or company cannot get.

### Charging strategies tested

- **S1 - Reference:** a bus starts charging at full power as soon as it is back at the depot.
- **S2 - Pause during the peak:** no charging from 16:00 to 20:00; full power again afterwards.
- **S3 - Night charging:** the charging is spread as flat as possible over 22:00 – 06:00.
- **S4 - Grid-aware charging:** nothing in the evening peak, the area peak is never raised, and the depot load is kept as flat as possible.

### What we found

- **Remiseweg:** with the queue included, the grid only exceeds its limit at the evening peak (100.2%). Night charging
  takes that hour away (99.5%), so here moving the charging is enough.
- **Westraven:** with the queue included, the limit is exceeded for most of the day; moving the charging lowers it only
  slightly (126.5% → 125.8%). In addition, filling every battery overnight within 8 hours needs 10.7 MW, more than the
  9.5 MW connection.
- **Lage Weide:** the grid keeps spare room throughout the day (94.1%).
- The way of shifting matters: only pausing during the peak (S2) produces a new, higher depot peak after 20:00,
  whereas spreading over the night (S3) or grid-aware charging (S4) avoids that.

---

# Data sources

Three sources are combined: grid capacity per area, the hourly national demand, and the bus timetable with the fleet.

### Capacity and queue per supply area - Netbeheer Nederland

Netbeheer Nederland, the umbrella organisation of the Dutch grid operators, runs the
[capacity map](https://capaciteitskaart.netbeheernederland.nl/). For each supply area it lists the transport capacity,
the capacity needed at the peak moment and the capacity requested by parties on the waiting list. The underlying data
can be exported as CSV ([export page](https://capaciteitskaart.netbeheernederland.nl/info/algemene-info/)); we use the
file `voedingsgebieden.csv`, which covers roughly 600 areas for 2026.

| Column | Meaning |
|:--------|:-------------|
| **voedingsgebied_id** | Code of the supply area, for example CM10 for Oudenrijn |
| **aanwezige_transportcapaciteit_afname** | Transport capacity for taking power from the grid (MW) |
| **benodigde_transportcapaciteit_afname** | Capacity required at the moment of the peak (MW) |
| **wachtrij_afname** | Capacity requested by parties on the waiting list (MW) |

A blank cell means the operator did not publish a figure; it is never read as zero.

### Hourly demand - ENTSO-E via Energy-Charts

Hourly demand is not published per supply area. We therefore take the national demand of the Netherlands from the
[Energy-Charts API](https://api.energy-charts.info/) (Fraunhofer ISE), which serves ENTSO-E data without an API key,
and scale that pattern to each area.

| Field | Meaning |
|:--------|:-------------|
| **unix_seconds** | Moment of each 15-minute value |
| **Load** | Electricity demand of the Netherlands (MW) |

### Timetable and fleet - GTFS and the bus team

Trips, routes and stop times come from the Dutch [GTFS feed](https://gtfs.ovapi.nl/nl/) (OVapi). The fleet per bus
model, with its energy use per km and battery size, was put together by the bus team from the
[OV in Nederland wiki](https://wiki.ovinnederland.nl/wiki/Concessie_Utrecht_Binnen_(2026-2035)) and manufacturer data.

| File | Used for |
|:--------|:-------------|
| **routes, trips, calendar_dates** | Which lines and trips run on the chosen day |
| **stop_times, shapes, stops** | Duration, length and first and last stop of each trip |
| **Distribution of the busses in Utrecht.xlsx** | Buses, kWh per km and battery capacity per model |

---

# From raw data to results

### Getting the data

The grid notebooks fetch the open data themselves: Python reads each file from its web address into memory and filters
it there, so no manual download is needed. When a source is offline, a stored copy in `data/backup` takes over. Files
that cannot be fetched (the bus team's fleet files) are kept in `data/raw`. The bus script needs the GTFS feed as an
unzipped folder and asks OpenStreetMap and OSRM for depot locations and road distances. The full GTFS feed is too large
for GitHub (stop_times alone is about 800 MB), so it is not included; see step 4 below.

### Processing steps and formulas

**Selecting our three areas**

Selecting our three areas from the national file happens in four filters (rows left after each step):

all areas (602) → Stedin (244) → province of Utrecht (47) → our depots (3)

**Estimating Westraven's capacity**

Westraven's area CM39 has no published capacity, so we derive it from Oudenrijn per postcode:

capacity CM39 = 3,287 postcodes × (45 MW ÷ 1,048 postcodes) ≈ 141 MW

and set its peak at 0.92 × capacity, the middle value of the Utrecht areas for which both numbers are known.

**Calculating hourly demand**

Hourly demand per area follows from the national series:

area demand(t) = national demand(t) × (area peak ÷ highest national demand of the year)

with `national demand(t)` the ENTSO-E value in hour *t* (MW) and `area peak` the published peak of the supply area (MW).

On the two daylight-saving days, the hour that does not exist is filled by linear interpolation and the hour that occurs twice is averaged.

**Calculating spare capacity**

The room that is left in each hour is then:

room(t) = capacity − area demand without the depot(t) − bus charging(t)

which gives, for every depot, the spare capacity in all 8,760 hours of the year.

### How to reproduce the results

1. Install Python 3.10 or newer and run `pip install -r requirements.txt`.
2. Execute the notebooks in `notebooks` in the order 00 → 05b, then 07, then 06 (or simply `python run_all.py`).
   Results go to `data/processed`, charts to `figures`.
3. In `src/config.py`, `LIVE = True` (the default) lets the notebooks download the newest open data themselves, including
   the GTFS feed (about 250 MB, read in memory); if a source is offline, the copy in `data/backup` is used. Numbers may
   then shift a little. Set `LIVE = False` to get exactly the numbers in this repository, without internet.
4. For the bus script, the GTFS feed is **not** downloaded automatically: download
   [gtfs-nl.zip](https://gtfs.ovapi.nl/nl/gtfs-nl.zip), unzip it into a folder `gtfs-nl` in the main folder of the
   repository and run all cells with an internet connection (for OpenStreetMap and OSRM). The fleet file and the `congestion data`
   folder are already next to the script.
5. The report `Group22_final_report.ipynb` only reads `data/processed` and `figures`, so it runs without internet.
