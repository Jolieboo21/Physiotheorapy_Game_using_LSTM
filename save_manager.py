import json
import os
from player import PlayerData

def save_score(player):
    file_path = "scores.json"
    scores = []
    print(f"DEBUG: Attempting to save score for {player.name} at {file_path}")

    # Đọc dữ liệu hiện tại nếu file tồn tại
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    scores = json.loads(content)
                    if not isinstance(scores, list):
                        scores = [scores]
                else:
                    scores = []
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON Decode Error - {str(e)}, initializing empty list")
            scores = []
        except UnicodeDecodeError as e:
            print(f"DEBUG: Unicode Decode Error - {str(e)}, initializing empty list")
            scores = []
    else:
        print(f"DEBUG: File {file_path} not found, creating new")

    # Cập nhật hoặc thêm bản ghi
    updated = False
    for entry in scores:
        if entry["name"] == player.name and entry["level"] == player.level:
            # Giữ điểm cao nhất và bản ghi mới nhất dựa trên play_date
            if entry["total_score"] < player.total_score or entry["play_date"] < player.play_date:
                entry.update(player.to_dict())
                updated = True
            break
    
    if not updated:
        scores.append(player.to_dict())

    # Kiểm tra và ghi file
    directory = os.path.dirname(file_path) or "."
    if not os.access(directory, os.W_OK):
        print(f"DEBUG: No write permission for directory {directory}")
    else:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=4, ensure_ascii=False)
                print(f"DEBUG: Successfully wrote to {file_path} - Scores: {scores}")
        except PermissionError as e:
            print(f"DEBUG: Permission Error writing to {file_path} - {str(e)}")
        except IOError as e:
            print(f"DEBUG: IO Error writing to {file_path} - {str(e)}")
        except Exception as e:
            print(f"DEBUG: Unexpected Error writing to {file_path} - {str(e)}")

def load_scores():
    file_path = "scores.json"
    scores = []
    print(f"DEBUG: Attempting to load scores from {file_path}")

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    data = json.loads(content)
                    if not isinstance(data, list):
                        data = [data]
                    scores = [PlayerData(**entry) for entry in data]
                else:
                    scores = []
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON Decode Error - {str(e)}, returning empty list")
            scores = []
        except UnicodeDecodeError as e:
            print(f"DEBUG: Unicode Decode Error - {str(e)}, returning empty list")
            scores = []
        except Exception as e:
            print(f"DEBUG: Unexpected Error loading {file_path} - {str(e)}")
            scores = []
    else:
        print(f"DEBUG: File {file_path} not found, returning empty list")

    return scores