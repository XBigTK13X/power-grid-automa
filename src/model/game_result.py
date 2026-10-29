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
        competing_automa = (
            "LeftAutoma"
            if self.left_cities_built >= self.right_cities_built
            else "RightAutoma"
        )
        competing_score = max(self.left_cities_built, self.right_cities_built)
        competing_tiebreaker = (
            self.left_plants[0][0]
            if self.left_cities_built >= self.right_cities_built
            and self.left_plants
            and self.left_plants[0]
            else (
                self.right_plants[0][0]
                if self.right_plants and self.right_plants[0]
                else 0
            )
        )
        self.human_score = min(self.human_cities_built, self.human_power_capacity)

        if competing_score > self.human_score:
            debug.sim(f"{competing_automa} wins")
            self.automa_city_win = True
            return False
        if competing_score < self.human_score:
            debug.sim("Human wins")
            self.human_city_win = True
            return True

        if self.human_money > competing_tiebreaker:
            debug.sim(
                f"Human wins with tiebreaker. Human money ${self.human_money} to {competing_tiebreaker}"
            )
            self.human_tiebreaker_win = True
            return True
        else:
            debug.sim(
                f"Automa wins with tiebreaker. Human money ${self.human_money} to {competing_tiebreaker}"
            )
            self.automa_tiebreaker_win = True
            return False
