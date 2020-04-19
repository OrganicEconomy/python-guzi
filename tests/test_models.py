import unittest
from datetime import date

from guzi.models import User

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

        source.spend_to(target, 10)

        self.assertEqual(len(source.guzi_wallet), 0)
        self.assertEqual(len(target.guzi_wallet), 0)
        self.assertEqual(len(target.balance.income), 10)

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
