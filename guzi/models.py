import collections
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


# This shortcut create a class named "Balance" with 2 attributes :
# "income" & "outcome"
Balance = collections.namedtuple('Balance', 'income outcome')

class GuziCreator:
    def create_guzi(user, date, index):
        return date.isoformat() + "-" + user.id + "-guzi{:04d}".format(index)

    def create_guza(user, date, index):
        return date.isoformat() + "-" + user.id + "-guza{:04d}".format(index)


class SpendableEntity:
    def pay(self, guzis):
        raise NotImplementedError
        
    def spend_to(self, target, amount):
        raise NotImplementedError


class User(SpendableEntity):

    def __init__(self, id, birthdate):
        self.id = id
        self.birthdate = birthdate
        self.guzi_wallet = []
        self.guza_wallet = []
        self.total_accumulated = []
        self.guza_trashbin = []
        self.balance = Balance([], [])

    def daily_guzis(self):
        """
        Return the number of Guzis (and Guzas) the user should earn each day
        """
        return int(len(self.total_accumulated) ** (1/3) + 1)

    def age(self, date=date.today()):
        """
        Return User's age at given date
        """
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
            self.total_accumulated += self.guzi_wallet[:amount]
        else:
            target.pay(self.guzi_wallet[:amount])
        del self.guzi_wallet[:amount]

    def give_guzas_to(self, target, amount):
        """
        give amount of Guzas to given Company target
        if amount is < 0 or too expansive, raise an error
        """
        if amount < 0:
            raise ValueError("Cannot give negative amount")
        if amount > len(self.guza_wallet):
            raise ValueError("User cannot give this amount")
        if not isinstance(target, Company):
            raise ValueError("Can only give Guzas to Company, not {}".format(type(target)))
        target.add_guzas(self.guza_wallet[:amount])
        for g in self.guza_wallet[:amount]:
            self.balance.outcome.append(g)
        del self.guza_wallet[:amount]

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
        number_of_guzis_to_add = self.daily_guzis()
        for i in range(number_of_guzis_to_add):
            self.guzi_wallet.append(GuziCreator.create_guzi(self, date, i))
            self.guza_wallet.append(GuziCreator.create_guza(self, date, i))

    def _is_guzi(self, guzi):
        return guzi[-8:-4] == "guzi"

    def _is_guza(self, guzi):
        return guzi[-8:-4] == "guza"


class Company(SpendableEntity):

    def __init__(self, id, founders):
        self.id = id
        self.guzi_wallet = []
        self.engaged_strategy = DefaultEngagedStrategy(founders)

    def add_guzas(self, guzas):
        """
        add_guzas is called from User to give the Company Guzas it will then
        be able to spend.
        """
        for guza in guzas:
            if guza in self.guzi_wallet:
                raise ValueError("guza {} already given".format(guza)) 
        self.guzi_wallet += guzas

    def spend_to(self, target, amount):
        """
        Spend given amount of Guzas to given User target
        if amount is < 0 or too expansive, raise an error
        """
        if amount < 0:
            raise ValueError("Cannot spend negative amount")
        if amount > len(self.guzi_wallet):
            raise ValueError("User cannot pay this amount")
        if target is self:
            self.total_accumulated += self.guzi_wallet[:amount]
        else:
            target.pay(self.guzi_wallet[:amount])
        del self.guzi_wallet[:amount]

    def add_engaged(self, user, times):
        self.engaged_strategy.add_engaged(user, times)

    def add_founder(self, user, times):
        self.engaged_strategy.add_founder(user, times)

    def pay(self, guzis):
        """
        When a User or a Company pays a Company, the paied Guzis don't stay in
        any Company wallet, it goes directly to Company's engaged users balance.
        """
        self.engaged_strategy.pay(guzis)


class DefaultEngagedStrategy:
    """
    DefaultEngagedStrategy gives Guzis to users fully in arrived order
    Example :
      - Add User1 3 times
      - Add User2 1 time
      - Add User3 5 times
      - Add User1 2 times (yes, User1 again)
      Then, when pay is called for 5 Guzis :
      - Firstly, User1 gets 3 Guzis
      - Secondly, User2 gets 1 Guzi
      - Finaly, User3 gets 1 Gusi
      Then, when pay is called again for 5 Guzis
      - User3 gets 4 Guzis
      - User 1 gets 1 Guzi
      (See test test_pay_should_pay_in_arrival_and_times_order for details)
      If a Company want a user to get daily engaged, it must add him daily
    """
    def __init__(self, founders):
        """
        At least one founder is necessary, instead where would the profit paied
        Guzis go ? Company CAN NOT KEEP ANY PAID GUZI, so it needs to send them
        to any user : the founder(s)
        """
        if len(founders) == 0:
            raise ValueError("At least one founder is necessary to a company")
        self.users = {}
        self.engaged_users = []
        self.founders = []
        for f in founders:
            self.add_founder(f, 1)
        self.founders_index = 0

    def add_engaged(self, user, times):
        """
        Here we store users once in users dict
        and only store ids in engaged_users, to avoid big memory use
        """
        self.users[user.id] = user
        for t in range(times):
            self.engaged_users.append(user.id)

    def add_founder(self, user, times):
        """
        founders only get profit. If engaged keep arriving, they always firstly
        get paid. If only every engaged has got his engagement filled, then the
        founders get the profit.
        The difference here is that they never leave. While there is profit,
        they keep earning with a loop).
        """
        self.users[user.id] = user
        for t in range(times):
            self.founders.append(user.id)

    def pay(self, guzis):
        for g in guzis:
            self._pay_guzi(g)

    def _pay_guzi(self, guzi):
        if len(self.engaged_users) == 0:
            self.users[self.founders[self.founders_index]].pay([guzi])
            self.founders_index += 1
            self.founders_index %= len(self.founders)
        else:
            self.users[self.engaged_users[0]].pay(guzi)
            del self.engaged_users[0]
