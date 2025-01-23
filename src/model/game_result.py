import src.debug as debug

class GameResult:
    def __init__(self):
        self.automa_score = 0
        self.automa_tiebreaker = 0
        self.human_cities = 0
        self.human_money = 0
        self.human_plants = []
        self.human_power_capacity = 0
        self.human_cities_built = 0
        self.human_score = 0
        self.human_win = False
        self.turns_taken = 0
        self.automa_city_win = False
        self.human_city_win = False
        self.automa_tiebreaker_win = False
        self.human_tiebreaker_win = False
        self.left_plants = []
        self.right_plants = []
        self.left_cities_built = 0
        self.right_cities_built = 0

    def calculate_winner(self):
        competing_automa = 'LeftAutoma' if self.left_cities_built >= self.right_cities_built else 'RightAutoma'
        competing_score = self.left_cities_built if self.left_cities_built >= self.right_cities_built else self.right_cities_built
        # TODO Actually calculate how many plants will fire, not just capacity
        if self.human_score > self.human_power_capacity:
            self.human_score = self.human_power_capacity
        else:
            self.human_score = self.human_cities_built
        if competing_score > self.human_score:
            debug.sim(f"{competing_automa} wins")
            self.automa_city_win = True
            return False
        if competing_score < self.human_score:
            debug.sim("Human wins")
            self.human_city_win = True
            return True
        if competing_score == self.human_score:
            if self.human_power_capacity < self.human_score:
                debug.sim(f"{competing_automa} wins")
                self.tiebreaker_automa_win = True
                return False
            else:
                if self.human_money <= self.automa_tiebreaker:
                    debug.sim(f"Automa wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker}")
                    self.tiebreaker_automa_win = True
                    return False
                else:
                    debug.sim(f"Human wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker}")
                    self.human_tiebreaker_win = True
                    return True