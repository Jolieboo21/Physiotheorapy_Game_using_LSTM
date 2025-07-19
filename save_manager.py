import json
from player import PlayerData

def save_score(player: PlayerData, filepath='scores.json'):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(player.to_dict())
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_scores(filepath='scores.json'):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return sorted(data, key=lambda x: x['score'], reverse=True)
    except:
        return []