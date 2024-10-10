import unittest
from unittest.mock import MagicMock
from datetime import date

from guzi.models import User, Ecosystem, GuziCreator, DefaultEngagedStrategy

class TestUser(unittest.TestCase):

    def test_new_user(self):
        date_of_birth = date(2012, 3, 18)

        user = User(1234, date_of_birth)

        self.assertEqual(user.id, 1234)
        self.assertEqual(len(user.money_wallet), 0)
        self.assertEqual(len(user.invest_wallet), 0)
        self.assertEqual(len(user.economic_exp), 0)
        self.assertEqual(user.birthdate, date(2012, 3, 18))

    def test_age(self):
        date_of_birth = date(2012, 1, 2)

        user = User("id", date_of_birth)

        self.assertEqual(user.age(date(2016, 1, 1)), 3)
        self.assertEqual(user.age(date(2016, 1, 2)), 4)

    def test_age_stupid_raises_error(self):
        date_of_birth = date(2010, 1, 1)

        user = User("id", date_of_birth)

        with self.assertRaises(ValueError):
            user.age(date(2000, 1, 1))

    def test_outdate_raise_error_for_unexisting_money(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.outdate([1234, 4321])

    def test_outdate_valid_money(self):
        user = User("id", None)
        user.money_wallet.append("2000-01-01-id-money0000")
        user.money_wallet.append("2000-01-01-id-money0001")
        user.money_wallet.append("2000-01-01-id-money0002")

        user.outdate(["2000-01-01-id-money0000"])

        self.assertEqual(len(user.money_wallet), 2)
        self.assertEqual(len(user.economic_exp), 1)

    def test_pay(self):
        user = User("id", None)

        user.pay([1111, 2222, 3333])

        self.assertEqual(len(user.economic_exp), 3)

    def test_spend_to_should_raise_error_if_user_cannot_afford_it(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, 10)

    def test_spend_to_should_raise_error_if_amount_is_negative(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, -10)

    def test_spend_to_should_correctly_transfert_moneys(self):
        """
        If a user source spends money to an target one, source must lose his
        moneys from his money_wallet and target should have money_wallet unchanged
        while his economic_exp has increased of the amount
        """
        source = User("source", None)
        target = User("target", None)

        for i in range(10):
            source.create_daily_money_and_invest(date(2010, 1, i+1))

        self.assertEqual(len(source.money_wallet), 10)
        self.assertEqual(len(target.money_wallet), 0)
        self.assertEqual(len(target.economic_exp), 0)

        source.spend_to(target, 7)

        self.assertEqual(len(source.money_wallet), 3)
        self.assertEqual(len(target.money_wallet), 0)
        self.assertEqual(len(target.economic_exp), 7)

    def test_spend_to_takes_older_moneys_first(self):
        """
        When a user pays, his oldest Guzis should be spended first
        to avoid constant outdate
        """
        source = User("source", None)
        target = User("target", None)
        trashEcosystem = Ecosystem("trash", [target])

        for i in range(31):
            source.create_daily_money_and_invest(date(2010, 1, i+1))

        source.spend_to(target, 10)
        source.invest_in(trashEcosystem, 10)

        # After spending, user waits 9 days more (to be at 30)
        for i in range(10):
            source.create_daily_money_and_invest(date(2010, 2, i+1))
        # Then, of oldest have been taken, there should have no outdated
        # Money which passed to the economic_exp
        source.check_outdated_moneys(date(2010, 2, 9))
        self.assertEqual(len(source.economic_exp), 0)

    def test_spend_to_user_to_himself_should_go_to_economic_exp(self):
        """
        When a user spends his own Guzis to himself, before they become
        outdated, then they are added to economic_exp
        """
        user = User("", None)

        for i in range(10):
            user.create_daily_money_and_invest(date(2010, 2, i+1))

        user.spend_to(user, 10)

        self.assertEqual(len(user.money_wallet), 0)
        self.assertEqual(len(user.economic_exp), 10)

    def test_give_invests_to_should_raise_error_if_user_cannot_afford_it(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.invest_in(None, 10)

    def test_give_invests_to_should_raise_error_if_amount_is_negative(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.invest_in(None, -10)

    def test_give_invests_to_should_raise_error_if_target_is_not_an_ecosystem(self):
        user = User("id", None)
        target = User(None, None)

        with self.assertRaises(ValueError):
            user.invest_in(target, 0)

    def test_give_invests_to_should_correctly_transfert_invests(self):
        """
        If a user source gives invests to a target ecosystem, source must lose his
        invests from his invest_wallet and target should have invest_wallet increased
        of the amount
        """
        source = User("source", None)
        target = Ecosystem("target", [User(None, None)])

        for i in range(10):
            source.create_daily_money_and_invest(date(2010, 1, i+1))

        self.assertEqual(len(source.invest_wallet), 10)
        self.assertEqual(len(target.money_wallet), 0)

        source.invest_in(target, 7)

        self.assertEqual(len(source.invest_wallet), 3)
        self.assertEqual(len(target.money_wallet), 7)

    def test_give_invests_to_takes_older_invests_first(self):
        """
        When a user gives Guzas, his oldest Guzas should be spended first
        to avoid constant outdate
        """
        source = User("source", None)
        target = Ecosystem("target", [User(None, None)])

        for i in range(31):
            source.create_daily_money_and_invest(date(2010, 1, i+1))

        source.invest_in(target, 10)

        # After spending, user waits 10 days more (to be at 31)
        for i in range(10):
            source.create_daily_money_and_invest(date(2010, 2, i+1))
        # Then, of oldest have been taken, there should have no outdated
        # Guza which passed to the economic_exp
        source.check_outdated_moneys(date(2010, 2, 9))
        self.assertEqual(len(source.invest_trashbin), 0)

    def test_check_outdated_moneys_correctly_remove_outdated_moneys(self):
        user = User("id", None)
        user.create_daily_money_and_invest(date(2010, 1, 1))

        self.assertEqual(len(user.money_wallet), 1)
        self.assertEqual(len(user.economic_exp), 0)

        user.check_outdated_moneys(date(2010, 2, 1))

        self.assertEqual(len(user.money_wallet), 0)
        self.assertEqual(len(user.economic_exp), 2)

    def test_check_outdated_moneys_correctly_remove_outdated_invests(self):
        user = User("id", None)
        user.create_daily_money_and_invest(date(2010, 1, 1))

        self.assertEqual(len(user.invest_wallet), 1)
        self.assertEqual(len(user.economic_exp), 0)

        user.check_outdated_moneys(date(2010, 2, 1))

        self.assertEqual(len(user.invest_wallet), 0)
        self.assertEqual(len(user.economic_exp), 2)

    def test_create_daily_moneys_for_empty_total_accumulated(self):
        user = User("id", None)

        user.create_daily_money_and_invest(date(2000, 1, 1))

        self.assertEqual(len(user.money_wallet), 1)
        self.assertEqual(len(user.invest_wallet), 1)

    def test_create_daily_moneys_for_round_total_accumulated(self):
        user = User("id", None)
        # With 8 moneys in economic_exp, user should get 3 Guzis/day
        user.economic_exp += [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888]

        user.create_daily_money_and_invest(date(2000, 1, 1))

        self.assertEqual(len(user.money_wallet), 3)
        self.assertEqual(len(user.invest_wallet), 3)
        self.assertEqual(user.money_wallet[0], "2000-01-01-id-money0000")
        self.assertEqual(user.money_wallet[1], "2000-01-01-id-money0001")
        self.assertEqual(user.money_wallet[2], "2000-01-01-id-money0002")
        self.assertEqual(user.invest_wallet[0], "2000-01-01-id-invest0000")
        self.assertEqual(user.invest_wallet[1], "2000-01-01-id-invest0001")
        self.assertEqual(user.invest_wallet[2], "2000-01-01-id-invest0002")


class TestEcosystem(unittest.TestCase):

    def test_init_default_strategy_should_be_set(self):
        ecosystem = Ecosystem("id", [User(None, None)])

        self.assertIsInstance(ecosystem.engaged_strategy, DefaultEngagedStrategy)

    def test_add_invests_should_increase_money_wallet(self):
        ecosystem = Ecosystem("company_id", [User(None, None)])

        ecosystem.add_invests(["1", "2"])

        self.assertEqual(len(ecosystem.money_wallet), 2)

    def test_add_invests_should_raise_error_if_invest_already_added(self):
        ecosystem = Ecosystem("ecosystem_id", [User(None, None)])
        ecosystem.money_wallet = ["1"]

        with self.assertRaises(ValueError):
            ecosystem.add_invests(["1", "2"])

    def test_spend_to_should_raise_error_if_company_cannot_afford_it(self):
        ecosystem = Ecosystem("id", [User(None, None)])

        with self.assertRaises(ValueError):
            ecosystem.spend_to(None, 10)

    def test_spend_to_should_raise_error_if_amount_is_negative(self):
        ecosystem = Ecosystem("id", [User(None, None)])

        with self.assertRaises(ValueError):
            ecosystem.spend_to(None, -10)

    def test_spend_to_should_correctly_transfert_invests(self):
        """
        If a ecosystem source spends invest to an target user, source must lose his
        invests from his money_wallet and target should have invest_wallet unchanged
        """
        source = Ecosystem("source", [User(None, None)])
        source.money_wallet = ["{}".format(i) for i in range(10)]
        target = User("target", None)

        self.assertEqual(len(source.money_wallet), 10)
        self.assertEqual(len(target.invest_wallet), 0)

        source.spend_to(target, 7)

        self.assertEqual(len(source.money_wallet), 3)
        self.assertEqual(len(target.invest_wallet), 0)
        self.assertEqual(len(target.economic_exp), 7)

    def test_add_engaged_should_call_engaged_strategy(self):
        user = User(None, None)
        ecosystem = Ecosystem("id", [user])
        ecosystem.engaged_strategy.add_engaged = MagicMock()

        ecosystem.add_engaged(user, 1)

        ecosystem.engaged_strategy.add_engaged.assert_called_with(user, 1)

    def test_add_founder_should_call_engaged_strategy(self):
        user = User(None, None)
        ecosystem = Ecosystem("id", [user])
        ecosystem.engaged_strategy.add_founder = MagicMock()

        ecosystem.add_founder(user, 1)

        ecosystem.engaged_strategy.add_founder.assert_called_with(user, 1)

    def test_pay_should_call_engaged_strategy(self):
        user = User(None, None)
        ecosystem = Ecosystem("id", [user])
        ecosystem.engaged_strategy.pay = MagicMock()

        ecosystem.pay(["a", "b"])

        ecosystem.engaged_strategy.pay.assert_called_with(["a", "b"])


class TestDefaultEngagedStrategy(unittest.TestCase):

    def test_init_should_raise_error_if_no_founder_given(self):
        with self.assertRaises(ValueError):
            DefaultEngagedStrategy([])

    def test_add_engaged_should_add_user_in_the_list_n_times(self):
        strategy = DefaultEngagedStrategy([User(None, None)])
        user = User("id", None)

        strategy.add_engaged(user, 3)

        self.assertEqual(len(strategy.engaged_users), 3)

    def test_add_founder_should_add_user_in_the_list_n_times(self):
        user = User(None, None)
        strategy = DefaultEngagedStrategy([user])
        self.assertEqual(len(strategy.founders), 1)

        strategy.add_founder(user, 3)

        self.assertEqual(len(strategy.founders), 4)

    def test_pay_should_pay_in_arrival_and_times_order(self):
        """
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
        """
        strategy = DefaultEngagedStrategy([User(None, None)])
        user1 = User("id1", None)
        user2 = User("id2", None)
        user3 = User("id3", None)

        strategy.add_engaged(user1, 3)
        strategy.add_engaged(user2, 1)
        strategy.add_engaged(user3, 5)
        strategy.add_engaged(user1, 2)

        strategy.pay(["1", "2", "3", "4", "5"])
        self.assertEqual(len(user1.economic_exp), 3)
        self.assertEqual(len(user2.economic_exp), 1)
        self.assertEqual(len(user3.economic_exp), 1)

        strategy.pay(["1", "2", "3", "4", "5"])
        self.assertEqual(len(user1.economic_exp), 4)
        self.assertEqual(len(user2.economic_exp), 1)
        self.assertEqual(len(user3.economic_exp), 5)

    def test_pay_should_pay_founder_if_no_engaged(self):
        founder = User("founder", None)
        strategy = DefaultEngagedStrategy([founder])

        strategy.pay(["1", "2", "3", "4", "5"])
        self.assertEqual(len(founder.economic_exp), 5)

    def test_pay_should_pay_founderS_equaly_if_no_engaged(self):
        founder1 = User("founder1", None)
        founder2 = User("founder2", None)
        strategy = DefaultEngagedStrategy([founder1, founder2])

        strategy.pay(["1", "2", "3", "4"])
        self.assertEqual(len(founder1.economic_exp), 2)
        self.assertEqual(len(founder2.economic_exp), 2)
