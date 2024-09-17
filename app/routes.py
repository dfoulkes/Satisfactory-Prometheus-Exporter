from app import app
from prometheus_client import Gauge, generate_latest, Info
from app.satisfactory_api import get_api_token, get_server_stats
from flask import Blueprint

# Define Prometheus Gauges
gauges = {
    "num_connected_players": Gauge("num_connected_players", "Number of Connected Players"),
    "player_limit": Gauge("player_limit", "Player Limit"),
    "tech_tier": Gauge("tech_tier", "Tech Tier"),
    "is_game_running": Gauge("is_game_running", "Is Game Running"),
    "total_game_duration": Gauge("total_game_duration", "Total Game Duration"),
    "is_game_paused": Gauge("is_game_paused", "Is Game Paused"),
    "average_tick_rate": Gauge("average_tick_rate", "Average Tick Rate")
}

# Define Prometheus Info Metrics
info_metrics = {
    "active_session_name": Info("active_session_name", "Active Session Name"),
    "auto_load_session_name": Info("auto_load_session_name", "Auto Load Session Name")
}


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello, World!"

@app.route('/metrics')
def metrics():
    token = get_api_token()
    stats = get_server_stats(token)

    # Set gauge values
    gauges["num_connected_players"].set(stats.numConnectedPlayers)
    gauges["player_limit"].set(stats.playerLimit)
    gauges["tech_tier"].set(stats.techTier)
    gauges["is_game_running"].set(stats.isGameRunning)
    gauges["total_game_duration"].set(stats.totalGameDuration)
    gauges["is_game_paused"].set(stats.isGamePaused)
    gauges["average_tick_rate"].set(stats.averageTickRate)

    # Set info values
    info_metrics["active_session_name"].info({"value": stats.activeSessionName})
    info_metrics["auto_load_session_name"].info({"value": stats.autoLoadSessionName})

    return generate_latest()

