import src.debug as debug

class GameResult:
    def __init__(self):
        self.automa_score = 0
        self.automa_tiebreaker = 0
        self.human_cities = 0
        self.human_money = 0
        self.human_plants = []
        self.human_power_capacity = 0
        self.human_score = 0
        self.human_win = False
        self.turns_taken = 0
        self.automa_city_win = False
        self.human_city_win = False
        self.automa_tiebreaker_win = False
        self.human_tiebreaker_win = False

    def calculate_winner(self):
        # TODO Actually calculate how many plants will fire, not just capacity
        if self.human_score > self.human_power_capacity:
            self.human_score = self.human_power_capacity
        if self.automa_score > self.human_score:
            debug.sim("Automa wins")
            self.automa_city_win = True
            return False
        if self.automa_score < self.human_score:
            debug.sim("Human wins")
            self.human_city_win = True
            return True
        if self.automa_score == self.human_score:
            if self.human_power_capacity < self.human_score:
                debug.sim("Automa wins")
                self.tiebreaker_automa_win = True
                return False
            else:
                if self.human_money <= self.automa_tiebreaker:
                    debug.sim(f"Automa wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker()}")
                    self.tiebreaker_automa_win = True
                    return False
                else:
                    debug.sim(f"Human wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker}")
                    self.human_tiebreaker_win = True
                    return True