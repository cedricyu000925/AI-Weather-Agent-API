"""
Weather analysis tools for BigQuery NOAA data
"""

from google.cloud import bigquery
import json


class BigQueryWeatherTool:
    """Tool to fetch weather data from BigQuery NOAA GSOD dataset"""
    
    def __init__(self, project_id: str, station_id: str):
        self.client = bigquery.Client(project=project_id)
        self.station_id = station_id
    
    def get_recent_weather(self, days: int = 30) -> str:
        """
        Fetch recent weather data for the station
        
        Args:
            days: Number of recent days to fetch (default 30)
            
        Returns:
            String representation of weather data
        """
        query = f"""
        SELECT 
          FORMAT_DATE('%Y-%m-%d', 
            DATE(CAST(year AS INT64), CAST(mo AS INT64), CAST(da AS INT64))
          ) as date,
          ROUND((CAST(temp AS FLOAT64) - 32) * 5/9, 1) as temp_c,
          ROUND(CAST(prcp AS FLOAT64) * 25.4, 1) as precip_mm,
          ROUND(CAST(wdsp AS FLOAT64) * 1.852, 1) as wind_speed_kmh
        FROM `bigquery-public-data.noaa_gsod.gsod2023`
        WHERE stn = '{self.station_id}'
          AND CAST(temp AS FLOAT64) < 9000
          AND temp IS NOT NULL
        ORDER BY year DESC, mo DESC, da DESC
        LIMIT {days}
        """
        
        results = self.client.query(query).result()
        
        data = []
        for row in results:
            data.append({
                'date': row.date,
                'temp_c': float(row.temp_c) if row.temp_c else None,
                'precip_mm': float(row.precip_mm) if row.precip_mm else None,
                'wind_speed_kmh': float(row.wind_speed_kmh) if row.wind_speed_kmh else None
            })
        
        return str(data)


class WeatherAnalyzer:
    """Tool for calculating statistical weather metrics"""
    
    def calculate_statistics(self, weather_data_str: str) -> dict:
        """
        Calculate statistical metrics from weather data
        
        Args:
            weather_data_str: String representation of weather data list
            
        Returns:
            Dictionary with calculated statistics
        """
        try:
            # Parse the data string
            data = eval(weather_data_str)
            
            # Extract temperature values
            temps = []
            for d in data:
                if d.get('temp_c') is not None:
                    temps.append(float(d['temp_c']))
            
            if len(temps) < 2:
                return {"error": "Insufficient data for analysis"}
            
            # Calculate basic statistics
            mean_temp = sum(temps) / len(temps)
            variance = sum((x - mean_temp) ** 2 for x in temps) / len(temps)
            std_temp = variance ** 0.5
            
            current_temp = temps[0]
            z_score = (current_temp - mean_temp) / std_temp if std_temp > 0 else 0.0
            day_change = temps[0] - temps[1] if len(temps) > 1 else 0.0
            
            # Calculate week-over-week change if enough data
            if len(temps) >= 14:
                recent_week = sum(temps[:7]) / 7
                previous_week = sum(temps[7:14]) / 7
                week_change = recent_week - previous_week
            else:
                week_change = 0.0
            
            stats = {
                "current_temp": round(current_temp, 1),
                "mean_temp": round(mean_temp, 1),
                "std_dev": round(std_temp, 1),
                "min_temp": round(min(temps), 1),
                "max_temp": round(max(temps), 1),
                "z_score": round(z_score, 2),
                "day_over_day_change": round(day_change, 1),
                "week_over_week_change": round(week_change, 1),
                "anomaly_detected": abs(z_score) > 2,
                "significant_spike": abs(day_change) > 5,
                "total_days": len(temps)
            }
            
            return stats
        
        except Exception as e:
            return {"error": str(e)}
