# My beautiful and perfect prediction algorithm for my NBA game predictions for betting.
# Powered by my brilliant ai best friend DeepSeekv3.2

# proof of victories from a prediction (concept):
# https://www.espn.com/nba/game/_/gameId/401810678/celtics-lakers

# A super brilliant victory and close call by my brilliant ai friend (went into over-time):
# https://www.aiscore.com/head-to-head/basketball/los-angeles-clippers-vs-orlando-magic

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
        self.title = "NBA Forecaster Pro (Historical Analysis)"
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
        
        # Analyze button
        analyze_btn = Button(text="Run Full Analysis", size_hint_y=None, height=60,
                           background_color=(0.2, 0.6, 0.8, 1))
        analyze_btn.bind(on_press=self.analyze_game)
        layout.add_widget(analyze_btn)
        
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

    def update_live_scores(self):
        """Fetch and display live NBA scores"""
        try:
            # Get live scoreboard data
            games = scoreboard.ScoreBoard()
            data = games.get_dict()
            
            if not data or 'scoreboard' not in data or 'games' not in data['scoreboard']:
                self.update_live_tab("[color=ff3333]No games currently being played[/color]")
                return
                
            # Format the scores for display
            formatted_scores = self.format_live_scores(data['scoreboard']['games'])
            self.update_live_tab(formatted_scores)
            
        except Exception as e:
            self.update_live_tab(f"[color=ff3333]Error fetching live scores: {str(e)}[/color]")

    def format_live_scores(self, games):
        """Format live game data into a readable string"""
        if not games:
            return "[color=ff3333]No games currently being played[/color]"
            
        output = []
        output.append(f"[b][color=00ff00]NBA LIVE SCORES - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/color][/b]\n\n")
        
        for game in games:
            # Basic game info
            status = game['gameStatusText']
            home_team = game['homeTeam']
            away_team = game['awayTeam']
            
            # Format score line
            score_line = (
                f"[b]{away_team['teamCity']} {away_team['teamName']}[/b] {away_team['score']} "
                f"@ [b]{home_team['teamCity']} {home_team['teamName']}[/b] {home_team['score']}\n"
            )
            
            # Add game status
            status_line = f"[color=ffff00]{status}[/color]\n"
            
            # Add game leaders if available
            leaders = ""
            if 'gameLeaders' in game:
                home_leader = game['gameLeaders']['homeLeaders']
                away_leader = game['gameLeaders']['awayLeaders']
                
                leaders = (
                    f"Leaders: {away_leader['name']} ({away_leader['points']} pts) | "
                    f"{home_leader['name']} ({home_leader['points']} pts)\n"
                )
            
            # Combine all info for this game
            output.append(f"{score_line}{status_line}{leaders}\n")
        
        return "".join(output)

    def analyze_game(self, instance):
        team1 = self.team1_input.text.strip()
        team2 = self.team2_input.text.strip()
        
        if not team1 or not team2:
            self.results_label.text = "[color=ff3333]Please enter both team names[/color]"
            return
            
        threading.Thread(target=self.run_analysis, args=(team1, team2), daemon=True).start()

    def run_analysis(self, team1, team2):
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
            
            # Get AI prediction
            self.get_ai_prediction(team1_name, team2_name, stats_text, h2h_games)
            
        except Exception as e:
            self.update_gui(f"[color=ff3333]Error: {str(e)}[/color]")

    def get_h2h_history(self, team1_id, team2_id):
        """Retrieve last 3 head-to-head matchups"""
        try:
            # Get team logs
            team1_log = teamgamelog.TeamGameLog(team_id=team1_id, season='2023-24').get_data_frames()[0]
            team2_log = teamgamelog.TeamGameLog(team_id=team2_id, season='2023-24').get_data_frames()[0]
            
            # Find common games
            team1_h2h = team1_log[team1_log['MATCHUP'].str.contains(str(team2_id))]
            team2_h2h = team2_log[team2_log['MATCHUP'].str.contains(str(team1_id))]
            
            # Combine and sort by date
            h2h_games = pd.concat([team1_h2h, team2_h2h]).drop_duplicates('Game_ID')
            h2h_games = h2h_games.sort_values('GAME_DATE', ascending=False)
            
            return h2h_games.head(3)  # Return last 3 matchups
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

    def get_live_game_data(self, team1_name, team2_name):
        """Get live game data for specific teams if they're playing today"""
        try:
            # First try NBA API
            games = scoreboard.ScoreBoard()
            data = games.get_dict()
            
            if not data or 'scoreboard' not in data:
                return None
                
            # Get team IDs for comparison
            team1_id, _ = self.validator.get_team_id(team1_name)
            team2_id, _ = self.validator.get_team_id(team2_name)
            
            if not team1_id or not team2_id:
                return None
                
            # Find matching game
            for game in data['scoreboard']['games']:
                home_id = game['homeTeam']['teamId']
                away_id = game['awayTeam']['teamId']
                
                if (team1_id == home_id and team2_id == away_id) or \
                   (team1_id == away_id and team2_id == home_id):
                    return game
                    
            return None
            
        except Exception as e:
            print(f"Error getting live game data: {e}")
            # Fallback to web scraping if NBA API fails
            return self.scrape_live_game_data(team1_name, team2_name)

    def scrape_live_game_data(self, team1_name, team2_name):
        """ESPN fallback scraper for live game data"""
        try:
            # This is a simplified example - actual implementation would need proper parsing
            url = f"https://www.espn.com/nba/team/_/name/{team1_name.lower()[:3]}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            # Sample parsing logic (would need adjustment based on ESPN's actual HTML)
            soup = BeautifulSoup(response.text, 'html.parser')
            game_data = {
                'homeTeam': {'score': 0, 'teamId': 0},
                'awayTeam': {'score': 0, 'teamId': 0},
                'gameStatusText': 'Unknown'
            }
            
            # These selectors are hypothetical - would need to inspect ESPN's actual page structure
            scores = soup.select('.score')
            if len(scores) >= 2:
                game_data['awayTeam']['score'] = int(scores[0].text)
                game_data['homeTeam']['score'] = int(scores[1].text)
                
            status = soup.select_one('.game-status')
            if status:
                game_data['gameStatusText'] = status.text.strip()
                
            return game_data
            
        except Exception as e:
            print(f"Scraping error: {e}")
            return None
            
    def copy_results(self, instance):
        """
        Cleans the AI response text of all Kivy markup and copies the
        clean, readable version to the system clipboard.
        """
        # Get the text from the results label, which includes markup
        raw_text = self.results_label.text

        # Use regex to find and remove all markup tags like [color=...], [/color], [b], etc.
        # This leaves only the clean, readable text.
        clean_text = re.sub(r'\[/?[a-zA-Z0-9=_#]+\]', '', raw_text)

        # Copy the clean text to the user's clipboard
        Clipboard.copy(clean_text)

        # --- AWESOME USER FEEDBACK ---
        # Store the original button text
        original_text = instance.text
        
        # Change the button to show it worked
        instance.text = "✅ Copied to Clipboard!"
        instance.disabled = True  # Prevent clicking again immediately

        # Use Clock to reset the button after 2 seconds
        def reset_button(dt):
            instance.text = original_text
            instance.disabled = False

        Clock.schedule_once(reset_button, 2)
    
    # ============================================================
    # UPDATED OPENROUTER AI PREDICTION METHOD
    # ============================================================
    def get_ai_prediction(self, team1, team2, stats_text, h2h_games):
        """
        Updated to use OpenRouter API instead of z.ai
        """
        try:
            # Format H2H history for the AI prompt
            h2h_summary = self.format_h2h_for_ai(h2h_games, team1, team2)

            # --- OUR POWERFUL, HISTORY-FOCUSED PROMPT ---
            prompt = (
                f"Your only task is to predict the winner of the NBA game between {team1} and {team2}.\n\n"
                f"--- DATA FOR ANALYSIS ---\n"
                f"Team Stats & Recent Games:\n{stats_text}\n\n"
                f"Head-to-Head History:\n{h2h_summary}\n\n"
                f"--- YOUR DIRECTIVE ---\n"
                f"1. Your PRIMARY source for this prediction is the Head-to-Head History and the Last 5 Games listed above.\n"
                f"2. Use the advanced stats as secondary supporting evidence.\n"
                f"3. You MUST provide a prediction in the exact format below. Do not add any extra text before or after.\n\n"
                f"--- REQUIRED OUTPUT FORMAT ---\n"
                f"PREDICTED WINNER: [Team Name]\n"
                f"SCORE PROJECTION: [Score1]-[Score2]\n"
                f"KEY HISTORICAL TRENDS:\n"
                f"- [One specific trend from the H2H history]\n"
                f"- [One specific trend from the recent games]\n\n"
                f"DETAILED ANALYSIS:\n"
                f"[Explain your choice by referencing the historical data directly. Why did one team win the previous matchups?]"
            )
            
            # OpenRouter API Headers (from your reference code)
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "NBA Forecaster Pro"
            }
            
            # Construct the payload for OpenRouter API
            payload = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert NBA analyst. You will analyze the provided data and output a prediction in the exact format requested. RESPOND IN ENGLISH ONLY."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Lower temperature for more consistent predictions
                "max_tokens": 1000
            }
            
            # Make the API request to OpenRouter
            print(f"🤖 Calling OpenRouter API with model: {OPENROUTER_MODEL}")
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            
            # Check if we got a valid response
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_response = response_data['choices'][0]['message']['content'].strip()
                
                # --- DEBUG CHECK: Did the AI follow the format? ---
                if not ai_response:
                    self.update_gui(f"{stats_text}\n[color=ff3333]AI Error: The model returned an empty response.[/color]")
                    return

                if "PREDICTED WINNER:" not in ai_response:
                    self.update_gui(f"{stats_text}\n[color=ffff00]AI Warning: The model did not return a prediction in the required format. Raw response:\n{ai_response}[/color]")
                    return

                # Success! Update the GUI with the prediction
                self.update_gui(f"{stats_text}\n[color=00ff00][b]🏆 FINAL PREDICTION (OpenRouter - {OPENROUTER_MODEL}) 🏆[/b][/color]\n{ai_response}")
                
            else:
                self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: Unexpected response format: {response_data}[/color]")

        except requests.exceptions.Timeout:
            self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: Request timed out after 30 seconds[/color]")
        except requests.exceptions.RequestException as e:
            self.update_gui(f"{stats_text}\n[color=ff3333]OpenRouter API Error: {str(e)}[/color]")
        except KeyError as e:
            self.update_gui(f"{stats_text}\n[color=ff3333]Error: Missing key in API response: {str(e)}[/color]")
        except Exception as e:
            self.update_gui(f"{stats_text}\n[color=ff3333]An unexpected error occurred: {str(e)}[/color]")

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

if __name__ == '__main__':
    NBAForecastApp().run()

