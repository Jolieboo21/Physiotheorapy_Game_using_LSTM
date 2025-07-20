import json
import os

def save_score(player):
    file_path = "scores.json"
    scores = []
    print(f"DEBUG: Attempting to save score for {player.name} at {file_path}")  # Debug trước khi đọc
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                content = f.read()
                if content.strip():  # Kiểm tra xem file có dữ liệu không
                    scores = json.loads(content)
                    if not isinstance(scores, list):  # Nếu không phải list, chuyển thành list
                        scores = [scores]
                else:
                    scores = []
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON Decode Error - {str(e)}, initializing empty list")
                scores = []
    else:
        print(f"DEBUG: File {file_path} not found, creating new")

    # Tìm người chơi có cùng tên và level để cập nhật
    updated = False
    for entry in scores:
        if entry["name"] == player.name and entry["level"] == player.level:
            entry["score"] = max(entry["score"], player.score)
            entry["total_time"] = player.total_time
            updated = True
            break
    
    # Nếu không tìm thấy bản ghi trùng cả name và level, thêm mới
    if not updated:
        scores.append({
            "name": player.name,
            "score": player.score,
            "total_time": player.total_time,
            "level": player.level
        })
    
    # Kiểm tra quyền ghi trước khi ghi
    if not os.access(os.path.dirname(file_path) or ".", os.W_OK):
        print(f"DEBUG: No write permission for {file_path}")
    else:
        try:
            with open(file_path, "w") as f:
                json.dump(scores, f, indent=4)
                print(f"DEBUG: Successfully wrote to {file_path} - Scores: {scores}")
        except PermissionError as e:
            print(f"DEBUG: Permission Error writing to {file_path} - {str(e)}")
        except IOError as e:
            print(f"DEBUG: IO Error writing to {file_path} - {str(e)}")
        except Exception as e:
            print(f"DEBUG: Unexpected Error writing to {file_path} - {str(e)}")