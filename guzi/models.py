import collections
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class GuziCreator:
    def create_money(user, date, index):
        return date.isoformat() + "-" + user.id + "-money{:04d}".format(index)

    def create_invest(user, date, index):
        return date.isoformat() + "-" + user.id + "-invest{:04d}".format(index)


class SpendableEntity:
    def pay(self, moneys):
        raise NotImplementedError
        
    def spend_to(self, target, amount):
        raise NotImplementedError


class User(SpendableEntity):

    def __init__(self, id, birthdate):
        self.id = id
        self.birthdate = birthdate
        self.money_wallet = []
        self.invest_wallet = []
        self.economic_exp = []
        self.invest_trashbin = []

    def daily_moneys(self):
        """
        Return the number of Guzis (and Invests) the user should earn each day
        """
        return int(len(self.economic_exp) ** (1/3) + 1)

    def age(self, date=date.today()):
        """
        Return User's age at given date
        """
        years = relativedelta(date, self.birthdate).years

        if years < 0:
            raise ValueError("Date must be after user birth date {}".format(self.birthdate))

        return years

    def outdate(self, moneys):
        """
        Outdate the given Money
        If one or more given Money are not in any wallet, raise an error
        Add given Money to economic_exp
        Also add given Invest to economic_exp
        """
        invalid_moneys = [g for g in moneys
                if g not in self.money_wallet + self.invest_wallet]
        if len(invalid_moneys) > 0:
            raise ValueError("Money(s) {} is/are invalid".format(invalid_moneys))
        
        for m in moneys:
            if self._is_money(m):
                self.economic_exp.append(m)
                del self.money_wallet[self.money_wallet.index(m)]
            if self._is_invest(m):
                self.economic_exp.append(m)
                del self.invest_wallet[self.invest_wallet.index(m)]

    def pay(self, moneys):
        """
        Add given moneys to User economic_exp
        """
        for m in moneys:
            self.economic_exp.append(m)

    def spend_to(self, target, amount):
        """
        Spend given amount of Guzis to given User target
        if amount is < 0 or too expansive, raise an error
        """
        if amount < 0:
            raise ValueError("Cannot spend negative amount")
        if amount > len(self.money_wallet):
            raise ValueError("User cannot pay this amount")
        if target is self:
            self.economic_exp += self.money_wallet[:amount]
        else:
            target.pay(self.money_wallet[:amount])
        del self.money_wallet[:amount]

    def invest_in(self, target, amount):
        """
        give amount of Invests to given Ecosystem target
        if amount is < 0 or too expansive, raise an error
        """
        if amount < 0:
            raise ValueError("Cannot give negative amount")
        if amount > len(self.invest_wallet):
            raise ValueError("User cannot give this much")
        if not isinstance(target, Ecosystem):
            raise ValueError("Can only give Invests to Ecosystem, not {}".format(type(target)))
        target.add_invests(self.invest_wallet[:amount])
        del self.invest_wallet[:amount]

    def check_outdated_moneys(self, date):
        """
        Pass through every User's Guzis and add outdated ones
        (>30 days old) to User's economic_exp
        """
        moneys_to_outdate = []
        for money in self.money_wallet + self.invest_wallet:
            # extract the date from the first 10 characters (YYYY-MM-DD)
            creation_date = date.fromisoformat(money[:10])
            if date - creation_date >= timedelta(days=30):
                moneys_to_outdate.append(money)

        self.outdate(moneys_to_outdate)

    def create_daily_money_and_invest(self, date):
        """
        Create daily Guzis for User.
        Daily_Guzis = (economic_exp)^(1/3) + 1
        Each Guzi has a specific format :
        <date>-<owner_id>-money<money_index>"
            <date> : 2010-04-18
            <money_index> : 4 digits index ("0001", "0342")
        """
        number_of_moneys_to_add = self.daily_moneys()
        for i in range(number_of_moneys_to_add):
            self.money_wallet.append(GuziCreator.create_money(self, date, i))
            self.invest_wallet.append(GuziCreator.create_invest(self, date, i))

    def _is_money(self, money):
        return money[-9:-4] == "money"

    def _is_invest(self, money):
        return money[-10:-4] == "invest"


class Ecosystem(SpendableEntity):

    def __init__(self, id, founders):
        self.id = id
        self.money_wallet = []
        self.engaged_strategy = DefaultEngagedStrategy(founders)

    def add_invests(self, invests):
        """
        add_invests is called from User to give the Ecosystem Invests it will then
        be able to spend.
        """
        for invest in invests:
            if invest in self.money_wallet:
                raise ValueError("invest {} already given".format(invest)) 
        self.money_wallet += invests

    def spend_to(self, target, amount):
        """
        Spend given amount of Invests to given User target
        if amount is < 0 or too expansive, raise an error
        """
        if amount < 0:
            raise ValueError("Cannot spend negative amount")
        if amount > len(self.money_wallet):
            raise ValueError("User cannot pay this amount")
        if target is self:
            self.economic_exp += self.money_wallet[:amount]
        else:
            target.pay(self.money_wallet[:amount])
        del self.money_wallet[:amount]

    def add_engaged(self, user, times):
        self.engaged_strategy.add_engaged(user, times)

    def add_founder(self, user, times):
        self.engaged_strategy.add_founder(user, times)

    def pay(self, moneys):
        """
        When a User or an Ecosystem pays an Ecosystem, the paied Invests don't stay in
        any Ecosystem wallet, it goes directly to Ecosystem's engaged users economic_exp.
        """
        self.engaged_strategy.pay(moneys)


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
      If a Ecosystem want a user to get daily engaged, it must add him daily
    """
    def __init__(self, founders):
        """
        At least one founder is necessary, instead where would the profit paied
        Guzis go ? Ecosystem CAN NOT KEEP ANY PAID GUZI, so it needs to send them
        to any user : the founder(s)
        """
        if len(founders) == 0:
            raise ValueError("At least one founder is necessary to a ecosystem")
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

    def pay(self, moneys):
        for g in moneys:
            self._pay_money(g)

    def _pay_money(self, money):
        if len(self.engaged_users) == 0:
            self.users[self.founders[self.founders_index]].pay([money])
            self.founders_index += 1
            self.founders_index %= len(self.founders)
        else:
            self.users[self.engaged_users[0]].pay(money)
            del self.engaged_users[0]
