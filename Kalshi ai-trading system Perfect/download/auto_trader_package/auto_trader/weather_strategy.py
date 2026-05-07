"""
Kalshi Weather Strategy — Exploits mispriced weather event contracts.

Weather markets are among the most profitable on Kalshi because:
1. Markets often lag behind updated NWS/NOAA forecasts
2. Historical baseline data (e.g., "average temp on this date") is freely available
3. Human intuition about weather is systematically biased
4. Low-volume markets have thinner competition

Data Sources (priority order):
  1. Meteostat — Professional-grade historical & recent weather observations
     - Station-based actual observations (not model reanalysis)
     - Climate normals with 10-30 year lookback
     - Hourly/daily data for precise date matching
  2. NWS/NOAA — US government forecasts (most reliable for US locations)
  3. Open-Meteo — Global forecast + historical archive (fallback)

Strategy:
- Fetch latest forecasts + historical observations for market locations
- Calculate fair probability from forecast data blended with meteostat observations
- Compare to Kalshi market price
- Trade when edge > minimum EV threshold (e.g., 10¢)
"""

import json
import re
from datetime import datetime, timezone, timedelta, date
from typing import Dict, List, Optional, Tuple

import requests

# Lazy-import pandas only when needed (for Meteostat data processing)
try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    _PANDAS_AVAILABLE = False

from .market_scanner import MarketScanner, MarketInfo
from .ev_analyzer import EVAnalyzer, TradeRecommendation


# ── API Endpoints ─────────────────────────────────────────────────────

NWS_API_BASE = "https://api.weather.gov"
OPEN_METEO_BASE = "https://api.open-meteo.com/v1"

# Meteostat availability flag — graceful fallback if not installed
_METEOSTAT_AVAILABLE = False
try:
    import meteostat
    _METEOSTAT_AVAILABLE = True
except ImportError:
    pass


def _suppress_meteostat_warnings():
    """
    Context manager to suppress Meteostat's noisy CDN download warnings.

    Meteostat prints messages like:
      "Warning: Cannot load daily/2016/KFFZ0.csv.gz from https://data.meteostat.net/"

    These are normal — not all weather stations have data for all years/dates.
    We suppress them to keep the console output clean.
    """
    import sys
    import io

    class _SuppressOutput:
        def __enter__(self):
            self._original_stderr = sys.stderr
            sys.stderr = io.StringIO()
            return self

        def __exit__(self, *args):
            sys.stderr = self._original_stderr

    return _SuppressOutput()


# ── Weather Data Fetcher ──────────────────────────────────────────────

class WeatherDataFetcher:
    """
    Multi-source weather data fetcher with Meteostat as primary source.

    Data source priority:
      1. Meteostat — historical observations + recent actuals (highest quality)
      2. NWS — US government forecasts
      3. Open-Meteo — global forecasts + historical archive (fallback)

    Meteostat advantages over Open-Meteo for historical data:
      - Station-based ACTUAL observations (not model reanalysis)
      - More precise for specific cities/locations
      - Better quality control and gap filling
      - Longer historical records available
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KalshiWeatherBot/2.0 (weather-research@example.com)",
            "Accept": "application/json",
        })
        self._meteostat_cache: Dict[str, any] = {}

    # ── Meteostat: Historical Observations ─────────────────────────────

    def _find_nearest_station(self, latitude: float, longitude: float, max_tries: int = 3) -> Optional[str]:
        """
        Find the nearest Meteostat weather station to given coordinates.

        Works with both meteostat v1 and v2 APIs.
        Tries up to max_tries stations in case the closest one has no data.
        Returns station_id string, or None on failure.
        """
        try:
            import meteostat as ms

            nearby_df = None

            # Try v2 API first (Point-based)
            try:
                from meteostat import Point
                point = Point(latitude, longitude)
                nearby_df = ms.stations.nearby(point)
            except (ImportError, AttributeError, TypeError):
                pass

            # Try v1 API fallback (Stations class)
            if nearby_df is None or (hasattr(nearby_df, 'empty') and nearby_df.empty):
                try:
                    from meteostat import Stations
                    stations = Stations()
                    stations = stations.nearby(latitude, longitude)
                    nearby_df = stations.fetch(max_tries)
                except (ImportError, AttributeError, TypeError):
                    pass

            if nearby_df is None or (hasattr(nearby_df, 'empty') and nearby_df.empty):
                return None

            # Return the closest station (first row)
            # If it doesn't have data, caller can try the next ones
            return nearby_df.index[0]

        except Exception as e:
            return None

    def _fetch_meteostat_daily(self, station_id: str, start, end) -> Optional["pd.DataFrame"]:
        """
        Fetch daily weather data from Meteostat for a station.

        Works with both meteostat v1 and v2 APIs.
        start/end are converted to pd.Timestamp for pandas compatibility,
        which fixes the 'Invalid comparison between dtype=datetime64[ns] and date'
        error that occurs on Python 3.10 with pandas 2.x.

        Returns a pandas DataFrame, or None on failure.
        """
        try:
            import meteostat as ms

            # Convert start/end to pd.Timestamp for pandas datetime64[ns] compatibility
            # This fixes: "Invalid comparison between dtype=datetime64[ns] and date"
            if _PANDAS_AVAILABLE and pd is not None:
                try:
                    start = pd.Timestamp(start)
                    end = pd.Timestamp(end)
                except Exception:
                    pass  # Fall through to use as-is

            # Try v2 API first (meteostat.daily function)
            try:
                ts = ms.daily(station_id, start, end)
                with _suppress_meteostat_warnings():
                    df = ts.fetch()
                if df is not None and not df.empty:
                    return df
            except (TypeError, AttributeError):
                pass

            # Try v1 API fallback (Daily class)
            try:
                from meteostat import Daily
                data = Daily(station_id, start, end)
                with _suppress_meteostat_warnings():
                    df = data.fetch()
                if df is not None and not df.empty:
                    return df
            except (ImportError, AttributeError, TypeError):
                pass

            return None

        except Exception as e:
            return None

    def get_meteostat_daily(
        self,
        latitude: float,
        longitude: float,
        start,
        end,
    ) -> Optional[Dict]:
        """
        Get actual daily weather observations from Meteostat.

        Returns observed high/low temps, precipitation, wind speed for
        the specified date range. Uses nearest weather station with data.

        This is REAL observational data, not model reanalysis — making it
        the most reliable source for historical baselines.

        Note: start/end should be datetime objects (not date) for pandas compatibility.

        Returns dict with keys: avg_high, avg_low, avg_precip, avg_wind,
        sample_days, station_id, or None on failure.
        """
        if not _METEOSTAT_AVAILABLE:
            return None

        try:
            station_id = self._find_nearest_station(latitude, longitude)
            if not station_id:
                return None

            df = self._fetch_meteostat_daily(station_id, start, end)
            if df is None or df.empty:
                return None

            # Flatten multi-index if present (v2 returns station,time,source)
            if isinstance(df.index, pd.MultiIndex):
                df = df.droplevel([0, 2])  # Drop station and source levels, keep time

            # Calculate averages from actual observations
            result = {
                "avg_high": safe_float_mean(df, "tmax"),
                "avg_low": safe_float_mean(df, "tmin"),
                "avg_precip": safe_float_mean(df, "prcp"),
                "avg_wind": safe_float_mean(df, "wspd"),
                "sample_days": len(df),
                "station_id": station_id,
            }

            # Convert from Celsius to Fahrenheit (Meteostat uses Celsius)
            if result["avg_high"] is not None:
                result["avg_high_f"] = result["avg_high"] * 9/5 + 32
            if result["avg_low"] is not None:
                result["avg_low_f"] = result["avg_low"] * 9/5 + 32

            return result

        except Exception as e:
            print(f"[Weather] Meteostat daily fetch error: {e}")
            return None

    def get_meteostat_recent(
        self,
        latitude: float,
        longitude: float,
        days_back: int = 5,
    ) -> Optional[Dict]:
        """
        Get recent actual weather observations from Meteostat.

        This provides REALITY CHECK data — what actually happened at
        this location in the past few days. Useful for:
          - Verifying forecast accuracy
          - Understanding current weather trends
          - Detecting anomalous conditions

        Returns dict with recent daily observations, or None on failure.
        """
        if not _METEOSTAT_AVAILABLE:
            return None

        try:
            # Use pd.Timestamp for pandas datetime64[ns] compatibility
            # Fixes: "Invalid comparison between dtype=datetime64[ns] and date"
            end = datetime.now() - timedelta(days=1)  # Yesterday
            start = end - timedelta(days=days_back)

            # Convert to pd.Timestamp explicitly for meteostat/pandas compatibility
            if _PANDAS_AVAILABLE and pd is not None:
                end = pd.Timestamp(end)
                start = pd.Timestamp(start)

            station_id = self._find_nearest_station(latitude, longitude)
            if not station_id:
                return None

            df = self._fetch_meteostat_daily(station_id, start, end)

            # If nearest station has no recent data, try to find another station
            # by looking at nearby stations and testing them
            if df is None or df.empty:
                try:
                    import meteostat as ms
                    from meteostat import Point
                    point = Point(latitude, longitude)
                    nearby = ms.stations.nearby(point)
                    if nearby is not None and not nearby.empty:
                        for alt_station_id in nearby.index[1:4]:  # Try next 3 stations
                            df = self._fetch_meteostat_daily(alt_station_id, start, end)
                            if df is not None and not df.empty:
                                station_id = alt_station_id
                                break
                except Exception:
                    pass

            if df is None or df.empty:
                return None

            # Flatten multi-index if present (v2 returns station,time,source)
            if isinstance(df.index, pd.MultiIndex):
                df = df.droplevel([0, 2])  # Drop station and source levels, keep time

            # Ensure index is datetime64 for safe .date() access
            if _PANDAS_AVAILABLE and pd is not None:
                if not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index)
                    except Exception:
                        pass

            # Extract recent observations
            recent_days = []
            for idx, row in df.iterrows():
                day_data = {
                    "date": str(idx.date()) if hasattr(idx, 'date') else str(idx),
                    "high_f": safe_c_to_f(row, "tmax"),
                    "low_f": safe_c_to_f(row, "tmin"),
                    "precip_mm": safe_float(row, "prcp"),
                    "wind_kph": safe_float(row, "wspd"),
                }
                recent_days.append(day_data)

            valid_highs = [d["high_f"] for d in recent_days if d["high_f"] is not None]
            valid_lows = [d["low_f"] for d in recent_days if d["low_f"] is not None]

            return {
                "station_id": station_id,
                "days": recent_days,
                "avg_high_f": sum(valid_highs) / len(valid_highs) if valid_highs else None,
                "avg_low_f": sum(valid_lows) / len(valid_lows) if valid_lows else None,
            }

        except Exception as e:
            print(f"[Weather] Meteostat recent fetch error: {e}")
            return None

    def get_meteostat_climate_normals(
        self,
        latitude: float,
        longitude: float,
        month: int,
        day: int,
        years_back: int = 10,
    ) -> Optional[Dict]:
        """
        Get climate normals for a specific date using Meteostat.

        Returns the average weather conditions on this calendar date
        over the past N years. More accurate than Open-Meteo archive
        because it uses station observations, not model data.

        Returns dict: avg_high_f, avg_low_f, avg_precip, sample_years, station_id
        """
        if not _METEOSTAT_AVAILABLE:
            return None

        try:
            this_year = date.today().year
            # Use pd.Timestamp for pandas datetime64[ns] compatibility
            # Fixes: "Invalid comparison between dtype=datetime64[ns] and date"
            start = pd.Timestamp(year=this_year - years_back, month=month, day=day) if _PANDAS_AVAILABLE and pd else datetime(this_year - years_back, month, day)
            end = pd.Timestamp(year=this_year - 1, month=month, day=day) if _PANDAS_AVAILABLE and pd else datetime(this_year - 1, month, day)

            station_id = self._find_nearest_station(latitude, longitude)
            if not station_id:
                return None

            df = self._fetch_meteostat_daily(station_id, start, end)
            if df is None or df.empty:
                return None

            # Flatten multi-index if present (v2 returns station,time,source)
            if isinstance(df.index, pd.MultiIndex):
                df = df.droplevel([0, 2])  # Drop station and source levels, keep time

            # Ensure index is DatetimeIndex before using .month/.day accessors
            # This prevents "Invalid comparison between dtype=datetime64[ns] and date"
            if _PANDAS_AVAILABLE and pd is not None:
                if not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index)
                    except Exception:
                        pass

            # Filter to only rows matching the target month/day
            matching = df[
                (df.index.month == month) & (df.index.day == day)
            ]

            if matching.empty:
                # Fallback: use same week (±3 days) for more data points
                matching = df[
                    (df.index.month == month) &
                    (df.index.day >= max(1, day - 3)) &
                    (df.index.day <= min(28, day + 3))
                ]

            if matching.empty:
                return None

            # Calculate averages from Celsius observations
            avg_high_c = safe_float_mean(matching, "tmax")
            avg_low_c = safe_float_mean(matching, "tmin")
            avg_precip = safe_float_mean(matching, "prcp")

            result = {
                "avg_high_f": avg_high_c * 9/5 + 32 if avg_high_c is not None else None,
                "avg_low_f": avg_low_c * 9/5 + 32 if avg_low_c is not None else None,
                "avg_precip": avg_precip,
                "sample_years": len(matching),
                "station_id": station_id,
            }

            return result

        except Exception as e:
            print(f"[Weather] Meteostat climate normals error: {e}")
            return None

    # ── NWS Forecast ──────────────────────────────────────────────────

    def get_nws_forecast(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get NWS forecast for a location.

        NWS workflow: point -> grid -> forecast URL -> forecast data
        """
        try:
            point_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
            resp = self.session.get(point_url, timeout=10)
            if resp.status_code != 200:
                return None

            point_data = resp.json()
            forecast_url = point_data.get("properties", {}).get("forecast")
            if not forecast_url:
                return None

            resp = self.session.get(forecast_url, timeout=10)
            if resp.status_code != 200:
                return None

            return resp.json()

        except Exception as e:
            print(f"[Weather] NWS fetch error: {e}")
            return None

    def get_nws_hourly(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get NWS hourly forecast for more granular data."""
        try:
            point_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
            resp = self.session.get(point_url, timeout=10)
            if resp.status_code != 200:
                return None

            point_data = resp.json()
            hourly_url = point_data.get("properties", {}).get("forecastHourly")
            if not hourly_url:
                return None

            resp = self.session.get(hourly_url, timeout=10)
            if resp.status_code != 200:
                return None

            return resp.json()

        except Exception as e:
            print(f"[Weather] NWS hourly fetch error: {e}")
            return None

    # ── Open-Meteo Forecast (Fallback) ─────────────────────────────────

    def get_open_meteo(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> Optional[Dict]:
        """
        Get Open-Meteo forecast (global, no API key needed).

        Returns temperature, precipitation, wind speed, etc.
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                         "windspeed_10m_max,weathercode",
                "hourly": "temperature_2m,precipitation,windspeed_10m",
                "forecast_days": forecast_days,
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
            }
            resp = self.session.get(
                f"{OPEN_METEO_BASE}/forecast", params=params, timeout=10
            )
            if resp.status_code != 200:
                return None
            return resp.json()

        except Exception as e:
            print(f"[Weather] Open-Meteo fetch error: {e}")
            return None

    # ── Historical Baseline (Open-Meteo Fallback) ──────────────────────

    def get_historical_baseline(
        self,
        latitude: float,
        longitude: float,
        month: int,
        day: int,
    ) -> Optional[Dict]:
        """
        Get historical weather norms for a date.

        Uses Meteostat first (station observations), falls back to
        Open-Meteo's historical API if Meteostat is unavailable.
        """
        # Try Meteostat first (real station observations)
        if _METEOSTAT_AVAILABLE:
            normals = self.get_meteostat_climate_normals(latitude, longitude, month, day)
            if normals and normals.get("avg_high_f") is not None:
                return {
                    "avg_high": normals["avg_high_f"],
                    "avg_low": normals["avg_low_f"],
                    "avg_precip": normals.get("avg_precip"),
                    "sample_years": normals.get("sample_years", 0),
                    "source": "meteostat",
                    "station_id": normals.get("station_id"),
                }

        # Fallback to Open-Meteo archive
        try:
            this_year = datetime.now().year
            start_date = f"{this_year - 10}-{month:02d}-{day:02d}"
            end_date = f"{this_year - 1}-{month:02d}-{day:02d}"

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
            }
            resp = self.session.get(
                f"{OPEN_METEO_BASE}/archive", params=params, timeout=15
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            daily = data.get("daily", {})

            max_temps = [t for t in daily.get("temperature_2m_max", []) if t is not None]
            min_temps = [t for t in daily.get("temperature_2m_min", []) if t is not None]
            precip = [p for p in daily.get("precipitation_sum", []) if p is not None]

            return {
                "avg_high": sum(max_temps) / len(max_temps) if max_temps else None,
                "avg_low": sum(min_temps) / len(min_temps) if min_temps else None,
                "avg_precip": sum(precip) / len(precip) if precip else None,
                "sample_years": len(max_temps),
                "source": "open-meteo",
            }

        except Exception as e:
            print(f"[Weather] Historical baseline fetch error: {e}")
            return None


# ── Location Parsing ───────────────────────────────────────────────────

# Common US cities for Kalshi weather markets
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "new york": (40.7128, -74.0060),
    "nyc": (40.7128, -74.0060),
    "ny": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "lax": (34.0522, -118.2437),
    "la": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "chi": (41.8781, -87.6298),
    "houston": (29.7604, -95.3698),
    "hou": (29.7604, -95.3698),
    "phoenix": (33.4484, -112.0740),
    "phx": (33.4484, -112.0740),
    "philadelphia": (39.9526, -75.1652),
    "san antonio": (29.4241, -98.4936),
    "san diego": (32.7157, -117.1611),
    "dallas": (32.7767, -96.7970),
    "dal": (32.7767, -96.7970),
    "miami": (25.7617, -80.1918),
    "mia": (25.7617, -80.1918),
    "atlanta": (33.7490, -84.3880),
    "atl": (33.7490, -84.3880),
    "boston": (42.3601, -71.0589),
    "bos": (42.3601, -71.0589),
    "denver": (39.7392, -104.9903),
    "den": (39.7392, -104.9903),
    "seattle": (47.6062, -122.3321),
    "sea": (47.6062, -122.3321),
    "washington": (38.9072, -77.0369),
    "dc": (38.9072, -77.0369),
    "detroit": (42.3314, -83.0458),
    "minneapolis": (44.9778, -93.2650),
    "nashville": (36.1627, -86.7816),
    "portland": (45.5152, -122.6784),
    "las vegas": (36.1699, -115.1398),
    "austin": (30.2672, -97.7431),
    "orlando": (28.5383, -81.3792),
    "tampa": (27.9506, -82.4572),
    "salt lake city": (40.7608, -111.8910),
    "raleigh": (35.7796, -78.6382),
    "kansas city": (39.0997, -94.5786),
    "st louis": (38.6270, -90.1994),
    "baltimore": (39.2904, -76.6122),
    "charlotte": (35.2271, -80.8431),
    "san francisco": (37.7749, -122.4194),
    "sf": (37.7749, -122.4194),
    "pittsburgh": (40.4406, -79.9959),
    "cincinnati": (39.1031, -84.5120),
    "cleveland": (41.4993, -81.6944),
    "indianapolis": (39.7684, -86.1581),
    "columbus": (39.9612, -82.9988),
    "memphis": (35.1495, -90.0490),
    "milwaukee": (43.0389, -87.9065),
    "albuquerque": (35.0844, -106.6504),
    "tucson": (32.2226, -110.9747),
    "fresno": (36.7378, -119.7871),
    "sacramento": (38.5816, -121.4944),
    "mesa": (33.4152, -111.8315),
    "omaha": (41.2565, -95.9345),
    "oklahoma city": (35.4676, -97.5164),
    "jacksonville": (30.3322, -81.6557),
    "el paso": (31.7619, -106.4850),
    "louisville": (38.2527, -85.7585),
    "richmond": (37.5407, -77.4360),
    "buffalo": (42.8864, -78.8784),
    "rochester": (43.1566, -77.6088),
    "birmingham": (33.5207, -86.8025),
    "honolulu": (21.3069, -157.8583),
    "anchorage": (61.2181, -149.9003),
    "fairbanks": (64.8378, -147.7164),
}

# US States — map state names to approximate geographic center coordinates
# These are used when a market references a state rather than a city
# (e.g., "Will there be an earthquake in California?")
STATE_COORDS: Dict[str, Tuple[float, float]] = {
    "alabama": (32.8067, -86.7911),
    "alaska": (61.3707, -152.4044),
    "arizona": (33.7298, -111.4312),
    "arkansas": (34.9697, -92.3731),
    "california": (36.1162, -119.6816),
    "colorado": (39.0598, -105.3111),
    "connecticut": (41.5978, -72.7554),
    "delaware": (39.3185, -75.5071),
    "florida": (27.7663, -81.6868),
    "georgia": (33.0406, -83.6431),
    "hawaii": (21.0943, -157.4983),
    "idaho": (44.2405, -114.4788),
    "illinois": (40.3495, -88.9861),
    "indiana": (39.8494, -86.2583),
    "iowa": (42.0115, -93.2105),
    "kansas": (38.5266, -96.7265),
    "kentucky": (37.6681, -84.6701),
    "louisiana": (31.1695, -91.8678),
    "maine": (44.6939, -69.3819),
    "maryland": (39.0639, -76.8021),
    "massachusetts": (42.2302, -71.5301),
    "michigan": (43.3266, -84.5361),
    "minnesota": (45.6945, -93.9002),
    "mississippi": (32.7416, -89.6787),
    "missouri": (38.4561, -92.2884),
    "montana": (46.9219, -110.4544),
    "nebraska": (41.1254, -98.2681),
    "nevada": (38.3135, -117.0554),
    "new hampshire": (43.4525, -71.5639),
    "new jersey": (40.2989, -74.5210),
    "new mexico": (34.8405, -106.2485),
    "new york state": (42.1657, -74.9481),
    "north carolina": (35.6301, -79.8064),
    "north dakota": (47.5289, -99.7840),
    "ohio": (40.3888, -82.7649),
    "oklahoma": (35.5653, -96.9289),
    "oregon": (44.5720, -122.0709),
    "pennsylvania": (40.5908, -77.2098),
    "rhode island": (41.6809, -71.5118),
    "south carolina": (33.8569, -80.9450),
    "south dakota": (44.2998, -99.4388),
    "tennessee": (35.7478, -86.6923),
    "texas": (31.0545, -97.5635),
    "utah": (40.1500, -111.8624),
    "vermont": (44.2253, -72.5803),
    "virginia": (37.7693, -78.1700),
    "washington state": (47.4009, -121.4905),
    "west virginia": (38.5976, -80.4549),
    "wisconsin": (44.2685, -89.6165),
    "wyoming": (42.7559, -107.3025),
}

# State abbreviations → full names mapping
STATE_ABBREV: Dict[str, str] = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas",
    "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware",
    "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho",
    "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas",
    "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
    "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada",
    "nh": "new hampshire", "nj": "new jersey", "nm": "new mexico",
    "ny": "new york", "nc": "north carolina", "nd": "north dakota",
    "oh": "ohio", "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania",
    "ri": "rhode island", "sc": "south carolina", "sd": "south dakota",
    "tn": "tennessee", "tx": "texas", "ut": "utah", "vt": "vermont",
    "va": "virginia", "wa": "washington", "wv": "west virginia",
    "wi": "wisconsin", "wy": "wyoming", "dc": "district of columbia",
}

# Special market types that don't need city-level location
# These map to broad regions or use special handling
SPECIAL_REGION_COORDS: Dict[str, Tuple[float, float]] = {
    "world": (0.0, 0.0),          # Global — no specific location
    "global": (0.0, 0.0),
    "us": (39.8283, -98.5795),     # Geographic center of contiguous US
    "usa": (39.8283, -98.5795),
    "united states": (39.8283, -98.5795),
    "conus": (39.8283, -98.5795),
    "gulf coast": (29.0, -90.0),
    "east coast": (38.0, -77.0),
    "west coast": (38.0, -122.0),
    "midwest": (41.0, -89.0),
    "south": (33.0, -90.0),
    "northeast": (42.0, -73.0),
    "pacific northwest": (46.0, -122.0),
    "great plains": (41.0, -100.0),
}

# Market type classification keywords
# Used to determine what kind of weather market this is beyond temperature/precip
EARTHQUAKE_KEYWORDS = ["earthquake", "magnitude", "seismic", "tremor"]
VOLCANO_KEYWORDS = ["volcano", "eruption", "supervolcano", "volcanic"]
HURRICANE_KEYWORDS = ["hurricane", "tropical storm", "tropical cyclone", "cyclone", "typhoon"]
TORNADO_KEYWORDS = ["tornado", "tornadoes", "twister"]
WILDFIRE_KEYWORDS = ["wildfire", "wild fire", "forest fire", "fire season"]
DROUGHT_KEYWORDS = ["drought", "water level", "reservoir"]
CLIMATE_CHANGE_KEYWORDS = ["pre-industrial", "2 degrees", "1.5 degrees", "carbon", "co2", "climate"]


def parse_location(text: str) -> Optional[Tuple[float, float]]:
    """
    Extract location from market title and return coordinates.

    Handles:
    - City names (e.g., "highest temperature in NYC")
    - State names (e.g., "earthquake in California")
    - State abbreviations (e.g., "in CA")
    - Special regions (e.g., "Gulf Coast")
    - Global/world references
    """
    text_lower = text.lower()

    # 1. Try city name matching first (most specific)
    # Sort by length (longest first) to avoid partial matches
    # e.g., "san francisco" before "san"
    sorted_cities = sorted(CITY_COORDS.keys(), key=len, reverse=True)
    for city in sorted_cities:
        if city in text_lower:
            return CITY_COORDS[city]

    # 2. Try state name matching
    sorted_states = sorted(STATE_COORDS.keys(), key=len, reverse=True)
    for state in sorted_states:
        if state in text_lower:
            return STATE_COORDS[state]

    # 3. Try state abbreviation (look for "in CA", "in TX", etc.)
    abbrev_match = re.search(r'\bin\s+([A-Z]{2})\b', text)
    if abbrev_match:
        abbrev = abbrev_match.group(1).lower()
        if abbrev in STATE_ABBREV:
            state_name = STATE_ABBREV[abbrev]
            if state_name in STATE_COORDS:
                return STATE_COORDS[state_name]

    # 4. Try special regions
    for region, coords in SPECIAL_REGION_COORDS.items():
        if region in text_lower:
            return coords

    # 5. Try to extract any capitalized location name after "in"
    # Pattern: "in CityName" or "in StateName"
    in_match = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    if in_match:
        location_name = in_match.group(1).lower()
        # Check against our databases
        if location_name in CITY_COORDS:
            return CITY_COORDS[location_name]
        if location_name in STATE_COORDS:
            return STATE_COORDS[location_name]

    return None


def classify_market_type(text: str) -> str:
    """
    Classify the type of weather/climate market.

    Returns one of:
    - "temperature" — temp threshold markets
    - "precipitation" — rain/snow markets
    - "earthquake" — seismic activity
    - "volcano" — volcanic eruptions
    - "hurricane" — tropical cyclones
    - "tornado" — tornado markets
    - "wildfire" — fire markets
    - "drought" — drought/water level
    - "climate_change" — global warming/climate change
    - "generic" — unclassified weather market
    """
    text_lower = text.lower()

    # Check specific types in order of specificity
    for kw in EARTHQUAKE_KEYWORDS:
        if kw in text_lower:
            return "earthquake"
    for kw in VOLCANO_KEYWORDS:
        if kw in text_lower:
            return "volcano"
    for kw in HURRICANE_KEYWORDS:
        if kw in text_lower:
            return "hurricane"
    for kw in TORNADO_KEYWORDS:
        if kw in text_lower:
            return "tornado"
    for kw in WILDFIRE_KEYWORDS:
        if kw in text_lower:
            return "wildfire"
    for kw in DROUGHT_KEYWORDS:
        if kw in text_lower:
            return "drought"
    for kw in CLIMATE_CHANGE_KEYWORDS:
        if kw in text_lower:
            return "climate_change"

    # Temperature markets
    if any(kw in text_lower for kw in ["temperature", "temp", "degree", "hot", "cold", "warm",
                                        "freez", "frost", "heat"]):
        return "temperature"
    if parse_temperature_threshold(text) is not None:
        return "temperature"

    # Precipitation markets
    if any(kw in text_lower for kw in ["rain", "snow", "precip", "inch of", "storm",
                                        "blizzard", "sleet", "hail"]):
        return "precipitation"

    # Wind markets
    if any(kw in text_lower for kw in ["wind", "gust", "hurrican"]):
        return "hurricane"  # Usually hurricane-related

    return "generic"


def is_actual_weather_market(market: MarketInfo) -> bool:
    """
    Check if a market is a genuine weather/climate market.

    Kalshi's "Climate and Weather" group sometimes contains sports markets,
    cross-category events, and other non-weather content that shouldn't be
    analyzed with weather data. This filter catches those false positives.

    IMPORTANT: This filter was rewritten to fix over-aggressive filtering
    that was rejecting ALL 50 weather markets. The old filter had several bugs:
    1. Subtitle pattern "yes Name1, yes Name2" caught hurricane/storm name lists
    2. Sports keywords like "match", "quarter" appeared in weather titles
    3. Regex patterns ("above .*°") used as literal strings with `in` operator
    4. Negative checks ran BEFORE positive checks (rejection beat acceptance)
    5. No ticker-based positive identification for known weather tickers

    New priority order (positive signals FIRST, ticker rejection BEFORE text):
      1. Known weather ticker prefix -> auto-accept
      2. Known non-weather ticker prefix -> auto-reject (BEFORE text checks!)
      3. Weather indicators in text -> auto-accept
      4. Weather regex patterns in text -> auto-accept
      5. Sports-specific keywords -> reject (if no weather signal from steps 1-4)
      6. Sports subtitle pattern (proper nouns only) -> reject
      7. classify_market_type non-generic -> auto-accept
      8. Location found -> accept
      9. Default -> reject

    Returns True if this is a genuine weather/climate market.
    """
    ticker = market.ticker.upper()
    title = market.title.lower()
    subtitle = (market.subtitle or "").lower()
    combined = title + " " + subtitle

    # ══════════════════════════════════════════════════════════════════
    # STEP 1: Known weather ticker prefixes -> AUTO-ACCEPT
    # ══════════════════════════════════════════════════════════════════
    # These are well-known Kalshi weather ticker patterns. If the ticker
    # matches any of these, it's DEFINITELY a weather market — no need
    # to check anything else.
    WEATHER_TICKER_PREFIXES = [
        "KXHIGH",     # High temperature (KXHIGHNY, KXHIGHLAX, KXHIGHTBOS, etc.)
        "KXLLOW",     # Low temperature (KXLLOWNY, KXLLOWCHI, etc.)
        "KXRAIN",     # Rain markets (KXRAINNY, KXRAINLAX, etc.)
        "KXSNOW",     # Snow markets (KXSNOWDEN, KXSNOWCHI, etc.)
        "KXHURR",     # Hurricane markets
        "KXEQK",      # Earthquake markets
        "KXVOL",      # Volcano markets
        "KXTORN",     # Tornado markets (if exists)
        "KXWIND",     # Wind markets (if exists)
        "KXFLOOD",    # Flood markets (if exists)
        "KXWILD",     # Wildfire markets (if exists)
        "KXDRGT",     # Drought markets (if exists)
        "KXTEMP",     # Temperature (generic)
        "KXCLIM",     # Climate markets
        "KXNEXT",     # Named storm markets (KXNEXTROMANIAPM, etc.)
        "XRAIN",      # Rain variant
        "XHIGH",      # High temp variant
        "XLOW",       # Low temp variant
        "XSNOW",      # Snow variant
    ]
    for prefix in WEATHER_TICKER_PREFIXES:
        if ticker.startswith(prefix):
            return True

    # ══════════════════════════════════════════════════════════════════
    # STEP 2: Known non-weather ticker prefixes -> AUTO-REJECT
    # ══════════════════════════════════════════════════════════════════
    # CRITICAL: This MUST come BEFORE text-based acceptance (Steps 3-4).
    # Sports/cross-category markets often have titles containing weather-
    # adjacent words like "storm", "heat", "wind", "ice" which would
    # cause false acceptance if text checks ran first.
    #
    # The ticker is the MOST RELIABLE signal — if it says KXMVESPORTS*,
    # it's NOT weather, regardless of what the title says.
    NON_WEATHER_TICKER_PREFIXES = [
        "KXMVESPORTS",                   # Sports multi-game markets
        "KXMVECROSSCATEGORY",            # Cross-category (not pure weather)
        "KXMVE",                         # Multi-event (sports, entertainment)
        "KXNBA",                         # NBA basketball
        "KXNFL",                         # NFL football
        "KXMLB",                         # MLB baseball
        "KXNHL",                         # NHL hockey
        "KXNASCAR",                      # NASCAR racing
        "KXSOCCER",                      # Soccer
        "KXMMA",                         # MMA fighting
        "KXGOLF",                        # Golf
        "KXTENNIS",                      # Tennis
    ]
    for prefix in NON_WEATHER_TICKER_PREFIXES:
        if ticker.startswith(prefix):
            return False

    # ══════════════════════════════════════════════════════════════════
    # STEP 3: Weather indicator keywords -> AUTO-ACCEPT
    # ══════════════════════════════════════════════════════════════════
    # These are strong signals that a market is about weather/climate.
    # Only reached if the ticker is NOT a known weather or non-weather prefix.
    WEATHER_INDICATORS = [
        # Temperature
        "temperature", "temp", "degree", "°f", "°c", "celsius", "fahrenheit",
        "highest temp", "lowest temp", "high of", "low of",
        "record high", "record low", "all-time high", "all-time low",
        # Precipitation
        "rain", "snow", "precip", "inches of rain", "inches of snow",
        "rainfall", "snowfall", "precipitation",
        # Severe weather
        "hurricane", "tornado", "earthquake", "volcano", "eruption",
        "flood", "drought", "wildfire", "storm", "wind", "frost",
        "heat wave", "cold snap", "blizzard", "ice", "sleet", "hail",
        "tropical storm", "tropical cyclone", "cyclone", "typhoon",
        "seismic", "magnitude", "tremor", "supervolcano", "volcanic",
        # General climate
        "weather", "climate", "fire season", "forest fire",
        "water level", "reservoir", "gust",
    ]
    for indicator in WEATHER_INDICATORS:
        if indicator in combined:
            return True

    # ══════════════════════════════════════════════════════════════════
    # STEP 4: Weather regex patterns -> AUTO-ACCEPT
    # ══════════════════════════════════════════════════════════════════
    # These patterns use actual regex matching (not `in` operator).
    # The old code put regex patterns in a list checked with `in`, which
    # only matched the literal string "above .*°" — never actual temps.
    # NOTE: These patterns must be SPECIFIC to temperature to avoid
    # false positives. "over 200" could be sports points, not degrees.
    # We require explicit temperature context: °F, °C, "degrees", or
    # temperature keywords (temp/temperature) nearby.
    WEATHER_REGEX_PATTERNS = [
        # Explicit degree symbols (very high confidence)
        r"\d+\s*[°˚]\s*[fFcC]",                    # "90°F", "32°C"
        r"\d+\s+degrees?\s*[fF]?",                  # "90 degrees", "90 degrees F"
        r"\d+\+\s*(°|degrees?|f|fahrenheit)",       # "90+°", "90+ degrees"
        # "above/below" + number + degree indicator
        r"above\s+\d+\s*[°˚]",                      # "above 90°"
        r"below\s+\d+\s*[°˚]",                      # "below 32°"
        r"above\s+\d+\s+degrees?",                   # "above 90 degrees"
        r"below\s+\d+\s+degrees?",                   # "below 32 degrees"
        # "exceeds" is weather-specific (not used in sports)
        r"exceeds?\s+\d+\s*(?:°|degrees?|f\b)?",    # "exceed 90°", "exceed 90 degrees"
        # "higher/lower than" with number (weather phrasing)
        r"higher\s+than\s+\d+",                      # "higher than 80"
        r"lower\s+than\s+\d+",                       # "lower than 20"
        # "high/low" + location (temperature markets)
        r"high(?:est)?\s+(?:temp|temperature)?\s*(?:in|for|at)",  # "high in NYC"
        r"low(?:est)?\s+(?:temp|temperature)?\s*(?:in|for|at)",   # "low in Chicago"
        # Number + °F or °C with above/below/over/under prefix
        r"(?:above|below|over|under)\s+\d+\s*[°˚]\s*[fFcC]",    # "above 90°F"
    ]
    for pattern in WEATHER_REGEX_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return True

    # ══════════════════════════════════════════════════════════════════
    # STEP 5: Sports-specific keywords -> REJECT
    # ══════════════════════════════════════════════════════════════════
    # Only reject if the text contains UNAMBIGUOUSLY sports terms.
    # Removed ambiguous words like "match", "quarter", "half", "draft"
    # that commonly appear in non-sports contexts.
    #
    # NOTE: Non-weather tickers were already rejected in Step 2 above.
    # This catches any remaining markets with sports text but unknown tickers.
    # This MUST come before classify_market_type (Step 7) because
    # parse_temperature_threshold can match sports phrases like "over 200"
    # as a temperature, causing false positives.
    SPORTS_KEYWORDS = [
        # Unambiguous sports terms
        "points scored", "touchdown", "field goal", "home run",
        "strikeout", "pitcher", "batting", "free throw",
        "3-pointer", "yellow card", "red card", "corner kick",
        # Unambiguous sports leagues/orgs
        "nfl", "nba", "mlb", "nhl", "mls", "pga", "atp", "wta",
        "ufc", "super bowl", "world series", "stanley cup",
        # Unambiguous sports names
        "basketball", "baseball", "football", "hockey", "soccer",
        "tennis", "golf", "boxing", "mma",
    ]
    for kw in SPORTS_KEYWORDS:
        if kw in combined:
            return False

    # ══════════════════════════════════════════════════════════════════
    # STEP 6: Sports subtitle pattern (refined)
    # ══════════════════════════════════════════════════════════════════
    # The old pattern rejected ANY subtitle with "yes Name1, yes Name2".
    # But weather markets ALSO use this pattern for:
    #   - Hurricane names: "yes Alberto, yes Beryl, yes Chris"
    #   - Earthquake regions: "yes Southern CA, yes Northern CA"
    #   - Storm categories: "yes Category 3, yes Category 4"
    #
    # New approach: only reject if the subtitle looks like sports player
    # props. We detect this by looking for "yes [FirstName] [LastName]"
    # patterns (proper noun names = people = likely sports players).
    # Hurricane names, city names, and category names don't have the
    # same pattern as human first+last names.
    if subtitle.startswith("yes ") and ",yes " in subtitle:
        # Check if the subtitle contains human-name patterns
        # Sports props have names like "yes Hubert Hurkacz, yes Alexandre Muller"
        # Weather markets have names like "yes Alberto, yes Beryl"
        #   or locations like "yes Southern CA, yes Northern CA"
        #   or categories like "yes Category 3, yes Category 4"
        #
        # Heuristic: If the names after "yes " are 2+ capitalized words
        # (first+last name pattern), it's likely sports. If they're
        # single words or non-name patterns, it's likely weather.
        import re as _re
        # Extract all the items after "yes "
        items = _re.findall(r'yes\s+([\w\s]+?)(?:,|$)', subtitle)
        if items:
            # Check if any item looks like a person name (2+ capitalized words)
            person_name_count = 0
            for item in items:
                item = item.strip()
                # Person name: "Hubert Hurkacz" (2+ words, both capitalized)
                words = item.split()
                if len(words) >= 2 and all(w[0].isupper() for w in words if w):
                    person_name_count += 1
            # If most items look like person names, reject as sports
            if person_name_count >= 2 and person_name_count >= len(items) * 0.5:
                return False

    # ══════════════════════════════════════════════════════════════════
    # STEP 7: classify_market_type -> accept if non-generic
    # ══════════════════════════════════════════════════════════════════
    # This is intentionally placed AFTER sports keyword checks because
    # parse_temperature_threshold can match sports phrases like "over 200"
    # as a temperature, causing false positives.
    market_type = classify_market_type(combined)
    if market_type != "generic":
        return True

    # ══════════════════════════════════════════════════════════════════
    # STEP 8: Location found -> accept
    # ══════════════════════════════════════════════════════════════════
    # If we can parse a location from the text, it's more likely a
    # weather market than a sports market. Sports markets typically
    # reference teams/players, not geographic locations.
    if parse_location(combined):
        return True

    # ══════════════════════════════════════════════════════════════════
    # STEP 9: Default -> reject
    # ══════════════════════════════════════════════════════════════════
    # No weather signals, no location, not a known weather ticker.
    # Likely a non-weather market that ended up in the climate category.
    return False


def parse_temperature_threshold(text: str) -> Optional[float]:
    """Parse a temperature threshold from market title (e.g., 'above 90°F')."""
    patterns = [
        r"above\s+(\d+)",
        r"below\s+(\d+)",
        r"over\s+(\d+)",
        r"under\s+(\d+)",
        r"higher\s+than\s+(\d+)",
        r"lower\s+than\s+(\d+)",
        r"exceeds?\s+(\d+)",
        r">\s*(\d+)",
        r"<\s*(\d+)",
        r"(\d+)\s*[°˚]?\s*[fF]",
        r"(\d+)\s+degrees?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def parse_direction(text: str) -> str:
    """Parse whether the market is about 'above' or 'below' a threshold."""
    text_lower = text.lower()
    above_words = ["above", "over", "higher", "exceed", ">", "greater", "at least"]
    below_words = ["below", "under", "lower", "<", "less", "at most"]

    for word in above_words:
        if word in text_lower:
            return "above"
    for word in below_words:
        if word in text_lower:
            return "below"

    return "above"  # default


def pd_isna(val) -> bool:
    """Check if a pandas value is NA, handling various types."""
    try:
        import pandas as _pd
        return bool(_pd.isna(val))
    except (ImportError, TypeError, ValueError):
        return val is None


def safe_float(row, col: str) -> Optional[float]:
    """
    Safely extract a float value from a pandas Series row.
    Handles NA values, None, and missing columns.
    """
    try:
        if col not in row.index:
            return None
        val = row[col]
        if val is None or pd_isna(val):
            return None
        return float(val)
    except (TypeError, ValueError, KeyError):
        return None


def safe_c_to_f(row, col: str) -> Optional[float]:
    """
    Safely extract a Celsius value from a pandas row and convert to Fahrenheit.
    Returns None if the value is NA or missing.
    """
    val = safe_float(row, col)
    if val is not None:
        return val * 9/5 + 32
    return None


def safe_float_mean(df, col: str) -> Optional[float]:
    """
    Safely calculate the mean of a DataFrame column.
    Returns None if the column doesn't exist or all values are NA.
    """
    try:
        if col not in df.columns:
            return None
        series = df[col].dropna()
        if series.empty:
            return None
        return float(series.mean())
    except (TypeError, ValueError, KeyError):
        return None


# ── Weather Strategy ────────────────────────────────────────────────────

class WeatherStrategy:
    """
    Identifies +EV opportunities in Kalshi weather markets.

    Data sources (priority order):
      1. Meteostat — station-based historical observations
      2. NWS/Open-Meteo — weather forecasts
      3. Open-Meteo archive — historical baselines (fallback)

    Workflow:
    1. Scanner finds weather markets
    2. Parse location + threshold + market type from title
    3. Fetch forecasts + Meteostat observations
    4. Fetch historical baseline (Meteostat preferred)
    5. Compute fair probability using all data sources
    6. EV Analyzer compares to market price
    7. Generate TradeRecommendations for +EV opportunities
    """

    def __init__(self, ev_analyzer: Optional[EVAnalyzer] = None):
        self.fetcher = WeatherDataFetcher()
        self.ev_analyzer = ev_analyzer or EVAnalyzer()
        self._min_confidence = 0.55  # Don't trade below this confidence
        self._meteostat_available = _METEOSTAT_AVAILABLE

        if self._meteostat_available:
            print("[Weather] Meteostat integration ACTIVE — station-based observations enabled")
        else:
            print("[Weather] Meteostat not available — using NWS/Open-Meteo only")

    def scan_and_analyze(
        self,
        scanner: MarketScanner,
    ) -> List[TradeRecommendation]:
        """
        Scan all weather markets and find +EV opportunities.

        Returns list of TradeRecommendations, sorted by edge (best first).
        """
        weather_markets = scanner.get_by_category("weather")
        print(f"[Weather] Found {len(weather_markets)} weather markets to analyze")

        recommendations = []
        for market in weather_markets:
            try:
                rec = self.analyze_market(market)
                if rec and rec.suggested_size > 0:
                    recommendations.append(rec)
            except Exception as e:
                print(f"[Weather] Error analyzing {market.ticker}: {e}")

        # Sort by edge (best first)
        recommendations.sort(key=lambda r: abs(r.ev_cents), reverse=True)
        print(f"[Weather] Found {len(recommendations)} +EV opportunities")
        return recommendations

    def analyze_market(self, market: MarketInfo) -> Optional[TradeRecommendation]:
        """Analyze a single weather market for +EV opportunity."""
        combined_text = market.title + " " + market.subtitle

        # Step 0: Filter out non-weather markets (sports, etc.)
        if not is_actual_weather_market(market):
            return None

        # Step 1: Classify market type
        market_type = classify_market_type(combined_text)

        # Step 2: Parse location
        coords = parse_location(combined_text)
        if not coords:
            # For climate change / global markets, we may not need specific coords
            if market_type == "climate_change":
                return self._analyze_climate_change_market(market)
            # For earthquake/volcano without location, try broader approach
            if market_type in ("earthquake", "volcano", "hurricane", "tornado", "wildfire"):
                return self._analyze_event_market(market, market_type)
            print(f"[Weather] Can't parse location from: {market.title[:60]}")
            return None

        lat, lon = coords

        # Step 3: Handle non-temperature/non-precip markets with special logic
        if market_type in ("earthquake", "volcano", "hurricane", "tornado", "wildfire", "drought"):
            return self._analyze_event_market(market, market_type, lat, lon)

        # Step 4: Parse temperature threshold (if temperature market)
        threshold = parse_temperature_threshold(combined_text)
        direction = parse_direction(combined_text)

        # Step 5: Fetch forecast data (with rate limiting)
        from .rate_limiter import get_weather_limiter
        weather_limiter = get_weather_limiter()
        weather_limiter.wait("api.open-meteo.com")

        forecast_data = self.fetcher.get_open_meteo(lat, lon, forecast_days=7)
        if not forecast_data:
            # Try NWS as fallback
            weather_limiter.wait("api.weather.gov")
            nws_data = self.fetcher.get_nws_forecast(lat, lon)
            if nws_data:
                forecast_data = self._convert_nws_to_standard(nws_data)

        if not forecast_data:
            print(f"[Weather] No forecast data for {market.title[:40]}")
            return None

        # Step 6: Fetch Meteostat recent observations (reality check)
        recent_obs = None
        if self._meteostat_available:
            try:
                recent_obs = self.fetcher.get_meteostat_recent(lat, lon, days_back=5)
            except Exception:
                pass  # Non-critical, continue without it

        # Step 7: Fetch historical baseline (Meteostat preferred)
        now = datetime.now()
        weather_limiter.wait("api.open-meteo.com")
        historical = self.fetcher.get_historical_baseline(lat, lon, now.month, now.day)

        # Step 8: Calculate fair probability
        fair_prob, confidence, reasoning = self._calculate_probability(
            market_title=market.title,
            market_type=market_type,
            threshold=threshold,
            direction=direction,
            forecast=forecast_data,
            historical=historical,
            recent_obs=recent_obs,
        )

        if fair_prob is None:
            return None

        # Step 9: Run through EV analyzer
        market_price = market.implied_prob if hasattr(market, 'implied_prob') else market.yes_price

        data_sources = []
        if recent_obs:
            data_sources.append("meteostat_recent")
        if historical:
            data_sources.append(historical.get("source", "unknown"))
        data_sources.extend(["open-meteo", "nws"])

        return self.ev_analyzer.analyze(
            ticker=market.ticker,
            fair_probability=fair_prob,
            market_price=market_price,
            confidence=confidence,
            reasoning=reasoning,
            strategy="weather",
            data_sources=data_sources,
        )

    def _convert_nws_to_standard(self, nws_data: Dict) -> Optional[Dict]:
        """Convert NWS forecast format to Open-Meteo-like format for uniform processing."""
        try:
            periods = nws_data.get("properties", {}).get("periods", [])
            if not periods:
                return None

            # Group by day
            daily_highs = {}
            daily_lows = {}
            for period in periods:
                name = period.get("name", "")
                temp = period.get("temperature")
                if temp is None:
                    continue
                # NWS temps are already in Fahrenheit
                is_night = "night" in name.lower()
                # Extract day reference
                if is_night:
                    daily_lows[name] = temp
                else:
                    daily_highs[name] = temp

            highs = list(daily_highs.values())[:7]
            lows = list(daily_lows.values())[:7]

            return {
                "daily": {
                    "temperature_2m_max": highs,
                    "temperature_2m_min": lows,
                    "precipitation_sum": [0.0] * max(len(highs), len(lows)),
                    "windspeed_10m_max": [],
                    "weathercode": [],
                },
                "source": "nws",
            }
        except Exception:
            return None

    def _analyze_climate_change_market(self, market: MarketInfo) -> Optional[TradeRecommendation]:
        """
        Analyze climate change markets (e.g., "Will the world pass 2°C over pre-industrial?").

        These are long-term, high-uncertainty markets. We use conservative
        estimates and always mark as high risk.
        """
        text_lower = (market.title + " " + market.subtitle).lower()
        market_price = market.yes_price

        # Parse the temperature threshold
        threshold_match = re.search(r'(\d+\.?\d*)\s*degrees?\s*celsius', text_lower)
        if not threshold_match:
            threshold_match = re.search(r'(\d+\.?\d*)\s*[°]\s*c', text_lower)
        if not threshold_match:
            threshold_match = re.search(r'(\d+\.?\d*)\s*[°]', text_lower)

        if threshold_match:
            threshold = float(threshold_match.group(1))

            # Current global temp anomaly is approximately 1.2-1.5°C above pre-industrial
            # 2024 was the first year to exceed 1.5°C annually
            current_anomaly = 1.45  # Approximate current annual anomaly

            if threshold >= 2.0:
                # 2°C threshold — unlikely in current year but trending upward
                fair_prob = 0.15  # Conservative estimate
                reasoning = f"Climate: current anomaly ~{current_anomaly}°C, 2°C threshold likely years away"
            elif threshold >= 1.5:
                fair_prob = 0.55  # Close to current levels, could go either way
                reasoning = f"Climate: current anomaly ~{current_anomaly}°C, 1.5°C threshold is borderline"
            else:
                fair_prob = 0.85  # Below 1.5°C already being exceeded
                reasoning = f"Climate: current anomaly ~{current_anomaly}°C, {threshold}°C already being exceeded"
        else:
            # Can't parse threshold — very low confidence
            fair_prob = 0.5
            reasoning = "Climate market: unable to parse temperature threshold"

        confidence = 0.35  # Low confidence for climate change markets

        return self.ev_analyzer.analyze(
            ticker=market.ticker,
            fair_probability=fair_prob,
            market_price=market_price,
            confidence=confidence,
            reasoning=reasoning,
            strategy="weather_climate",
            data_sources=["climate_data"],
        )

    def _analyze_event_market(
        self,
        market: MarketInfo,
        market_type: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> Optional[TradeRecommendation]:
        """
        Analyze event-based weather markets (earthquake, volcano, hurricane, etc.).

        These markets are harder to predict with weather data alone.
        We provide conservative probability estimates based on historical
        frequency data, and always mark them as high risk.
        """
        text_lower = (market.title + " " + market.subtitle).lower()
        market_price = market.yes_price

        # Historical frequency estimates (approximate annual probabilities)
        # These are very rough and should be refined with actual data
        EVENT_BASELINES = {
            "earthquake": {
                "california": 0.60,   # ~60% chance of 5.0+ in CA any year
                "us": 0.80,           # ~80% chance of notable US earthquake
                "default": 0.40,      # Default estimate
                "8.0_magnitude": 0.05, # 8.0+ quakes are rare
            },
            "volcano": {
                "default": 0.10,      # Eruptions are rare events
                "yellowstone": 0.001, # Yellowstone supervolcano extremely unlikely
            },
            "hurricane": {
                "gulf_coast": 0.70,   # High probability during season
                "east_coast": 0.50,
                "us": 0.85,           # At least one US hurricane per year
                "default": 0.40,
            },
            "tornado": {
                "default": 0.60,      # Tornado season is fairly active
                "oklahoma": 0.70,
            },
            "wildfire": {
                "california": 0.75,   # Very likely during fire season
                "default": 0.40,
            },
            "drought": {
                "default": 0.30,
            },
        }

        baseline = EVENT_BASELINES.get(market_type, {})
        fair_prob = baseline.get("default", 0.30)

        # Refine based on location/region
        if lat is not None:
            for region, prob in baseline.items():
                if region == "default":
                    continue
                if region.replace("_", " ") in text_lower:
                    fair_prob = prob
                    break

        # Check for magnitude/severity modifiers
        if "8.0" in text_lower or "8.0 magnitude" in text_lower:
            fair_prob = baseline.get("8.0_magnitude", 0.05)
        elif "7.0" in text_lower:
            fair_prob = min(fair_prob, 0.15)
        elif "supervolcano" in text_lower:
            fair_prob = 0.001  # Extremely unlikely in any given year

        # Check for time constraints (e.g., "this year", "by June")
        if "this year" in text_lower or "by december" in text_lower:
            # Adjust for remaining time in the year
            pass  # fair_prob already annual
        elif "this month" in text_lower or "by end of" in text_lower:
            fair_prob *= 0.15  # Much less likely in a single month

        # Cap probability
        fair_prob = max(0.01, min(0.95, fair_prob))

        # High risk, low confidence for event markets
        confidence = 0.30  # Low — we're using rough baselines
        risk_level = "high"

        # Get Meteostat data for recent weather patterns if available
        meteostat_context = ""
        if lat is not None and self._meteostat_available:
            try:
                recent = self.fetcher.get_meteostat_recent(lat, lon, days_back=5)
                if recent and recent.get("days"):
                    meteostat_context = f" | Meteostat: {len(recent['days'])} recent observations available"
            except Exception:
                pass

        reasoning = (
            f"Event market ({market_type}): estimated {fair_prob:.0%} baseline probability "
            f"from historical frequency data{meteostat_context} | "
            f"Market type: {market_type} | HIGH RISK — use with caution"
        )

        return self.ev_analyzer.analyze(
            ticker=market.ticker,
            fair_probability=fair_prob,
            market_price=market_price,
            confidence=confidence,
            reasoning=reasoning,
            strategy=f"weather_{market_type}",
            data_sources=["historical_frequency"] + (["meteostat_recent"] if meteostat_context else []),
        )

    def _calculate_probability(
        self,
        market_title: str,
        market_type: str = "generic",
        threshold: Optional[float] = None,
        direction: str = "above",
        forecast: Dict = None,
        historical: Optional[Dict] = None,
        recent_obs: Optional[Dict] = None,
    ) -> Tuple[Optional[float], float, str]:
        """
        Calculate fair probability from all available data sources.

        Blends:
          - Weather forecast data (Open-Meteo / NWS)
          - Meteostat recent observations (reality check)
          - Historical baseline data (Meteostat preferred)

        Returns:
            (fair_probability, confidence, reasoning)
        """
        if forecast is None:
            return (None, 0.0, "No forecast data available")

        daily = forecast.get("daily", {})

        # Extract forecast temperatures (Open-Meteo with fahrenheit flag)
        highs = daily.get("temperature_2m_max", [])
        lows = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind_max = daily.get("windspeed_10m_max", [])

        # Filter out None values
        valid_highs = [t for t in highs[:7] if t is not None]
        valid_lows = [t for t in lows[:7] if t is not None]

        # ── Temperature markets ────────────────────────────────────────
        if threshold is not None and (valid_highs or valid_lows):
            return self._calc_temp_probability(
                threshold, direction, valid_highs, valid_lows, historical, recent_obs
            )

        # ── Precipitation markets ─────────────────────────────────────
        if market_type == "precipitation" or any(kw in market_title.lower() for kw in ["rain", "snow", "precip"]):
            return self._calc_precip_probability(precip, historical, recent_obs)

        # ── Hurricane/storm markets ───────────────────────────────────
        if any(kw in market_title.lower() for kw in ["hurricane", "tropical", "storm"]):
            return (None, 0.0, "Hurricane markets require NHC tracking data — use event market path")

        # ── Generic temperature market (no specific threshold) ─────────
        if market_type == "temperature" and valid_highs:
            # For generic temperature markets, use the forecast spread
            # to estimate if temperatures will be above/below seasonal norms
            return self._calc_generic_temp_probability(valid_highs, valid_lows, historical, recent_obs)

        # Generic: can't classify
        return (None, 0.0, f"Unclassifiable weather market: {market_title[:40]}")

    def _calc_temp_probability(
        self,
        threshold: float,
        direction: str,
        forecast_highs: List[float],
        forecast_lows: List[float],
        historical: Optional[Dict],
        recent_obs: Optional[Dict] = None,
    ) -> Tuple[float, float, str]:
        """Calculate probability for a temperature threshold market."""
        if direction == "above":
            actual_temps = forecast_highs
            hist_key = "avg_high"
        else:
            actual_temps = forecast_lows
            hist_key = "avg_low"

        if not actual_temps:
            return (0.5, 0.2, "No forecast temperature data available")

        # Forecast-based probability
        days_meeting = sum(1 for t in actual_temps if
                         (t >= threshold if direction == "above" else t <= threshold))
        forecast_prob = days_meeting / len(actual_temps)

        # Historical baseline adjustment
        hist_adjustment = 0.0
        hist_reasoning = ""
        hist_source = ""
        if historical and historical.get(hist_key) is not None:
            hist_avg = historical[hist_key]
            hist_source = historical.get("source", "unknown")
            if direction == "above":
                hist_prob = 1.0 if hist_avg >= threshold else max(0, 0.5 - (threshold - hist_avg) / 10)
            else:
                hist_prob = 1.0 if hist_avg <= threshold else max(0, 0.5 - (hist_avg - threshold) / 10)
            hist_adjustment = (hist_prob - forecast_prob) * 0.3  # 30% weight on historical
            hist_reasoning = f" | Historical avg: {hist_avg:.1f}°F (hist_prob={hist_prob:.0%}, source={hist_source})"

        # Meteostat recent observations adjustment (reality check)
        recent_adjustment = 0.0
        recent_reasoning = ""
        if recent_obs and recent_obs.get("avg_high_f") is not None:
            if direction == "above":
                recent_avg = recent_obs["avg_high_f"]
                recent_prob = 1.0 if recent_avg >= threshold else max(0, 0.5 - (threshold - recent_avg) / 8)
            else:
                recent_avg = recent_obs.get("avg_low_f", recent_obs["avg_high_f"])
                recent_prob = 1.0 if recent_avg <= threshold else max(0, 0.5 - (recent_avg - threshold) / 8)
            recent_adjustment = (recent_prob - forecast_prob) * 0.15  # 15% weight on recent actuals
            recent_reasoning = f" | Meteostat recent avg: {recent_avg:.1f}°F (recent_prob={recent_prob:.0%})"

        # Blended probability
        fair_prob = max(0.0, min(1.0, forecast_prob + hist_adjustment + recent_adjustment))

        # Confidence based on data quality and agreement
        spread = max(actual_temps) - min(actual_temps) if len(actual_temps) > 1 else 0
        confidence = 0.7 if spread < 5 else 0.5
        if historical:
            confidence = min(confidence + 0.1, 0.9)
        if recent_obs:
            confidence = min(confidence + 0.05, 0.95)  # Meteostat data boosts confidence slightly

        # Reasoning string
        forecast_str = ", ".join(f"{t:.1f}" for t in actual_temps[:5])
        reasoning = (
            f"Forecast temps: [{forecast_str}] | "
            f"Threshold: {direction} {threshold}°F | "
            f"Forecast prob: {forecast_prob:.0%}{hist_reasoning}{recent_reasoning}"
        )

        return (fair_prob, confidence, reasoning)

    def _calc_generic_temp_probability(
        self,
        forecast_highs: List[float],
        forecast_lows: List[float],
        historical: Optional[Dict],
        recent_obs: Optional[Dict] = None,
    ) -> Tuple[float, float, str]:
        """Calculate probability for a generic temperature market without specific threshold."""
        if not forecast_highs:
            return (0.5, 0.2, "No forecast data")

        # Compare forecast to historical averages
        forecast_avg = sum(forecast_highs) / len(forecast_highs)

        if historical and historical.get("avg_high") is not None:
            hist_avg = historical["avg_high"]
            deviation = forecast_avg - hist_avg
            # If forecast is above historical, market for "above average" is more likely
            fair_prob = 0.5 + (deviation / 20.0)  # Normalize deviation
            fair_prob = max(0.05, min(0.95, fair_prob))

            hist_source = historical.get("source", "unknown")
            reasoning = (
                f"Forecast avg: {forecast_avg:.1f}°F vs Historical avg: {hist_avg:.1f}°F "
                f"(deviation: {deviation:+.1f}°F, source={hist_source})"
            )
            confidence = 0.55
        else:
            fair_prob = 0.5
            reasoning = f"Forecast avg: {forecast_avg:.1f}°F — no historical comparison"
            confidence = 0.35

        # Adjust with Meteostat recent observations
        if recent_obs and recent_obs.get("avg_high_f") is not None:
            recent_avg = recent_obs["avg_high_f"]
            recent_dev = forecast_avg - recent_avg
            reasoning += f" | Meteostat recent avg: {recent_avg:.1f}°F"
            confidence = min(confidence + 0.05, 0.85)

        return (fair_prob, confidence, reasoning)

    def _calc_precip_probability(
        self,
        precip_forecast: List[float],
        historical: Optional[Dict],
        recent_obs: Optional[Dict] = None,
    ) -> Tuple[float, float, str]:
        """Calculate probability for precipitation markets."""
        valid_precip = [p for p in precip_forecast[:7] if p is not None]
        if not valid_precip:
            return (0.5, 0.2, "No precipitation forecast data")

        rain_days = sum(1 for p in valid_precip if p > 0.1)  # 0.1mm threshold
        forecast_prob = rain_days / len(valid_precip)

        # Historical adjustment
        hist_adj = 0.0
        hist_source = ""
        if historical and historical.get("avg_precip") is not None:
            avg_precip = historical["avg_precip"]
            hist_source = historical.get("source", "unknown")
            hist_rain_prob = min(1.0, avg_precip / 5.0)
            hist_adj = (hist_rain_prob - forecast_prob) * 0.2

        # Meteostat recent observations
        recent_adj = 0.0
        recent_reasoning = ""
        if recent_obs and recent_obs.get("days"):
            recent_rain_days = sum(1 for d in recent_obs["days"]
                                   if d.get("precip_mm") is not None and d["precip_mm"] > 0.5)
            if recent_obs["days"]:
                recent_rain_prob = recent_rain_days / len(recent_obs["days"])
                recent_adj = (recent_rain_prob - forecast_prob) * 0.15
                recent_reasoning = f" | Meteostat: {recent_rain_days}/{len(recent_obs['days'])} recent rain days"

        fair_prob = max(0.0, min(1.0, forecast_prob + hist_adj + recent_adj))
        confidence = 0.6 if len(valid_precip) >= 3 else 0.4
        if historical:
            confidence = min(confidence + 0.05, 0.85)
        if recent_obs:
            confidence = min(confidence + 0.05, 0.85)

        reasoning = (
            f"Forecast precip: {[f'{p:.1f}' for p in valid_precip[:5]]} | "
            f"Forecast prob: {forecast_prob:.0%}"
            f"{f' (source={hist_source})' if hist_source else ''}"
            f"{recent_reasoning}"
        )

        return (fair_prob, confidence, reasoning)
