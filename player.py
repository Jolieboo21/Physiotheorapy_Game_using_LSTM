import datetime

class PlayerData:
    def __init__(self, name, total_score, total_time=0, level="Level 1", play_date=None, exercise_names=None, exercise_scores=None, exercise_times=None):
        self.name = name
        self.total_score = total_score
        self.total_time = total_time
        self.level = level
        self.play_date = play_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.exercise_names = exercise_names or []  # Danh sách tên bài tập
        self.exercise_scores = exercise_scores or []  # Danh sách điểm từng bài tập
        self.exercise_times = exercise_times or []   # Danh sách thời gian từng bài tập

    def to_dict(self):
        return {
            "name": self.name,
            "total_score": self.total_score,
            "total_time": self.total_time,
            "level": self.level,
            "play_date": self.play_date,
            "exercise_names": self.exercise_names,
            "exercise_scores": self.exercise_scores,
            "exercise_times": self.exercise_times
        }