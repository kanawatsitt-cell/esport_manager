from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'Smart_Office.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS Teams (
        team_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT    NOT NULL UNIQUE,
        game      TEXT    NOT NULL,
        country   TEXT    NOT NULL,
        founded   DATE    NOT NULL,
        logo_url  TEXT
    );

    CREATE TABLE IF NOT EXISTS Players (
        player_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id     INTEGER NOT NULL,
        ign         TEXT    NOT NULL UNIQUE,
        real_name   TEXT    NOT NULL,
        role        TEXT    NOT NULL,
        nationality TEXT    NOT NULL,
        salary      INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Gear (
        gear_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id     INTEGER NOT NULL,
        gear_type     TEXT    NOT NULL,
        brand         TEXT    NOT NULL,
        model         TEXT    NOT NULL,
        purchase_date DATE    NOT NULL,
        FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Tournaments (
        tournament_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL,
        game            TEXT    NOT NULL,
        start_date      DATE    NOT NULL,
        end_date        DATE    NOT NULL,
        prize_pool      INTEGER NOT NULL DEFAULT 0,
        location        TEXT    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Match_Results (
        result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER NOT NULL,
        team_id       INTEGER NOT NULL,
        placement     INTEGER NOT NULL,
        points        INTEGER NOT NULL DEFAULT 0,
        prize_won     INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id) ON DELETE CASCADE,
        FOREIGN KEY (team_id)       REFERENCES Teams(team_id) ON DELETE CASCADE
    );
    """)

    # Seed data only if empty
    if c.execute("SELECT COUNT(*) FROM Teams").fetchone()[0] == 0:
        c.executescript("""
        INSERT INTO Teams (team_name, game, country, founded) VALUES
            ('Neon Wolves',    'Valorant',       'Thailand',     '2020-03-15'),
            ('Shadow Force',   'CS2',            'South Korea',  '2019-07-22'),
            ('Dragon Squad',   'League of Legends','China',      '2018-01-10'),
            ('Iron Titans',    'Dota 2',         'USA',          '2017-11-05'),
            ('Pixel Phantoms', 'Valorant',       'Brazil',       '2021-06-01'),
            ('Cyber Aces',     'CS2',            'Russia',       '2016-09-30'),
            ('Storm Rising',   'League of Legends','Europe',     '2020-02-14'),
            ('Ghost Protocol', 'Dota 2',         'Thailand',     '2022-04-20'),
            ('Red Eclipse',    'Valorant',       'Japan',        '2021-08-08'),
            ('Zero Hour',      'CS2',            'Germany',      '2019-05-17');

        INSERT INTO Players (team_id, ign, real_name, role, nationality, salary) VALUES
            (1,'NightHawk',  'Somchai Kaewpan',  'Duelist',    'Thai',       45000),
            (1,'BladeX',     'Wichai Sombat',    'Controller', 'Thai',       40000),
            (1,'ViperKing',  'Nattapong Saree',  'Initiator',  'Thai',       38000),
            (2,'ShadowByte', 'Kim Minjun',       'AWPer',      'Korean',     70000),
            (2,'NanoStrike', 'Park Seojun',      'Rifler',     'Korean',     65000),
            (3,'DragonFire', 'Wang Wei',         'Mid',        'Chinese',    90000),
            (3,'JadeCarry',  'Li Xiao',          'ADC',        'Chinese',    85000),
            (4,'TitanSmash', 'John Steel',       'Carry',      'American',   80000),
            (5,'PhantomX',   'Rafael Costa',     'Duelist',    'Brazilian',  55000),
            (6,'AceStrike',  'Ivan Petrov',      'Rifler',     'Russian',    60000),
            (1,'GhostStep',  'Apirak Jaidee',    'Sentinel',   'Thai',       42000),
            (2,'IronSight',  'Choi Yoongi',      'IGL',        'Korean',     72000);

        INSERT INTO Gear (player_id, gear_type, brand, model, purchase_date) VALUES
            (1, 'Mouse',    'Logitech', 'G Pro X Superlight', '2024-01-10'),
            (1, 'Keyboard', 'Razer',    'BlackWidow V3',      '2024-01-10'),
            (2, 'Mouse',    'Zowie',    'EC2-C',              '2023-11-05'),
            (3, 'Headset',  'HyperX',  'Cloud Alpha',        '2023-09-20'),
            (4, 'Mouse',    'SteelSeries','Rival 600',        '2024-02-01'),
            (4, 'Monitor',  'ASUS',    'ROG Swift 360Hz',    '2023-08-15'),
            (5, 'Mouse',    'Finalmouse','Ultralight 2',      '2024-03-01'),
            (6, 'Keyboard', 'Ducky',    'One 2 Mini',         '2023-07-11'),
            (7, 'Headset',  'Sennheiser','HD 560S',           '2023-12-25'),
            (8, 'Mouse',    'Logitech', 'G303 Shroud',        '2024-01-20'),
            (9, 'Monitor',  'BenQ',    'XL2546K',            '2024-02-10'),
            (10,'Keyboard', 'Leopold',  'FC900R',             '2023-10-05');

        INSERT INTO Tournaments (name, game, start_date, end_date, prize_pool, location) VALUES
            ('VCT Bangkok 2024',         'Valorant',        '2024-03-01','2024-03-10', 500000, 'Bangkok'),
            ('ESL One Katowice 2024',    'CS2',             '2024-02-14','2024-02-18', 750000, 'Katowice'),
            ('Worlds 2024',              'League of Legends','2024-10-01','2024-11-03',2000000,'Seoul'),
            ('The International 2024',  'Dota 2',          '2024-09-05','2024-09-22',3000000,'Copenhagen'),
            ('VCT Pacific 2024',         'Valorant',        '2024-04-01','2024-06-30', 800000,'Seoul'),
            ('BLAST Premier Spring 2024','CS2',             '2024-01-22','2024-02-04', 425000,'London'),
            ('LCK Spring 2024',          'League of Legends','2024-01-17','2024-04-14', 300000,'Seoul'),
            ('ESL One Birmingham 2024',  'Dota 2',          '2024-05-01','2024-05-05', 500000,'Birmingham'),
            ('VCT Masters Madrid 2024',  'Valorant',        '2024-03-11','2024-03-24', 650000,'Madrid'),
            ('IEM Cologne 2024',         'CS2',             '2024-07-09','2024-07-21', 500000,'Cologne');

        INSERT INTO Match_Results (tournament_id, team_id, placement, points, prize_won) VALUES
            (1,1,1,100,200000),(1,5,2, 75,100000),(1,9,3, 50, 50000),
            (2,2,1,100,300000),(2,6,2, 75,150000),(2,10,3,50, 75000),
            (3,3,1,100,800000),(3,7,2, 75,400000),
            (4,4,1,100,1200000),(4,8,2,75,600000),
            (5,1,2, 75,200000),(5,9,3, 50,100000),
            (6,2,1,100,170000),(6,6,3, 50, 85000),
            (7,3,2, 75,120000),(7,7,1,100,180000),
            (8,4,1,100,200000),(8,8,3, 50,100000),
            (9,1,3, 50,130000),(9,5,1,100,260000),
            (10,2,2,75,200000),(10,10,4,30, 50000);
        """)

    conn.commit()
    conn.close()

# ─── DASHBOARD ──────────────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    conn = get_db()
    stats = {
        'teams':       conn.execute("SELECT COUNT(*) FROM Teams").fetchone()[0],
        'players':     conn.execute("SELECT COUNT(*) FROM Players").fetchone()[0],
        'tournaments': conn.execute("SELECT COUNT(*) FROM Tournaments").fetchone()[0],
        'total_prize': conn.execute("SELECT COALESCE(SUM(prize_won),0) FROM Match_Results").fetchone()[0],
    }
    top_teams = conn.execute("""
        SELECT t.team_name, t.game, t.country,
               COUNT(DISTINCT p.player_id) AS player_count,
               COALESCE(SUM(mr.prize_won),0) AS total_prize,
               COALESCE(SUM(mr.points),0)    AS total_points
        FROM Teams t
        LEFT JOIN Players p      ON t.team_id = p.team_id
        LEFT JOIN Match_Results mr ON t.team_id = mr.team_id
        GROUP BY t.team_id
        ORDER BY total_points DESC
        LIMIT 5
    """).fetchall()
    recent_results = conn.execute("""
        SELECT t.team_name, tn.name AS tournament_name, mr.placement, mr.prize_won, tn.game
        FROM Match_Results mr
        JOIN Teams t       ON mr.team_id = t.team_id
        JOIN Tournaments tn ON mr.tournament_id = tn.tournament_id
        ORDER BY mr.result_id DESC LIMIT 8
    """).fetchall()
    conn.close()
    return render_template('dashboard.html', stats=stats, top_teams=top_teams, recent_results=recent_results)

# ─── TEAMS ───────────────────────────────────────────────────────────────────
@app.route('/teams')
def teams():
    conn = get_db()
    rows = conn.execute("""
        SELECT t.*, COUNT(p.player_id) AS player_count
        FROM Teams t LEFT JOIN Players p ON t.team_id = p.team_id
        GROUP BY t.team_id ORDER BY t.team_name
    """).fetchall()
    conn.close()
    return render_template('teams.html', teams=rows)

@app.route('/teams/add', methods=['POST'])
def add_team():
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO Teams (team_name,game,country,founded) VALUES (?,?,?,?)",
                 (d['team_name'], d['game'], d['country'], d['founded']))
    conn.commit(); conn.close()
    return redirect(url_for('teams'))

@app.route('/teams/edit/<int:tid>', methods=['POST'])
def edit_team(tid):
    d = request.form
    conn = get_db()
    conn.execute("UPDATE Teams SET team_name=?,game=?,country=?,founded=? WHERE team_id=?",
                 (d['team_name'], d['game'], d['country'], d['founded'], tid))
    conn.commit(); conn.close()
    return redirect(url_for('teams'))

@app.route('/teams/delete/<int:tid>', methods=['POST'])
def delete_team(tid):
    conn = get_db()
    conn.execute("DELETE FROM Teams WHERE team_id=?", (tid,))
    conn.commit(); conn.close()
    return redirect(url_for('teams'))

# ─── PLAYERS ─────────────────────────────────────────────────────────────────
@app.route('/players')
def players():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, t.team_name FROM Players p
        JOIN Teams t ON p.team_id = t.team_id ORDER BY t.team_name, p.ign
    """).fetchall()
    teams = conn.execute("SELECT team_id, team_name FROM Teams ORDER BY team_name").fetchall()
    conn.close()
    return render_template('players.html', players=rows, teams=teams)

@app.route('/players/add', methods=['POST'])
def add_player():
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO Players (team_id,ign,real_name,role,nationality,salary) VALUES (?,?,?,?,?,?)",
                 (d['team_id'], d['ign'], d['real_name'], d['role'], d['nationality'], d['salary']))
    conn.commit(); conn.close()
    return redirect(url_for('players'))

@app.route('/players/edit/<int:pid>', methods=['POST'])
def edit_player(pid):
    d = request.form
    conn = get_db()
    conn.execute("UPDATE Players SET team_id=?,ign=?,real_name=?,role=?,nationality=?,salary=? WHERE player_id=?",
                 (d['team_id'], d['ign'], d['real_name'], d['role'], d['nationality'], d['salary'], pid))
    conn.commit(); conn.close()
    return redirect(url_for('players'))

@app.route('/players/delete/<int:pid>', methods=['POST'])
def delete_player(pid):
    conn = get_db()
    conn.execute("DELETE FROM Players WHERE player_id=?", (pid,))
    conn.commit(); conn.close()
    return redirect(url_for('players'))

# ─── GEAR ────────────────────────────────────────────────────────────────────
@app.route('/gear')
def gear():
    conn = get_db()
    rows = conn.execute("""
        SELECT g.*, p.ign, t.team_name FROM Gear g
        JOIN Players p ON g.player_id = p.player_id
        JOIN Teams t   ON p.team_id   = t.team_id
        ORDER BY p.ign
    """).fetchall()
    players_list = conn.execute("SELECT player_id, ign FROM Players ORDER BY ign").fetchall()
    conn.close()
    return render_template('gear.html', gear_list=rows, players=players_list)

@app.route('/gear/add', methods=['POST'])
def add_gear():
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO Gear (player_id,gear_type,brand,model,purchase_date) VALUES (?,?,?,?,?)",
                 (d['player_id'], d['gear_type'], d['brand'], d['model'], d['purchase_date']))
    conn.commit(); conn.close()
    return redirect(url_for('gear'))

@app.route('/gear/edit/<int:gid>', methods=['POST'])
def edit_gear(gid):
    d = request.form
    conn = get_db()
    conn.execute("UPDATE Gear SET player_id=?,gear_type=?,brand=?,model=?,purchase_date=? WHERE gear_id=?",
                 (d['player_id'], d['gear_type'], d['brand'], d['model'], d['purchase_date'], gid))
    conn.commit(); conn.close()
    return redirect(url_for('gear'))

@app.route('/gear/delete/<int:gid>', methods=['POST'])
def delete_gear(gid):
    conn = get_db()
    conn.execute("DELETE FROM Gear WHERE gear_id=?", (gid,))
    conn.commit(); conn.close()
    return redirect(url_for('gear'))

# ─── TOURNAMENTS ─────────────────────────────────────────────────────────────
@app.route('/tournaments')
def tournaments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM Tournaments ORDER BY start_date DESC").fetchall()
    conn.close()
    return render_template('tournaments.html', tournaments=rows)

@app.route('/tournaments/add', methods=['POST'])
def add_tournament():
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO Tournaments (name,game,start_date,end_date,prize_pool,location) VALUES (?,?,?,?,?,?)",
                 (d['name'], d['game'], d['start_date'], d['end_date'], d['prize_pool'], d['location']))
    conn.commit(); conn.close()
    return redirect(url_for('tournaments'))

@app.route('/tournaments/edit/<int:tid>', methods=['POST'])
def edit_tournament(tid):
    d = request.form
    conn = get_db()
    conn.execute("UPDATE Tournaments SET name=?,game=?,start_date=?,end_date=?,prize_pool=?,location=? WHERE tournament_id=?",
                 (d['name'], d['game'], d['start_date'], d['end_date'], d['prize_pool'], d['location'], tid))
    conn.commit(); conn.close()
    return redirect(url_for('tournaments'))

@app.route('/tournaments/delete/<int:tid>', methods=['POST'])
def delete_tournament(tid):
    conn = get_db()
    conn.execute("DELETE FROM Tournaments WHERE tournament_id=?", (tid,))
    conn.commit(); conn.close()
    return redirect(url_for('tournaments'))

# ─── MATCH RESULTS ───────────────────────────────────────────────────────────
@app.route('/results')
def results():
    conn = get_db()
    rows = conn.execute("""
        SELECT mr.*, t.team_name, tn.name AS tournament_name, tn.game
        FROM Match_Results mr
        JOIN Teams t        ON mr.team_id = t.team_id
        JOIN Tournaments tn ON mr.tournament_id = tn.tournament_id
        ORDER BY tn.name, mr.placement
    """).fetchall()
    teams = conn.execute("SELECT team_id, team_name FROM Teams ORDER BY team_name").fetchall()
    tournaments = conn.execute("SELECT tournament_id, name FROM Tournaments ORDER BY name").fetchall()
    conn.close()
    return render_template('results.html', results=rows, teams=teams, tournaments=tournaments)

@app.route('/results/add', methods=['POST'])
def add_result():
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO Match_Results (tournament_id,team_id,placement,points,prize_won) VALUES (?,?,?,?,?)",
                 (d['tournament_id'], d['team_id'], d['placement'], d['points'], d['prize_won']))
    conn.commit(); conn.close()
    return redirect(url_for('results'))

@app.route('/results/edit/<int:rid>', methods=['POST'])
def edit_result(rid):
    d = request.form
    conn = get_db()
    conn.execute("UPDATE Match_Results SET tournament_id=?,team_id=?,placement=?,points=?,prize_won=? WHERE result_id=?",
                 (d['tournament_id'], d['team_id'], d['placement'], d['points'], d['prize_won'], rid))
    conn.commit(); conn.close()
    return redirect(url_for('results'))

@app.route('/results/delete/<int:rid>', methods=['POST'])
def delete_result(rid):
    conn = get_db()
    conn.execute("DELETE FROM Match_Results WHERE result_id=?", (rid,))
    conn.commit(); conn.close()
    return redirect(url_for('results'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
