class PlayerData:
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

    def to_dict(self):
        return {"name": self.name, "score": self.score}