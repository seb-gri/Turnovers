import sqlite3

def initialize_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Création de la table matches
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        match_date TEXT,
        home_team TEXT,
        away_team TEXT,
        competition_id INTEGER,
        season_id INTEGER,
        match_week INTEGER
    )''')

    # Création de la table turnovers avec les nouvelles colonnes
    cursor.execute('''CREATE TABLE IF NOT EXISTS turnovers (
        team_name TEXT,
        match_id INTEGER,
        Miscontrol INTEGER DEFAULT 0,
        Pass INTEGER DEFAULT 0,
        Dribble INTEGER DEFAULT 0,
        Shot INTEGER DEFAULT 0,
        FOREIGN KEY(match_id) REFERENCES matches(match_id)
    )''')

    # Création de la table player_turnovers
    cursor.execute('''CREATE TABLE IF NOT EXISTS player_turnovers (
        event_id TEXT PRIMARY KEY,
        player_id INTEGER,
        team_name TEXT,
        match_id INTEGER,
        player TEXT,
        position TEXT,
        period INTEGER,
        minute INTEGER,
        second INTEGER,
        location TEXT,
        Miscontrol INTEGER DEFAULT 0,
        Pass INTEGER DEFAULT 0,
        Dribble INTEGER DEFAULT 0,
        Shot INTEGER DEFAULT 0,
        FOREIGN KEY(match_id) REFERENCES matches(match_id)
    )''')

    # Création de la table player_playtime
    cursor.execute('''CREATE TABLE IF NOT EXISTS player_playtime (
        player_id INTEGER,
        match_id INTEGER,
        team_name TEXT,
        player_name TEXT,
        match TEXT,
        playtime INTEGER,
        PRIMARY KEY (player_id, match_id),
        FOREIGN KEY(match_id) REFERENCES matches(match_id)
    )''')

    # Création de la table player_info
    cursor.execute('''CREATE TABLE IF NOT EXISTS player_info (
        player_id INTEGER PRIMARY KEY,
        player_name TEXT,
        team_name TEXT,
        primary_position TEXT
    )''')

    # Création de la table relances_joueur pour les relances depuis le propre camp
    cursor.execute('''CREATE TABLE IF NOT EXISTS relances_joueur (
        pass_id TEXT PRIMARY KEY,
        player_id INTEGER,
        player_name TEXT,
        team_name TEXT,
        match_id INTEGER,
        match_teams TEXT,
        match_date TEXT,
        pass_result TEXT,
        recipient_name TEXT,
        start_x REAL,
        start_y REAL,
        end_x REAL,
        end_y REAL,
        under_pressure INTEGER,
        FOREIGN KEY(match_id) REFERENCES matches(match_id),
        FOREIGN KEY(player_id) REFERENCES player_info(player_id)
    )''')

    conn.commit()
    conn.close()
