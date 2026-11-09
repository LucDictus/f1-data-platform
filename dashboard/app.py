import os

import duckdb
import streamlit as st

DB_PATH = os.path.join(os.environ.get("F1_DATA_DIR", "data"), "f1.duckdb")


@st.cache_data(ttl=600)
def query(sql: str, params: tuple = ()):
    # Open and close per query: an open connection locks the file and makes dbt build fail.
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(sql, list(params)).df()


st.title("F1 Data Platform")

st.header("Points per team")
points = query("""
    SELECT r.season::VARCHAR AS season, c.team_lineage AS team, SUM(r.points) AS points
    FROM marts.fct_race_results AS r
    JOIN marts.dim_constructor AS c ON r.constructor_id = c.constructor_id
    GROUP BY ALL
    ORDER BY season
""")
st.line_chart(points, x="season", y="points", color="team")

seasons = query("SELECT DISTINCT season FROM marts.dim_race ORDER BY season DESC")["season"]
season = st.selectbox("Season", seasons)

st.header("Average pit stop per team")
pits = query(
    """
    SELECT c.constructor_name AS team, ROUND(AVG(p.duration_s), 2) AS avg_stop_s
    FROM marts.fct_pit_stops AS p
    JOIN marts.dim_constructor AS c ON p.constructor_id = c.constructor_id
    WHERE p.season = ? AND NOT p.is_long_stop
    GROUP BY ALL
    ORDER BY avg_stop_s
""",
    (season,),
)
st.bar_chart(pits, x="team", y="avg_stop_s", horizontal=True)

st.header("Lap times in one race")
races = query(
    "SELECT round, race_name FROM marts.dim_race WHERE season = ? ORDER BY round", (season,)
)
race = st.selectbox("Race", races.itertuples(), format_func=lambda r: f"{r.round}. {r.race_name}")
laps = query(
    """
    WITH laps AS (
        SELECT d.driver_code AS driver, l.lap, l.lap_time_s
        FROM marts.fct_lap_times AS l
        JOIN marts.dim_driver AS d ON l.driver_id = d.driver_id
        WHERE l.season = ? AND l.round = ?
    )
    -- Drop red-flag and safety-car laps, which would flatten the chart.
    SELECT * FROM laps WHERE lap_time_s < 1.2 * (SELECT MEDIAN(lap_time_s) FROM laps)
""",
    (season, race.round),
)
if laps.empty:
    st.info("No lap times downloaded for this race yet.")
else:
    st.line_chart(laps, x="lap", y="lap_time_s", color="driver")
