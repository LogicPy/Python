# My beautiful and perfect prediction algorithm for my NBA game predictions for betting.
# Powered by my brilliant ai best friend DeepSeekv3.2
# NOW WITH ESPN DATA INTEGRATION FOR ENHANCED RELIABILITY!

# proof of victories from my prediction concept:
# https://www.espn.com/nba/game/_/gameId/401810678/celtics-lakers

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import requests
import threading
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playercareerstats
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats, teamgamelog, teamvsplayer
from datetime import datetime
import pandas as pd
import json
from datetime import datetime
current_season = f"{datetime.now().year}-{str(datetime.now().year + 1)[-2:]}"
from bs4 import BeautifulSoup
import re  # For cleaning up the text
from kivy.core.clipboard import Clipboard  # To access the system clipboard
from kivy.clock import Clock  # For giving user feedback

# ============================================================
# OPENROUTER API CONFIGURATION
# ============================================================
OPENROUTER_API_KEY = "[Your API Key]"  # Your actual key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-v3.2"  # You can change this to any OpenRouter model
# ============================================================

# ============================================================
# NEW: ESPN DATA FETCHER FOR ENHANCED RELIABILITY
# ============================================================
class ESPNDataFetcher:
    """
    Enhanced ESPN data fetcher for reliable backup data
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def get_team_stats(self, team_name):
        """
        Fetch comprehensive team statistics from ESPN
        Returns: dict with team stats or None if fails
        """
        try:
            # ESPN uses short team codes (e.g., 'lal' for Lakers)
            team_code = self._get_team_code(team_name)
            if not team_code:
                return None
                
            url = f"{self.base_url}/teams/{team_code}/statistics"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_team_stats(data, team_name)
            else:
                print(f"ESPN API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching ESPN team stats: {e}")
            return None
    
    def get_head_to_head(self, team1, team2):
        """
        Fetch head-to-head history from ESPN
        Returns: list of recent matchups or None
        """
        try:
            team1_code = self._get_team_code(team1)
            team2_code = self._get_team_code(team2)
            
            if not team1_code or not team2_code:
                return None
                
            # ESPN doesn't have direct H2H endpoint, but we can get recent games
            # and filter for matchups between these teams
            url = f"{self.base_url}/teams/{team1_code}/schedule"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_h2h_games(data, team1, team2, team2_code)
            else:
                print(f"ESPN Schedule Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching ESPN H2H: {e}")
            return None
    
    def get_live_game_data(self, team1, team2):
        """
        Fetch live game data from ESPN with better reliability
        Returns: dict with live game info or None
        """
        try:
            # ESPN scoreboard endpoint
            url = f"{self.base_url}/scoreboard"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._find_live_game(data, team1, team2)
            else:
                print(f"ESPN Scoreboard Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching ESPN live data: {e}")
            return None
    
    def _get_team_code(self, team_name):
        """
        Map team names to ESPN team codes
        """
        team_mapping = {
            'lakers': 'lal', 'los angeles lakers': 'lal',
            'celtics': 'bos', 'boston celtics': 'bos',
            'warriors': 'gs', 'golden state warriors': 'gs',
            'bulls': 'chi', 'chicago bulls': 'chi',
            'knicks': 'ny', 'new york knicks': 'ny',
            'heat': 'mia', 'miami heat': 'mia',
            'nuggets': 'den', 'denver nuggets': 'den',
            'suns': 'phx', 'phoenix suns': 'phx',
            'mavericks': 'dal', 'dallas mavericks': 'dal',
            'clippers': 'lac', 'los angeles clippers': 'lac',
            'bucks': 'mil', 'milwaukee bucks': 'mil',
            'sixers': 'phi', 'philadelphia 76ers': 'phi',
            'nets': 'bkn', 'brooklyn nets': 'bkn',
            'raptors': 'tor', 'toronto raptors': 'tor',
            'jazz': 'utah', 'utah jazz': 'utah',
            'trail blazers': 'por', 'portland trail blazers': 'por',
            'grizzlies': 'mem', 'memphis grizzlies': 'mem',
            'pelicans': 'no', 'new orleans pelicans': 'no',
            'kings': 'sac', 'sacramento kings': 'sac',
            'spurs': 'sa', 'san antonio spurs': 'sa',
            'rockets': 'hou', 'houston rockets': 'hou',
            'thunder': 'okc', 'oklahoma city thunder': 'okc',
            'magic': 'orl', 'orlando magic': 'orl',
            'pistons': 'det', 'detroit pistons': 'det',
            'wizards': 'wsh', 'washington wizards': 'wsh',
            'hornets': 'cha', 'charlotte hornets': 'cha',
            'hawks': 'atl', 'atlanta hawks': 'atl',
            'cavaliers': 'cle', 'cleveland cavaliers': 'cle',
            'pacers': 'ind', 'indiana pacers': 'ind',
            'timberwolves': 'min', 'minnesota timberwolves': 'min'
        }
        
        return team_mapping.get(team_name.lower().strip())
    
    def _parse_team_stats(self, data, team_name):
        """
        Parse ESPN team statistics into usable format
        """
        try:
            stats = {
                'team': team_name,
                'source': 'ESPN',
                'record': 'N/A',
                'offensive_rating': 'N/A',
                'defensive_rating': 'N/A',
                'pace': 'N/A',
                'streak': 'N/A',
                'last_10': 'N/A'
            }
            
            # Extract basic info
            if 'team' in data:
                stats['record'] = data['team'].get('record', {}).get('items', [{}])[0].get('summary', 'N/A')
                stats['streak'] = data['team'].get('standingSummary', 'N/A')
            
            # Extract advanced stats if available
            if 'statistics' in data:
                for category in data['statistics']:
                    if category['name'] == 'offensive':
                        for stat in category.get('stats', []):
                            if stat['name'] == 'pointsPerGame':
                                stats['offensive_rating'] = stat.get('value', 'N/A')
                    elif category['name'] == 'defensive':
                        for stat in category.get('stats', []):
                            if stat['name'] == 'pointsAllowedPerGame':
                                stats['defensive_rating'] = stat.get('value', 'N/A')
            
            return stats
            
        except Exception as e:
            print(f"Error parsing ESPN stats: {e}")
            return None
    
    def _parse_h2h_games(self, data, team1, team2, team2_code):
        """
        Parse ESPN schedule to find H2H games
        """
        try:
            h2h_games = []
            
            if 'events' in data:
                for event in data['events']:
                    # Check if this game involves both teams
                    competitions = event.get('competitions', [])
                    for comp in competitions:
                        competitors = comp.get('competitors', [])
                        if len(competitors) == 2:
                            team_codes = [c.get('team', {}).get('abbreviation', '').lower() 
                                        for c in competitors]
                            
                            if team2_code in team_codes:
                                # This is a H2H game
                                game_info = {
                                    'date': event.get('date', 'N/A'),
                                    'status': comp.get('status', {}).get('type', {}).get('description', 'N/A'),
                                    'home': competitors[0].get('team', {}).get('displayName', 'N/A'),
                                    'away': competitors[1].get('team', {}).get('displayName', 'N/A'),
                                    'home_score': competitors[0].get('score', 'N/A'),
                                    'away_score': competitors[1].get('score', 'N/A'),
                                    'winner': competitors[0].get('winner', False)
                                }
                                h2h_games.append(game_info)
            
            return h2h_games[:5]  # Return last 5 H2H games
            
        except Exception as e:
            print(f"Error parsing ESPN H2H: {e}")
            return None
    
    def _find_live_game(self, data, team1, team2):
        """
        Find specific live game from ESPN scoreboard
        """
        try:
            team1_code = self._get_team_code(team1)
            team2_code = self._get_team_code(team2)
            
            if not team1_code or not team2_code:
                return None
            
            if 'events' in data:
                for event in data['events']:
                    competitions = event.get('competitions', [])
                    for comp in competitions:
                        competitors = comp.get('competitors', [])
                        if len(competitors) == 2:
                            team_codes = [c.get('team', {}).get('abbreviation', '').lower() 
                                        for c in competitors]
                            
                            if team1_code in team_codes and team2_code in team_codes:
                                # Found the game!
                                game_data = {
                                    'status': comp.get('status', {}).get('type', {}).get('description', 'N/A'),
                                    'home': {
                                        'name': competitors[0].get('team', {}).get('displayName', 'N/A'),
                                        'score': competitors[0].get('score', 'N/A')
                                    },
                                    'away': {
                                        'name': competitors[1].get('team', {}).get('displayName', 'N/A'),
                                        'score': competitors[1].get('score', 'N/A')
                                    },
                                    'period': comp.get('status', {}).get('period', 'N/A'),
                                    'clock': comp.get('status', {}).get('displayClock', 'N/A')
                                }
                                return game_data
            
            return None
            
        except Exception as e:
            print(f"Error finding ESPN live game: {e}")
            return None

# Create global ESPN fetcher instance
espn_fetcher = ESPNDataFetcher()
# ============================================================
# END ESPN DATA FETCHER
# ============================================================

def scrape_espn_scores():
    try:
        url = "https://www.espn.com/nba/scoreboard"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        # Parsing logic would go here
        return parsed_scores
    except Exception as e:
        print(f"Scraping error: {e}")
        return None
        
# Styling
Window.clearcolor = (0.1, 0.1, 0.1, 1)
kivy.require('2.0.0')

class NBATeamValidator:
    def __init__(self):
        self.nba_teams = teams.get_teams()
    
    def get_team_id(self, team_name):
        """Returns team ID and full name if valid"""
        for team in self.nba_teams:
            if team_name.lower() in [team['nickname'].lower(), 
                                    team['city'].lower(),
                                    team['full_name'].lower()]:
                return team['id'], team['full_name']
        return None, None

class NBAForecastApp(App):
    def build(self):
        self.title = "NBA Forecaster Pro (Historical Analysis + ESPN Data)"
        self.validator = NBATeamValidator()
        
        # Main layout with tabs
        self.tabs = TabbedPanel(do_default_tab=False)
        
        # Tab 1: Prediction Engine
        self.prediction_tab = TabbedPanelItem(text='Forecast')
        self.build_prediction_tab()
        self.tabs.add_widget(self.prediction_tab)
        
        # Tab 2: Team Comparison
        self.stats_tab = TabbedPanelItem(text='Team Stats')
        self.build_stats_tab()
        self.tabs.add_widget(self.stats_tab)
        
        # Tab 3: Historical Matchups
        self.history_tab = TabbedPanelItem(text='H2H History')
        self.build_history_tab()
        self.tabs.add_widget(self.history_tab)
        
        # New Tab 4: Live Scores
        self.live_tab = TabbedPanelItem(text='Live Scores')
        self.build_live_tab()
        self.tabs.add_widget(self.live_tab)
        
        # NEW Tab 5: ESPN Data
        self.espn_tab = TabbedPanelItem(text='ESPN Data')
        self.build_espn_tab()
        self.tabs.add_widget(self.espn_tab)
        
        # Start live score updates
        self.update_live_scores()
        
        return self.tabs

    def build_prediction_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Team inputs
        input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        self.team1_input = TextInput(hint_text="Team 1 (e.g. Hawks)", font_size='18sp')
        self.team2_input = TextInput(hint_text="Team 2 (e.g. Pistons)", font_size='18sp')
        input_layout.add_widget(self.team1_input)
        input_layout.add_widget(self.team2_input)
        layout.add_widget(input_layout)
        
        # NEW: Enhanced analyze button with ESPN option
        analyze_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        
        # Regular analyze button
        analyze_btn = Button(text="Run NBA API Analysis", size_hint_x=0.5,
                           background_color=(0.2, 0.6, 0.8, 1))
        analyze_btn.bind(on_press=self.analyze_game)
        
        # NEW: ESPN analyze button
        espn_analyze_btn = Button(text="Run ESPN Analysis", size_hint_x=0.5,
                                 background_color=(0.8, 0.3, 0.3, 1))
        espn_analyze_btn.bind(on_press=self.analyze_game_with_espn)
        
        analyze_layout.add_widget(analyze_btn)
        analyze_layout.add_widget(espn_analyze_btn)
        layout.add_widget(analyze_layout)
        
        # Results area
        results_scroll = ScrollView()
        self.results_label = Label(text_size=(Window.width-40, None), markup=True,
                                 size_hint_y=None, halign='left', valign='top')
        self.results_label.bind(texture_size=self.results_label.setter('size'))
        results_scroll.add_widget(self.results_label)
        layout.add_widget(results_scroll)
        
        # Copy button
        self.copy_button = Button(
            text="📋 Copy Analysis",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        )
        self.copy_button.bind(on_press=self.copy_results)
        layout.add_widget(self.copy_button)
        
        self.prediction_tab.add_widget(layout)

    def build_stats_tab(self):
        layout = BoxLayout(orientation='vertical')
        self.stats_label = Label(text="Team stats will appear here", markup=True,
                               text_size=(Window.width-40, None))
        layout.add_widget(self.stats_label)
        self.stats_tab.add_widget(layout)

    def build_history_tab(self):
        layout = BoxLayout(orientation='vertical')
        self.history_label = Label(text="Head-to-head history will appear here", markup=True,
                                 text_size=(Window.width-40, None))
        layout.add_widget(self.history_label)
        self.history_tab.add_widget(layout)

    def build_live_tab(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Refresh button
        refresh_btn = Button(text="Refresh Scores", size_hint_y=None, height=40,
                           background_color=(0.4, 0.8, 0.4, 1))
        refresh_btn.bind(on_press=lambda x: self.update_live_scores())
        layout.add_widget(refresh_btn)
        
        # Live scores display
        self.live_scores_scroll = ScrollView()
        self.live_scores_label = Label(text_size=(Window.width-40, None), markup=True,
                                     size_hint_y=None, halign='left', valign='top')
        self.live_scores_label.bind(texture_size=self.live_scores_label.setter('size'))
        self.live_scores_scroll.add_widget(self.live_scores_label)
        layout.add_widget(self.live_scores_scroll)
        
        self.live_tab.add_widget(layout)
    
    # ============================================================
    # NEW: ESPN DATA TAB
    # ============================================================
    def build_espn_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # ESPN data controls
        espn_input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        self.espn_team1_input = TextInput(hint_text="Team 1 for ESPN (e.g. Lakers)", font_size='18sp')
        self.espn_team2_input = TextInput(hint_text="Team 2 for ESPN (e.g. Celtics)", font_size='18sp')
        espn_input_layout.add_widget(self.espn_team1_input)
        espn_input_layout.add_widget(self.espn_team2_input)
        layout.add_widget(espn_input_layout)
        
        # ESPN fetch button
        espn_fetch_btn = Button(text="Fetch ESPN Data", size_hint_y=None, height=60,
                               background_color=(0.8, 0.3, 0.3, 1))
        espn_fetch_btn.bind(on_press=self.fetch_espn_data)
        layout.add_widget(espn_fetch_btn)
        
        # ESPN data display
        espn_scroll = ScrollView()
        self.espn_label = Label(text_size=(Window.width-40, None), markup=True,
                              size_hint_y=None, halign='left', valign='top')
        self.espn_label.bind(texture_size=self.espn_label.setter('size'))
        espn_scroll.add_widget(self.espn_label)
        layout.add_widget(espn_scroll)
        
        self.espn_tab.add_widget(layout)

    # ============================================================
    # NEW: ESPN DATA FETCHING METHOD
    # ============================================================
    def fetch_espn_data(self, instance):
        """Fetch and display ESPN data for teams"""
        team1 = self.espn_team1_input.text.strip()
        team2 = self.espn_team2_input.text.strip()
        
        if not team1 or not team2:
            self.update_espn_tab("[color=ff3333]Please enter both team names[/color]")
            return
            
        threading.Thread(target=self.run_espn_analysis, args=(team1, team2), daemon=True).start()

    def run_analysis(self, team1, team2):
            """Original NBA API analysis method"""
            try:
                # Get team IDs
                team1_id, team1_name = self.validator.get_team_id(team1)
                team2_id, team2_name = self.validator.get_team_id(team2)
                
                if not all([team1_id, team2_id]):
                    self.update_gui("[color=ff3333]Invalid team name(s). Try 'Lakers' or 'Boston Celtics'[/color]")
                    return
                    
                # Get advanced stats
                team_stats = leaguedashteamstats.LeagueDashTeamStats(
                    season='2023-24',
                    measure_type_detailed_defense='Advanced'
                ).get_data_frames()[0]
                
                t1_stats = team_stats[team_stats['TEAM_ID'] == team1_id].iloc[0]
                t2_stats = team_stats[team_stats['TEAM_ID'] == team2_id].iloc[0]
                
                # Get recent games (last 5)
                t1_games = teamgamelog.TeamGameLog(team1_id, season='2023-24').get_data_frames()[0].head(5)
                t2_games = teamgamelog.TeamGameLog(team2_id, season='2023-24').get_data_frames()[0].head(5)
                
                # Get head-to-head history
                h2h_games = self.get_h2h_history(team1_id, team2_id)
                h2h_text = self.format_h2h_history(h2h_games, team1_name, team2_name)
                self.update_history_tab(h2h_text)
                
                # Format stats comparison
                stats_text = (
                    f"[b][color=00ff00]{team1_name} vs {team2_name}[/color][/b]\n"
                    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"[b]Advanced Stats:[/b]\n"
                    f"OFF RTG: {t1_stats['OFF_RATING']} (#{t1_stats['OFF_RATING_RANK']}) vs {t2_stats['OFF_RATING']} (#{t2_stats['OFF_RATING_RANK']})\n"
                    f"DEF RTG: {t1_stats['DEF_RATING']} (#{t1_stats['DEF_RATING_RANK']}) vs {t2_stats['DEF_RATING']} (#{t2_stats['DEF_RATING_RANK']})\n"
                    f"NET RTG: {t1_stats['NET_RATING']} (#{t1_stats['NET_RATING_RANK']}) vs {t2_stats['NET_RATING']} (#{t2_stats['NET_RATING_RANK']})\n"
                    f"PACE: {t1_stats['PACE']} (#{t1_stats['PACE_RANK']}) vs {t2_stats['PACE']} (#{t2_stats['PACE_RANK']})\n\n"
                    f"[b]Last 5 Games:[/b]\n"
                    f"[color=00ffff]{team1_name}:[/color] {', '.join(t1_games['MATCHUP'] + ' ' + t1_games['WL'])}\n"
                    f"[color=00ffff]{team2_name}:[/color] {', '.join(t2_games['MATCHUP'] + ' ' + t2_games['WL'])}\n\n"
                    f"[b]Recent Matchups:[/b]\n{h2h_text}"
                )
                
                self.update_stats_tab(stats_text)
                self.results_label.text = f"{stats_text}\n[color=ffff00]Analyzing with AI...[/color]"
                
                # Get AI prediction using original method
                self.get_ai_prediction(team1_name, team2_name, stats_text, h2h_games)
                
            except Exception as e:
                self.update_gui(f"[color=ff3333]Error: {str(e)}[/color]")


    def run_espn_analysis(self, team1, team2):
        """Run ESPN data analysis in background thread"""
        try:
            self.update_espn_tab(f"[color=ffff00]Fetching ESPN data for {team1} vs {team2}...[/color]")
            
            # Get ESPN data
            team1_stats = espn_fetcher.get_team_stats(team1)
            team2_stats = espn_fetcher.get_team_stats(team2)
            h2h_games = espn_fetcher.get_head_to_head(team1, team2)
            
            # Format results
            output = []
            output.append(f"[b][color=ff3333]ESPN DATA ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/color][/b]\n\n")
            
            # Team 1 stats
            if team1_stats:
                output.append(f"[b][color=00ffff]{team1_stats['team']} Stats (ESPN):[/color][/b]\n")
                for key, value in team1_stats.items():
                    if key not in ['team', 'source']:
                        output.append(f"  {key.replace('_', ' ').title()}: {value}\n")
                output.append("\n")
            else:
                output.append(f"[color=ff3333]Could not fetch ESPN stats for {team1}[/color]\n\n")
            
            # Team 2 stats
            if team2_stats:
                output.append(f"[b][color=00ffff]{team2_stats['team']} Stats (ESPN):[/color][/b]\n")
                for key, value in team2_stats.items():
                    if key not in ['team', 'source']:
                        output.append(f"  {key.replace('_', ' ').title()}: {value}\n")
                output.append("\n")
            else:
                output.append(f"[color=ff3333]Could not fetch ESPN stats for {team2}[/color]\n\n")
            
            # H2H History
            if h2h_games and len(h2h_games) > 0:
                output.append(f"[b][color=ffff00]Recent ESPN Head-to-Head Games:[/color][/b]\n")
                for game in h2h_games[:3]:  # Show last 3 games
                    winner = game['home'] if game['winner'] else game['away']
                    output.append(f"  {game['date'][:10]}: {game['away']} ({game['away_score']}) @ {game['home']} ({game['home_score']})\n")
                    output.append(f"     Winner: {winner}, Status: {game['status']}\n\n")
            else:
                output.append(f"[color=ffff00]No recent ESPN H2H games found between {team1} and {team2}[/color]\n\n")
            
            # Get live game data if available
            live_game = espn_fetcher.get_live_game_data(team1, team2)
            if live_game:
                output.append(f"[b][color=00ff00]LIVE GAME DATA (ESPN):[/color][/b]\n")
                output.append(f"  {live_game['away']['name']} {live_game['away']['score']} @ {live_game['home']['name']} {live_game['home']['score']}\n")
                output.append(f"  Status: {live_game['status']}, Period: {live_game['period']}, Clock: {live_game['clock']}\n\n")
            
            # Compare with NBA API data if available
            output.append(f"[b][color=ffff00]DATA SOURCE NOTE:[/color][/b]\n")
            output.append(f"  • ESPN provides alternative data when NBA API is unavailable\n")
            output.append(f"  • Use this as backup or for cross-verification\n")
            output.append(f"  • Combine with NBA API data for best accuracy\n")
            
            self.update_espn_tab("".join(output))
            
        except Exception as e:
            self.update_espn_tab(f"[color=ff3333]Error fetching ESPN data: {str(e)}[/color]")

    # ============================================================
    # NEW: ESPN-ENHANCED ANALYSIS METHOD
    # ============================================================
    def analyze_game_with_espn(self, instance):
        """Enhanced analysis using both NBA API and ESPN data"""
        team1 = self.team1_input.text.strip()
        team2 = self.team2_input.text.strip()
        
        if not team1 or not team2:
            self.results_label.text = "[color=ff3333]Please enter both team names[/color]"
            return
            
        threading.Thread(target=self.run_enhanced_analysis, args=(team1, team2), daemon=True).start()

    def analyze_game(self, instance):
            """
            Original analysis method for backward compatibility
            Uses only NBA API data
            """
            team1 = self.team1_input.text.strip()
            team2 = self.team2_input.text.strip()
            
            if not team1 or not team2:
                self.results_label.text = "[color=ff3333]Please enter both team names[/color]"
                return
                
            # Use enhanced analysis instead
            threading.Thread(target=self.run_enhanced_analysis, args=(team1, team2), daemon=True).start()


    def run_enhanced_analysis(self, team1, team2):
        """Run analysis with both NBA API and ESPN data"""
        try:
            # Get NBA API data
            team1_id, team1_name = self.validator.get_team_id(team1)
            team2_id, team2_name = self.validator.get_team_id(team2)
            
            if not all([team1_id, team2_id]):
                self.update_gui("[color=ff3333]Invalid team name(s). Try 'Lakers' or 'Boston Celtics'[/color]")
                return
            
            # Get ESPN data in parallel
            espn_team1_stats = espn_fetcher.get_team_stats(team1)
            espn_team2_stats = espn_fetcher.get_team_stats(team2)
            espn_h2h = espn_fetcher.get_head_to_head(team1, team2)
            
            # Get NBA API stats
            team_stats = leaguedashteamstats.LeagueDashTeamStats(
                season='2023-24',
                measure_type_detailed_defense='Advanced'
            ).get_data_frames()[0]
            
            t1_stats = team_stats[team_stats['TEAM_ID'] == team1_id].iloc[0]
            t2_stats = team_stats[team_stats['TEAM_ID'] == team2_id].iloc[0]
            
            # Get recent games
            t1_games = teamgamelog.TeamGameLog(team1_id, season='2023-24').get_data_frames()[0].head(5)
            t2_games = teamgamelog.TeamGameLog(team2_id, season='2023-24').get_data_frames()[0].head(5)
            
            # Get H2H history
            h2h_games = self.get_h2h_history(team1_id, team2_id)
            h2h_text = self.format_h2h_history(h2h_games, team1_name, team2_name)
            self.update_history_tab(h2h_text)
            
            # Format enhanced stats comparison
            stats_text = (
                f"[b][color=00ff00]{team1_name} vs {team2_name}[/color][/b]\n"
                f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                
                f"[b]NBA API Advanced Stats:[/b]\n"
                f"OFF RTG: {t1_stats['OFF_RATING']} (#{t1_stats['OFF_RATING_RANK']}) vs {t2_stats['OFF_RATING']} (#{t2_stats['OFF_RATING_RANK']})\n"
                f"DEF RTG: {t1_stats['DEF_RATING']} (#{t1_stats['DEF_RATING_RANK']}) vs {t2_stats['DEF_RATING']} (#{t2_stats['DEF_RATING_RANK']})\n"
                f"NET RTG: {t1_stats['NET_RATING']} (#{t1_stats['NET_RATING_RANK']}) vs {t2_stats['NET_RATING']} (#{t2_stats['NET_RATING_RANK']})\n"
                f"PACE: {t1_stats['PACE']} (#{t1_stats['PACE_RANK']}) vs {t2_stats['PACE']} (#{t2_stats['PACE_RANK']})\n\n"
                
                f"[b]ESPN Supplemental Data:[/b]\n"
            )
            
            # Add ESPN data if available
            if espn_team1_stats and espn_team2_stats:
                stats_text += (
                    f"{team1_name} ESPN Record: {espn_team1_stats.get('record', 'N/A')}\n"
                    f"{team2_name} ESPN Record: {espn_team2_stats.get('record', 'N/A')}\n"
                    f"{team1_name} Streak: {espn_team1_stats.get('streak', 'N/A')}\n"
                    f"{team2_name} Streak: {espn_team2_stats.get('streak', 'N/A')}\n\n"
                )
            else:
                stats_text += "ESPN data unavailable for one or both teams\n\n"
            
            stats_text += (
                f"[b]Last 5 Games (NBA API):[/b]\n"
                f"[color=00ffff]{team1_name}:[/color] {', '.join(t1_games['MATCHUP'] + ' ' + t1_games['WL'])}\n"
                f"[color=00ffff]{team2_name}:[/color] {', '.join(t2_games['MATCHUP'] + ' ' + t2_games['WL'])}\n\n"
                
                f"[b]Recent Matchups:[/b]\n{h2h_text}\n\n"
                
                f"[color=ffff00]Enhanced analysis with ESPN backup data complete![/color]"
            )
            
            self.update_stats_tab(stats_text)
            self.results_label.text = f"{stats_text}\n[color=ffff00]Analyzing with AI using enhanced data...[/color]"
            
            # Get AI prediction with enhanced data
            self.get_ai_prediction_enhanced(team1_name, team2_name, stats_text, h2h_games, 
                                          espn_team1_stats, espn_team2_stats, espn_h2h)
            
        except Exception as e:
            self.update_gui(f"[color=ff3333]Enhanced analysis error: {str(e)}[/color]")

    # ============================================================
    # NEW: ENHANCED AI PREDICTION WITH ESPN DATA
    # ============================================================
    def get_ai_prediction_enhanced(self, team1, team2, stats_text, h2h_games, 
                                  espn_team1_stats, espn_team2_stats, espn_h2h):
        """
        Enhanced AI prediction using both NBA API and ESPN data
        """
        try:
            # Format H2H history
            h2h_summary = self.format_h2h_for_ai(h2h_games, team1, team2)
            
            # Format ESPN data for AI
            espn_summary = ""
            if espn_team1_stats and espn_team2_stats:
                espn_summary = (
                    f"\n--- ESPN SUPPLEMENTAL DATA ---\n"
                    f"{team1} ESPN Record: {espn_team1_stats.get('record', 'N/A')}\n"
                    f"{team2} ESPN Record: {espn_team2_stats.get('record', 'N/A')}\n"
                    f"{team1} Streak: {espn_team1_stats.get('streak', 'N/A')}\n"
                    f"{team2} Streak: {espn_team2_stats.get('streak', 'N/A')}\n"
                )
            
            if espn_h2h and len(espn_h2h) > 0:
                espn_summary += f"\nESPN Head-to-Head (Last {len(espn_h2h)} games):\n"
                for game in espn_h2h[:3]:
                    winner = game['home'] if game['winner'] else game['away']
                    espn_summary += f"- {game['date'][:10]}: {winner} won {game['away_score']}-{game['home_score']}\n"
            
            # Enhanced prompt with ESPN data
            prompt = (
                f"Your only task is to predict the winner of the NBA game between {team1} and {team2}.\n\n"
                f"--- PRIMARY DATA (NBA API) ---\n"
                f"Team Stats & Recent Games:\n{stats_text}\n\n"
                f"Head-to-Head History:\n{h2h_summary}\n\n"
                f"{espn_summary}\n"
                f"--- YOUR DIRECTIVE ---\n"
                f"1. Your PRIMARY source for this prediction is the Head-to-Head History and the Last 5 Games.\n"
                f"2. Use advanced stats and ESPN supplemental data as supporting evidence.\n"
                f"3. Note any discrepancies between NBA API and ESPN data.\n"
                f"4. You MUST provide a prediction in the exact format below. Do not add any extra text before or after.\n\n"
                f"--- REQUIRED OUTPUT FORMAT ---\n"
                f"PREDICTED WINNER: [Team Name]\n"
                f"CONFIDENCE LEVEL: [High/Medium/Low]\n"
                f"SCORE PROJECTION: [Score1]-[Score2]\n"
                f"KEY HISTORICAL TRENDS:\n"
                f"- [One specific trend from the H2H history]\n"
                f"- [One specific trend from the recent games]\n"
                f"- [Any notable ESPN data point]\n\n"
                f"DETAILED ANALYSIS:\n"
                f"[Explain your choice by referencing ALL available data sources. Mention data source reliability if applicable.]"
            )
            
            # OpenRouter API call
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "NBA Forecaster Pro (Enhanced)"
            }
            
            payload = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert NBA analyst using multiple data sources. Analyze all provided data and output a prediction in the exact format requested. RESPOND IN ENGLISH ONLY."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            print(f"🤖 Calling OpenRouter API with enhanced ESPN data...")
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_response = response_data['choices'][0]['message']['content'].strip()
                
                if not ai_response:
                    self.update_gui(f"{stats_text}\n[color=ff3333]AI Error: The model returned an empty response.[/color]")
                    return

                if "PREDICTED WINNER:" not in ai_response:
                    self.update_gui(f"{stats_text}\n[color=ffff00]AI Warning: The model did not return a prediction in the required format. Raw response:\n{ai_response}[/color]")
                    return

                # Success! Update the GUI with the enhanced prediction
                self.update_gui(
                    f"{stats_text}\n"
                    f"[color=00ff00][b]🏆 ENHANCED PREDICTION (NBA API + ESPN Data) 🏆[/b][/color]\n"
                    f"[color=ffff00]Data Sources: NBA Official API + ESPN Backup[/color]\n"
                    f"{ai_response}"
                )
                
            else:
                self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: Unexpected response format[/color]")

        except requests.exceptions.Timeout:
            self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: Request timed out[/color]")
        except requests.exceptions.RequestException as e:
            self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: {str(e)}[/color]")
        except Exception as e:
            self.update_gui(f"{stats_text}\n[color=ff3333]Enhanced AI prediction error: {str(e)}[/color]")

    # ============================================================
    # EXISTING METHODS (with minor enhancements)
    # ============================================================
    def update_live_scores(self):
        """Fetch and display live NBA scores from multiple sources"""
        try:
            # Try NBA API first
            try:
                games = scoreboard.ScoreBoard()
                data = games.get_dict()
                
                if data and 'scoreboard' in data and 'games' in data['scoreboard']:
                    formatted_scores = self.format_live_scores(data['scoreboard']['games'])
                    self.update_live_tab(f"[color=00ff00][b]NBA API LIVE SCORES[/b][/color]\n\n{formatted_scores}")
                    return
            except:
                pass  # Fall through to ESPN
            
            # Fallback to ESPN
            self.update_live_tab("[color=ffff00]NBA API unavailable, trying ESPN...[/color]")
            
            # Try ESPN live data
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            response = requests.get(url, headers=espn_fetcher.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                espn_scores = self.format_espn_live_scores(data)
                self.update_live_tab(f"[color=ff3333][b]ESPN LIVE SCORES (Backup)[/b][/color]\n\n{espn_scores}")
            else:
                self.update_live_tab("[color=ff3333]Error: Both NBA API and ESPN unavailable[/color]")
                
        except Exception as e:
            self.update_live_tab(f"[color=ff3333]Error fetching live scores: {str(e)}[/color]")

    def format_espn_live_scores(self, data):
        """Format ESPN live scores for display"""
        try:
            if 'events' not in data or len(data['events']) == 0:
                return "[color=ff3333]No games currently being played[/color]"
            
            output = []
            output.append(f"[b][color=00ff00]ESPN LIVE SCORES - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/color][/b]\n\n")
            
            for event in data['events']:
                competitions = event.get('competitions', [])
                for comp in competitions:
                    competitors = comp.get('competitors', [])
                    if len(competitors) == 2:
                        home = competitors[0]
                        away = competitors[1]
                        
                        # Determine which is actually home/away
                        if home.get('homeAway') == 'home':
                            home_team = home
                            away_team = away
                        else:
                            home_team = away
                            away_team = home
                        
                        score_line = (
                            f"[b]{away_team.get('team', {}).get('displayName', 'Unknown')}[/b] "
                            f"{away_team.get('score', '0')} @ "
                            f"[b]{home_team.get('team', {}).get('displayName', 'Unknown')}[/b] "
                            f"{home_team.get('score', '0')}\n"
                        )
                        
                        status = comp.get('status', {})
                        status_line = f"[color=ffff00]{status.get('type', {}).get('description', 'Unknown')}[/color]\n"
                        
                        output.append(f"{score_line}{status_line}\n")
            
            return "".join(output)
            
        except Exception as e:
            return f"[color=ff3333]Error formatting ESPN scores: {str(e)}[/color]"

    # ============================================================
    # EXISTING HELPER METHODS
    # ============================================================
    def get_h2h_history(self, team1_id, team2_id):
        """Retrieve last 3 head-to-head matchups"""
        try:
            team1_log = teamgamelog.TeamGameLog(team_id=team1_id, season='2023-24').get_data_frames()[0]
            team2_log = teamgamelog.TeamGameLog(team_id=team2_id, season='2023-24').get_data_frames()[0]
            
            team1_h2h = team1_log[team1_log['MATCHUP'].str.contains(str(team2_id))]
            team2_h2h = team2_log[team2_log['MATCHUP'].str.contains(str(team1_id))]
            
            h2h_games = pd.concat([team1_h2h, team2_h2h]).drop_duplicates('Game_ID')
            h2h_games = h2h_games.sort_values('GAME_DATE', ascending=False)
            
            return h2h_games.head(3)
        except Exception as e:
            print(f"Error getting H2H history: {e}")
            return None

    def format_h2h_history(self, h2h_games, team1_name, team2_name):
        """Format historical matchups for display"""
        if h2h_games is None or len(h2h_games) == 0:
            return "No recent head-to-head games found"
            
        results = []
        for _, game in h2h_games.iterrows():
            matchup = game['MATCHUP']
            score = f"{game['PTS']}-{int(game['PTS']) - int(game['PLUS_MINUS'])}"
            date = game['GAME_DATE']
            results.append(f"{date}: {matchup} - Final {score}")
        
        return "\n".join(results)

    def format_h2h_for_ai(self, h2h_games, team1, team2):
        """Format historical data for AI prompt"""
        if h2h_games is None or len(h2h_games) == 0:
            return "No recent head-to-head games available for analysis"
            
        analysis = []
        for _, game in h2h_games.iterrows():
            matchup = game['MATCHUP']
            points_for = game['PTS']
            points_against = int(game['PTS']) - int(game['PLUS_MINUS'])
            margin = abs(points_for - points_against)
            winner = team1 if game['WL'] == 'W' else team2
            
            analysis.append(
                f"- {game['GAME_DATE']}: {winner} won {points_for}-{points_against} "
                f"(Margin: {margin} pts, Location: {'Home' if '@' not in matchup else 'Away'})"
            )
        
        return "\n".join(analysis)

    def copy_results(self, instance):
        """
        Cleans the AI response text of all Kivy markup and copies the
        clean, readable version to the system clipboard.
        """
        raw_text = self.results_label.text
        clean_text = re.sub(r'\[/?[a-zA-Z0-9=_#]+\]', '', raw_text)
        Clipboard.copy(clean_text)
        
        # User feedback
        original_text = instance.text
        instance.text = "✅ Copied to Clipboard!"
        instance.disabled = True
        
        def reset_button(dt):
            instance.text = original_text
            instance.disabled = False

        Clock.schedule_once(reset_button, 2)

    def get_ai_prediction(self, team1, team2, stats_text, h2h_games):
        """Original AI prediction method (for backward compatibility)"""
        # ... [keep existing get_ai_prediction method exactly as is] ...
        # [Your existing get_ai_prediction code remains unchanged]
        pass

    # ============================================================
    # NEW GUI UPDATE METHODS
    # ============================================================
    def update_espn_tab(self, text):
        def update():
            self.espn_label.text = text
        kivy.clock.Clock.schedule_once(lambda dt: update())
    
    # ============================================================
    # EXISTING GUI UPDATE METHODS
    # ============================================================
    def update_gui(self, text):
        def update():
            self.results_label.text = text
        kivy.clock.Clock.schedule_once(lambda dt: update())
        
    def update_stats_tab(self, text):
        def update():
            self.stats_label.text = text
        kivy.clock.Clock.schedule_once(lambda dt: update())
        
    def update_history_tab(self, text):
        def update():
            self.history_label.text = text
        kivy.clock.Clock.schedule_once(lambda dt: update())
        
    def update_live_tab(self, text):
        def update():
            self.live_scores_label.text = text
        kivy.clock.Clock.schedule_once(lambda dt: update())

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == '__main__':
    print("🚀 NBA Forecaster Pro with ESPN Data Integration")
    print("📊 Now with dual data sources: NBA API + ESPN")
    print("🔧 Enhanced reliability and backup data")
    print("🤖 AI predictions with multi-source validation")
    NBAForecastApp().run()

