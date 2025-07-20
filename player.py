class PlayerData:
    def __init__(self, name, score, total_time=0, level="Level 1"):
        self.name = name
        self.score = score
        self.total_time = total_time  # Tổng thời gian (giây)
        self.level = level  # Mức độ (ví dụ: "Level 1")