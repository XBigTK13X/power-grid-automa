from copy import deepcopy

import src.debug as debug

class ResourceRow:
    def __init__(self,kind,bins,per_bin,first_fill_amount,refill_amounts):
        self.costs = [1,2,3,4,5,6,7,8,10,12,14,16]
        self.first_fill_amount = first_fill_amount
        self.refill_amounts = refill_amounts
        self.refill_rates = [self.refill_amounts[0],self.refill_amounts[1],self.refill_amounts[2]]
        self.kind = kind
        self.bins = []
        for ii in range(0,bins):
            self.bins.append(0)
        self.index = bins-1
        self.bin_size = per_bin
        self.quantity = 0
        self.quantity_max = 12 if kind == 'nuke' else 24
        self.bin_count = bins
        filling = True
        while self.costs[self.index] >= self.first_fill_amount and filling:
            self.bins[self.index] = self.bin_size
            self.quantity += 1 if kind == 'nuke' else 3
            if not self.next_cheaper_bin_index():
                filling = False

    def next_cheaper_bin_index(self):
        if self.index > 0:
            self.index -= 1
            return True
        if self.index <= 0:
            self.index = 0
            return False

    def next_expensive_bin_index(self):
        if self.index < len(self.bins) - 1:
            self.index += 1
            return True
        if self.index >= len(self.bins):
            self.index = len(self.bins) - 1
            return False

    def take_one(self,money):
        if self.bins[self.index] == 0:
            if self.next_expensive_bin_index():
                if money >= self.costs[self.index]:
                    self.bins[self.index] -= 1
                    money -= self.costs[self.index]
                    self.quantity -= 1
                    return True,money
                else:
                    return False,money
            else:
                return False,money
        else:
            if money >= self.costs[self.index]:
                self.bins[self.index] -= 1
                money -= self.costs[self.index]
                self.quantity -= 1
                return True,money
            else:
                return False,money

    def put_one(self):
        if self.bins[self.index] >= self.bin_size:
            self.bins[self.index] = self.bin_size
            if self.next_cheaper_bin_index():
                self.bins[self.index] += 1
                self.quantity += 1
                return True
            else:
                return False
        else:
            self.bins[self.index] += 1
            self.quantity += 1
            return True


    def refill_phase(self,step_index):
        refill_rate = self.refill_rates[step_index]
        if refill_rate <= 0:
            return 0
        amount = 0
        for ii in range(0,refill_rate):
            if self.quantity < self.quantity_max:
                amount += 1
                self.put_one()
        return amount

    def current_cost(self):
        return self.costs[self.index]

    def debug(self):
        debug.game(f'{self.bins}<-{self.kind} ({self.quantity})')

class ResourceMarket:
    def __init__(self,start_amounts,refill_rates):
        self.kinds = {
            'coal': 0,
            'oil': 1,
            'trash': 2,
            'nuke': 3
        }
        self.start_amounts = start_amounts
        self.refill_rates = refill_rates
        self.rows = [
            ResourceRow('coal',8,3,self.start_amounts[0],[self.refill_rates[0][0],self.refill_rates[1][0],self.refill_rates[2][0]]),
            ResourceRow('oil',8,3,self.start_amounts[1],[self.refill_rates[0][1],self.refill_rates[1][1],self.refill_rates[2][1]]),
            ResourceRow('trash',8,3,self.start_amounts[2],[self.refill_rates[0][2],self.refill_rates[1][2],self.refill_rates[2][2]]),
            ResourceRow('nuke',12,1,self.start_amounts[3],[self.refill_rates[0][3],self.refill_rates[1][3],self.refill_rates[2][3]])
        ]

    def purchase(self,kind,amount,money):
        resource_row = None
        if kind == 'wind':
            return True,money
        purchased = True
        taken = 0
        while purchased and taken < amount:
            if kind == 'oil/coal':
                resource_row = self.rows[0] if self.rows[0].current_cost() < self.rows[1].current_cost() else self.rows[1]
            else:
                resource_row = self.rows[self.kinds[kind]]
            purchased,money = resource_row.take_one(money)
            if purchased:
                taken += 1
        return purchased,money,taken

    def refill_phase(self,step):
        amounts = {}
        for row in self.rows:
            amounts[row.kind] = row.refill_phase(step - 1)
        return amounts

    def cost_to_buy(self,kind,amount):
        row_backup = deepcopy(self.rows[self.kinds[kind]])
        purchased,money,taken = self.purchase(kind,amount,10000)
        self.rows[self.kinds[kind]] = row_backup
        return 10000-money,taken

    def amounts(self):
        return [
            self.rows[0].quantity,
            self.rows[1].quantity,
            self.rows[2].quantity,
            self.rows[3].quantity
        ]

    def debug(self):
        for row in self.rows:
            row.debug()