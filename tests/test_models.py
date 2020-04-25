import unittest
from datetime import date

from guzi.models import User, Company, GuziCreator, DefaultEngagedStrategy

class TestUser(unittest.TestCase):

    def test_new_user(self):
        date_of_birth = date(2012, 3, 18)

        user = User(1234, date_of_birth)

        self.assertEqual(user.id, 1234)
        self.assertEqual(len(user.guzi_wallet), 0)
        self.assertEqual(len(user.guza_wallet), 0)
        self.assertEqual(len(user.total_accumulated), 0)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.balance.outcome), 0)
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

    def test_outdate_raise_error_for_unexisting_guzi(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.outdate([1234, 4321])

    def test_outdate_valid_guzi(self):
        user = User("id", None)
        user.guzi_wallet.append("2000-01-01-id-guzi0000")
        user.guzi_wallet.append("2000-01-01-id-guzi0001")
        user.guzi_wallet.append("2000-01-01-id-guzi0002")

        user.outdate(["2000-01-01-id-guzi0000"])

        self.assertEqual(len(user.guzi_wallet), 2)
        self.assertEqual(len(user.total_accumulated), 1)

    def test_pay(self):
        user = User("id", None)

        user.pay([1111, 2222, 3333])

        self.assertEqual(len(user.balance.income), 3)

    def test_spend_to_should_raise_error_if_user_cannot_afford_it(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, 10)

    def test_spend_to_should_raise_error_if_amount_is_negative(self):
        user = User("id", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, -10)

    def test_spend_to_should_correctly_transfert_guzis(self):
        """
        If a user source spends guzi to an target one, source must lose his
        guzis from his guzi_wallet and target should have guzi_wallet unchanged
        while his balance_income has increased of the amount
        """
        source = User("source", None)
        target = User("target", None)

        for i in range(10):
            source.create_daily_guzis(date(2010, 1, i+1))

        self.assertEqual(len(source.guzi_wallet), 10)
        self.assertEqual(len(target.guzi_wallet), 0)
        self.assertEqual(len(target.balance.income), 0)

        source.spend_to(target, 7)

        self.assertEqual(len(source.guzi_wallet), 3)
        self.assertEqual(len(target.guzi_wallet), 0)
        self.assertEqual(len(target.balance.income), 7)

    def test_spend_to_takes_older_guzis_first(self):
        """
        When a user pays, his oldest Guzis should be spended first
        to avoid constant outdate
        """
        source = User("source", None)
        target = User("target", None)

        for i in range(31):
            source.create_daily_guzis(date(2010, 1, i+1))

        source.spend_to(target, 10)

        # After spending, user waits 9 days more (to be at 30)
        for i in range(10):
            source.create_daily_guzis(date(2010, 2, i+1))
        # Then, of oldest have been taken, there should have no outdated
        # Guzi which passed to the total_accumulated
        source.check_outdated_guzis(date(2010, 2, 9))
        self.assertEqual(len(source.total_accumulated), 0)

    def test_spend_to_user_to_himself_should_go_to_total_accumulated(self):
        """
        When a user spends his own Guzis to himself, before they become
        outdated, then they are added to total_accumulated
        """
        user = User("", None)

        for i in range(10):
            user.create_daily_guzis(date(2010, 2, i+1))

        user.spend_to(user, 10)

        self.assertEqual(len(user.guzi_wallet), 0)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.balance.outcome), 0)
        self.assertEqual(len(user.total_accumulated), 10)

    def test_check_balance_with_negative_balance(self):
        user = User("id", None)
        user.balance.outcome.append(1111)

        user.check_balance()

        self.assertEqual(len(user.balance.outcome), 1)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.total_accumulated), 0)

    def test_check_balance_with_positive_balance(self):
        user = User("id", None)
        user.balance.income.append(1111)

        self.assertEqual(len(user.balance.outcome), 0)
        self.assertEqual(len(user.balance.income), 1)
        self.assertEqual(len(user.total_accumulated), 0)

        user.check_balance()

        self.assertEqual(len(user.balance.outcome), 0)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.total_accumulated), 1)

    def test_check_outdated_guzis_correctly_remove_outdated_guzis(self):
        user = User("id", None)
        user.create_daily_guzis(date(2010, 1, 1))

        self.assertEqual(len(user.guzi_wallet), 1)
        self.assertEqual(len(user.total_accumulated), 0)

        user.check_outdated_guzis(date(2010, 2, 1))

        self.assertEqual(len(user.guzi_wallet), 0)
        self.assertEqual(len(user.total_accumulated), 1)

    def test_create_daily_guzis_for_empty_total_accumulated(self):
        user = User("id", None)

        user.create_daily_guzis(date(2000, 1, 1))

        self.assertEqual(len(user.guzi_wallet), 1)
        self.assertEqual(len(user.guza_wallet), 1)

    def test_create_daily_guzis_for_round_total_accumulated(self):
        user = User("id", None)
        # With 8 guzis in total_accumulated, user should get 3 Guzis/day
        user.total_accumulated += [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888]

        user.create_daily_guzis(date(2000, 1, 1))

        self.assertEqual(len(user.guzi_wallet), 3)
        self.assertEqual(len(user.guza_wallet), 3)
        self.assertEqual(user.guzi_wallet[0], "2000-01-01-id-guzi0000")
        self.assertEqual(user.guzi_wallet[1], "2000-01-01-id-guzi0001")
        self.assertEqual(user.guzi_wallet[2], "2000-01-01-id-guzi0002")
        self.assertEqual(user.guza_wallet[0], "2000-01-01-id-guza0000")
        self.assertEqual(user.guza_wallet[1], "2000-01-01-id-guza0001")
        self.assertEqual(user.guza_wallet[2], "2000-01-01-id-guza0002")


class TestCompany(unittest.TestCase):

    def test_init_default_strategy_should_be_set(self):
        company = Company("id")

        self.assertIsInstance(company.engaged_strategy, DefaultEngagedStrategy)

    def test_add_guzas_should_increase_guza_wallet(self):
        company = Company("company_id")

        company.add_guzas(["1", "2"])

        self.assertEqual(len(company.guza_wallet), 2)

    def test_add_guzas_should_raise_error_if_guza_already_addn(self):
        company = Company("company_id")
        company.guza_wallet = ["1"]

        with self.assertRaises(ValueError):
            company.add_guzas(["1", "2"])

    def test_spend_to_should_raise_error_if_company_cannot_afford_it(self):
        company = Company("id")

        with self.assertRaises(ValueError):
            company.spend_to(None, 10)

    def test_spend_to_should_raise_error_if_amount_is_negative(self):
        company = Company("id")

        with self.assertRaises(ValueError):
            company.spend_to(None, -10)

    def test_spend_to_should_correctly_transfert_guzas(self):
        """
        If a company source spends guza to an target one, source must lose his
        guzas from his guza_wallet and target should have guza_wallet unchanged
        while his balance_income has increased of the amount
        """
        source = Company("source")
        source.guza_wallet = ["{}".format(i) for i in range(10)]
        target = User("target", None)

        self.assertEqual(len(source.guza_wallet), 10)
        self.assertEqual(len(target.guza_wallet), 0)
        self.assertEqual(len(target.balance.income), 0)

        source.spend_to(target, 7)

        self.assertEqual(len(source.guza_wallet), 3)
        self.assertEqual(len(target.guza_wallet), 0)
        self.assertEqual(len(target.balance.income), 7)


class TestDefaultEngagedStrategy(unittest.TestCase):

    def test_add_engaged_should_add_user_in_the_list_n_times(self):
        strategy = DefaultEngagedStrategy()
        user = User("id", None)

        strategy.add_engaged(user, 3)

        self.assertEqual(len(strategy.engaged_users), 3)

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
        strategy = DefaultEngagedStrategy()
        user1 = User("id1", None)
        user2 = User("id2", None)
        user3 = User("id3", None)

        strategy.add_engaged(user1, 3)
        strategy.add_engaged(user2, 1)
        strategy.add_engaged(user3, 5)
        strategy.add_engaged(user1, 2)

        strategy.pay(["1", "2", "3", "4", "5"])
        self.assertEqual(len(user1.balance.income), 3)
        self.assertEqual(len(user2.balance.income), 1)
        self.assertEqual(len(user3.balance.income), 1)

        strategy.pay(["1", "2", "3", "4", "5"])
        self.assertEqual(len(user1.balance.income), 4)
        self.assertEqual(len(user2.balance.income), 1)
        self.assertEqual(len(user3.balance.income), 5)
