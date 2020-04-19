import collections
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
        """
        Return User's age at given date
        """
        from dateutil.relativedelta import relativedelta

        years = relativedelta(date, self.birthdate).years

        if years < 0:
            raise ValueError("Date must be after user birth date {}".format(self.birthdate))

        return years

    def outdate(self, guzis):
        """
        Outdate the given Guzis
        If one or more given Guzis are not in any wallet, raise an error
        Add given Guzis to total_accumulated
        Add given Guzas to guza_trashbin
        """
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
        """
        Add given guzis to User balance income
        """
        for guzi in guzis:
            self.balance.income.append(guzi)

    def spend_to(self, target, amount):
        """
        Spend given amount of Guzis to given User target
        if amount is < 0 or too expansive, raise an error
        """
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
        """
        Check the balance state
        If the balance income is greater than outcome,
        add the bonus income to the total_accumulated
        """
        while len(self.balance.income) > len(self.balance.outcome):
            guzi = self.balance.income[-1]
            # Remove last element to add it to total_accumulated
            del self.balance.income[-1]
            self.total_accumulated.append(guzi)

    def check_outdated_guzis(self, date):
        """
        Pass through every User's Guzis and add outdated ones
        (>30 days old) to User's total_accumulated
        """
        guzis_to_outdate = []
        for guzi in self.guzi_wallet + self.guza_wallet:
            # extract the date from the first 10 characters (YYYY-MM-DD)
            creation_date = date.fromisoformat(guzi[:10])
            if date - creation_date >= timedelta(days=30):
                guzis_to_outdate.append(guzi)

        self.outdate(guzis_to_outdate)

    def create_daily_guzis(self, date):
        """
        Create daily Guzis for User.
        Daily_Guzis = (total_accumulated)^(1/3) + 1
        Each Guzi has a specific format :
        <date>-<owner_id>-guzi<guzi_index>"
            <date> : 2010-04-18
            <guzi_index> : 4 digits index ("0001", "0342")
        """
        number_of_guzis_to_add = int(len(self.total_accumulated) ** (1/3) + 1)
        for i in range(number_of_guzis_to_add):
            self.guzi_wallet.append(date.isoformat() + "-" + self.id + "-guzi{:04d}".format(i))
            self.guza_wallet.append(date.isoformat() + "-" + self.id + "-guza{:04d}".format(i))

    def _is_guzi(self, guzi):
        return guzi[-8:-4] == "guzi"

    def _is_guza(self, guzi):
        return guzi[-8:-4] == "guza"
