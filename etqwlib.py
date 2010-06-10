import re
import socket
from struct import unpack

# States
WARMUP       = 1 << 0
IN_PROGRESS  = 1 << 1
REVIEWING    = 1 << 2
SECOND_ROUND = 1 << 3 # For stopwatch

def strip_colors(text):
    """Strips color codes from text."""
    return re.sub(r'\^.?', '', text)

def fetch_data(ip, port):
    """Sends status query to server and returns the data."""
    vars = {}
    players = {}
    info = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    try:
        sock.sendto('\xff\xffgetInfoEx\x00', (ip, int(port)))
        data = sock.recv(4096)[33:]
        sock.close()
    except:
        sock.close()
        return (vars, players, info)

    # Server variables
    items = data.split('\0')
    pairs = zip(items[::2], items[1::2])
    num_pairs = 0
    for num_pairs, (name, value) in enumerate(pairs):
        if name == value == '':
            break
        vars[name.lower()] = value
    data = '\0'.join(items[(num_pairs * 2) + 2:])

    # Players
    while data[0] != '\x20':
        id, ping, rate = unpack('3B', data[:3])
        nick = data[3:].split('\0', 1)[0]
        clantag_pos = unpack('B', data[4 + len(nick)])[0]
        clantag = data[5 + len(nick):].split('\0', 1)[0]
        is_bot = unpack('B', data[6 + len(nick) + len(clantag)])[0]
        name = nick + clantag if clantag_pos else clantag + nick
        data = data[7 + len(name):]

        player = {}
        player['ping'] = int(ping)
        player['rate'] = int(rate) # Not used as of version 1.4
        player['name'] = strip_colors(name)
        player['nick'] = strip_colors(nick)
        player['clantag_pos'] = int(clantag_pos)
        player['clantag'] = strip_colors(clantag)
        player['raw_name'] = str(name)
        player['raw_nick'] = str(nick)
        player['raw_clantag'] = str(clantag)
        player['is_bot'] = bool(is_bot)
        players[int(id)] = player
    data = data[1:]

    # Server info block
    info['os_mask'] = unpack('<i', data[:4])[0]
    info['is_ranked'] = bool(unpack('B', data[4])[0])
    info['time_left'] = unpack('<i', data[5:9])[0]
    info['game_state'] = unpack('B', data[9])[0]
    info['server_type'] = unpack('B', data[10])[0]
    info['interested_clients'] = unpack('B', data[11])[0]
    data = data[12:]

    # Extra data
    while data[0] != '\x20':
        id, xp = unpack('<Bf', data[0:5])
        team = data[5:].split('\0', 1)[0]
        kills, deaths = unpack('<2i', data[6 + len(team):14 + len(team)])
        data = data[14 + len(team):]

        # This should happen only if the server sent malformed data
        if int(id) not in players.keys():
            continue

        players[id]['xp'] = float(xp)
        players[id]['team'] = str(team)
        players[id]['kills'] = int(kills)
        players[id]['deaths'] = int(deaths)

    return (vars, players, info)
