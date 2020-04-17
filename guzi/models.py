import collections
from datetime import date, timedelta

# This shortcut create a class named "Balance" with 2 attributes :
# "income" & "outcome"
Balance = collections.namedtuple('Balance', 'income outcome')

class User:

    def __init__(self, id, birth_date):
        self.id = id
        self.birth_date = birth_date
        self.guzi_wallet = []
        self.guza_wallet = []
        self.total_accumulated = []
        self.balance = Balance([], [])

    def age(self, date=date.today()):
        from dateutil.relativedelta import relativedelta

        years = relativedelta(date, self.birth_date).years

        if years < 0:
            raise ValueError("Date must be after user birth date {}".format(self.birth_date))

        return years

    def outdate(self, guzis):
        invalid_guzis = [g for g in guzis if g not in self.guzi_wallet]
        if len(invalid_guzis) > 0:
            raise ValueError("guzi(s) {} is/are invalid".format(invalid_guzis))
        
        for guzi in guzis:
            del self.guzi_wallet[self.guzi_wallet.index(guzi)]
            self.total_accumulated.append(guzi)

    def pay(self, guzis):
        for guzi in guzis:
            self.balance.income.append(guzi)

    def check_balance(self):
        while len(self.balance.income) > len(self.balance.outcome):
            guzi = self.balance.income[-1]
            # Remove last element to add it to total_accumulated
            del self.balance.income[-1]
            self.total_accumulated.append(guzi)

    def create_daily_guzis(self, date):
        number_of_guzis_to_add = int(len(self.total_accumulated) ** (1/3) + 1)
        for i in range(number_of_guzis_to_add):
            self.guzi_wallet.append(self.id + date.isoformat() + "-n{:04d}".format(i))
            self.guza_wallet.append(self.id + date.isoformat() + "-n{:04d}".format(i))
