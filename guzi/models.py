import collections, string, random
from datetime import date, timedelta


# This shortcut create a class named "Balance" with 2 attributes :
# "income" & "outcome"
Balance = collections.namedtuple('Balance', 'income outcome')

class User:

    def __init__(self, id, birthdate):
        self.id = id
        self.birthdate = birthdate
        self.guzi_wallet = []
        self.guza_wallet = []
        self.total_accumulated = []
        self.guza_trashbin = []
        self.balance = Balance([], [])

    def age(self, date=date.today()):
        from dateutil.relativedelta import relativedelta

        years = relativedelta(date, self.birthdate).years

        if years < 0:
            raise ValueError("Date must be after user birth date {}".format(self.birthdate))

        return years

    def outdate(self, guzis):
        invalid_guzis = [g for g in guzis
                if g not in self.guzi_wallet + self.guza_wallet]
        if len(invalid_guzis) > 0:
            raise ValueError("guzi(s) {} is/are invalid".format(invalid_guzis))
        
        for guzi in guzis:
            if self._is_guzi(guzi):
                del self.guzi_wallet[self.guzi_wallet.index(guzi)]
                self.total_accumulated.append(guzi)
            if self._is_guza(guzi):
                del self.guza_wallet[self.guza_wallet.index(guzi)]
                self.guza_trashbin.append(guzi)

    def pay(self, guzis):
        for guzi in guzis:
            self.balance.income.append(guzi)

    def spend_to(self, amount, target):
        if amount < 0:
            raise ValueError("Cannot spend negative amount")
        if amount > len(self.guzi_wallet):
            raise ValueError("User cannot pay this amount")
        if target is self:
            self.total_accumulated += self.guzi_wallet[:10]
        else:
            target.pay(self.guzi_wallet[:10])
        del self.guzi_wallet[:10]

    def check_balance(self):
        while len(self.balance.income) > len(self.balance.outcome):
            guzi = self.balance.income[-1]
            # Remove last element to add it to total_accumulated
            del self.balance.income[-1]
            self.total_accumulated.append(guzi)

    def check_outdated_guzis(self, date):
        guzis_to_outdate = []
        for guzi in self.guzi_wallet + self.guza_wallet:
            # extract the date from the first 10 characters (YYYY-MM-DD)
            creation_date = date.fromisoformat(guzi[:10])
            if date - creation_date >= timedelta(days=30):
                guzis_to_outdate.append(guzi)

        self.outdate(guzis_to_outdate)

    def create_daily_guzis(self, date):
        number_of_guzis_to_add = int(len(self.total_accumulated) ** (1/3) + 1)
        for i in range(number_of_guzis_to_add):
            self.guzi_wallet.append(date.isoformat() + "-" + self.id + "-guzi{:04d}".format(i))
            self.guza_wallet.append(date.isoformat() + "-" + self.id + "-guza{:04d}".format(i))

    def _is_guzi(self, guzi):
        return guzi[-8:-4] == "guzi"

    def _is_guza(self, guzi):
        return guzi[-8:-4] == "guza"


class Simulator:

    def __init__(self, start_date=date.today()):
        self.start_date = start_date
        self.current_date = start_date
        self.user_pool = []

    def generate_user(self, min_birth=date(1940, 1, 1), max_birth=date.today()):
        """
        Create a User instance with random birthdate and unique id
        and add it to the simulator user_pool.
        This is simply a shortcut
        """
        randId = self._randomword(20)
        randBirthdate = self._random_date(min_birth, max_birth)
        new_user = User(randId, randBirthdate)
        self.user_pool.append(new_user)
        return new_user

    def generate_adult_user(self):
        return self.generate_user(date(1940, 1, 1), date.today()-18*timedelta(days=365, hours=6))

    def new_day(self):
        self.current_date += timedelta(days=1)
        for user in self.user_pool:
            user.check_balance()
            user.check_outdated_guzis(self.current_date)
            user.create_daily_guzis(self.current_date)

    def new_days(self, days):
        for i in range(days):
            self.new_day()

    def _random_date(self, start, end):
        """
        This function will return a random datetime between two datetime objects.
        """
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        return start + timedelta(seconds=random_second)

    def _randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
