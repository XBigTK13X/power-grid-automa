import src.debug as debug


class ResourceRow:
    def __init__(self, kind, bins, per_bin, first_fill_amount, refill_amounts):
        self.costs = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16]
        self.first_fill_amount = first_fill_amount
        self.refill_amounts = refill_amounts
        self.refill_rates = [
            self.refill_amounts[0],
            self.refill_amounts[1],
            self.refill_amounts[2],
        ]
        self.kind = kind
        self.bin_count = bins
        self.bin_size = per_bin
        self.quantity_max = 12 if kind == "nuke" else 24
        self.bins = [0 for _ in range(self.bin_count)]
        self.quantity = 0

        for idx in range(self.bin_count):
            if self.costs[idx] >= self.first_fill_amount:
                fill_qty = 1 if kind == "nuke" else self.bin_size
                self.bins[idx] = fill_qty
                self.quantity += fill_qty

    def take_one(self, money):
        for idx in range(self.bin_count):
            if self.bins[idx] > 0:
                cost = self.costs[idx]
                if money >= cost:
                    self.bins[idx] -= 1
                    self.quantity -= 1
                    return True, money - cost
                return False, money
        return False, money

    def put_one(self):
        if self.quantity >= self.quantity_max:
            return False
        for idx in range(self.bin_count - 1, -1, -1):
            if self.bins[idx] < self.bin_size:
                self.bins[idx] += 1
                self.quantity += 1
                return True
        return False

    def refill_phase(self, step_index):
        refill_rate = self.refill_rates[step_index]
        added = 0
        for _ in range(refill_rate):
            if self.put_one():
                added += 1
            else:
                break
        return added

    def current_cost(self):
        for idx in range(self.bin_count):
            if self.bins[idx] > 0:
                return self.costs[idx]
        return float("inf")

    def debug(self):
        debug.game(f"{self.bins}<-{self.kind} ({self.quantity})")


class ResourceMarket:
    def __init__(self, start_amounts, refill_rates):
        self.kinds = {"coal": 0, "oil": 1, "trash": 2, "nuke": 3}
        self.start_amounts = start_amounts
        self.refill_rates = refill_rates
        self.rows = [
            ResourceRow(
                "coal",
                8,
                3,
                self.start_amounts[0],
                [
                    self.refill_rates[0][0],
                    self.refill_rates[1][0],
                    self.refill_rates[2][0],
                ],
            ),
            ResourceRow(
                "oil",
                8,
                3,
                self.start_amounts[1],
                [
                    self.refill_rates[0][1],
                    self.refill_rates[1][1],
                    self.refill_rates[2][1],
                ],
            ),
            ResourceRow(
                "trash",
                8,
                3,
                self.start_amounts[2],
                [
                    self.refill_rates[0][2],
                    self.refill_rates[1][2],
                    self.refill_rates[2][2],
                ],
            ),
            ResourceRow(
                "nuke",
                12,
                1,
                self.start_amounts[3],
                [
                    self.refill_rates[0][3],
                    self.refill_rates[1][3],
                    self.refill_rates[2][3],
                ],
            ),
        ]

    def purchase(self, kind, amount, money):
        if kind == "wind":
            return True, money, 0
        purchased = True
        taken = 0
        while purchased and taken < amount:
            if kind == "oil/coal":
                resource_row = (
                    self.rows[0]
                    if self.rows[0].current_cost() <= self.rows[1].current_cost()
                    else self.rows[1]
                )
            else:
                resource_row = self.rows[self.kinds[kind]]
            purchased, money = resource_row.take_one(money)
            if purchased:
                taken += 1
        return purchased, money, taken

    def refill_phase(self, step):
        amounts = {}
        step_idx = min(max(step - 1, 0), 2)
        for row in self.rows:
            amounts[row.kind] = row.refill_phase(step_idx)
        return amounts

    def cost_to_buy(self, kind, amount):
        row = self.rows[self.kinds[kind]]
        accumulated_cost = 0
        needed = amount
        for idx in range(row.bin_count):
            available = row.bins[idx]
            take_count = min(needed, available)
            accumulated_cost += take_count * row.costs[idx]
            needed -= take_count
            if needed == 0:
                break
        return accumulated_cost, amount - needed

    def amounts(self):
        return [
            self.rows[0].quantity,
            self.rows[1].quantity,
            self.rows[2].quantity,
            self.rows[3].quantity,
        ]

    def debug(self):
        for row in self.rows:
            row.debug()
