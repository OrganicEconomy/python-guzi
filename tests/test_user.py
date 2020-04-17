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
        self.assertEqual(user.birth_date, date(2012, 3, 18))

    def test_age(self):
        date_of_birth = date(2012, 1, 2)

        user = User("id-", date_of_birth)

        self.assertEqual(user.age(date(2016, 1, 1)), 3)
        self.assertEqual(user.age(date(2016, 1, 2)), 4)

    def test_age_stupid_raises_error(self):
        date_of_birth = date(2010, 1, 1)

        user = User("id-", date_of_birth)

        with self.assertRaises(ValueError):
            user.age(date(2000, 1, 1))

    def test_outdate_raise_error_for_unexisting_guzi(self):
        user = User("id-", None)

        with self.assertRaises(ValueError):
            user.outdate([1234, 4321])

    def test_outdate_valid_guzi(self):
        user = User("id-", None)
        user.guzi_wallet.append(1111)
        user.guzi_wallet.append(2222)
        user.guzi_wallet.append(3333)

        user.outdate([1111])

        self.assertEqual(len(user.guzi_wallet), 2)
        self.assertEqual(len(user.total_accumulated), 1)

    def test_pay(self):
        user = User("id-", None)

        user.pay([1111, 2222, 3333])

        self.assertEqual(len(user.balance.income), 3)

    def test_check_balance_with_negative_balance(self):
        user = User("id-", None)
        user.balance.outcome.append(1111)

        user.check_balance()

        self.assertEqual(len(user.balance.outcome), 1)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.total_accumulated), 0)

    def test_check_balance_with_positive_balance(self):
        user = User("id-", None)
        user.balance.income.append(1111)

        self.assertEqual(len(user.balance.outcome), 0)
        self.assertEqual(len(user.balance.income), 1)
        self.assertEqual(len(user.total_accumulated), 0)

        user.check_balance()

        self.assertEqual(len(user.balance.outcome), 0)
        self.assertEqual(len(user.balance.income), 0)
        self.assertEqual(len(user.total_accumulated), 1)

    def test_create_daily_guzis_for_empty_total_accumulated(self):
        user = User("id-", None)

        user.create_daily_guzis(date(2000, 1, 1))

        self.assertEqual(len(user.guzi_wallet), 1)
        self.assertEqual(len(user.guza_wallet), 1)

    def test_create_daily_guzis_for_round_total_accumulated(self):
        user = User("id-", None)
        # With 8 guzis in total_accumulated, user should get 3 Guzis/day
        user.total_accumulated += [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888]

        user.create_daily_guzis(date(2000, 1, 1))

        self.assertEqual(len(user.guzi_wallet), 3)
        self.assertEqual(len(user.guza_wallet), 3)
        self.assertEqual(user.guzi_wallet[0], "id-2000-01-01-n0000")
        self.assertEqual(user.guzi_wallet[1], "id-2000-01-01-n0001")
        self.assertEqual(user.guzi_wallet[2], "id-2000-01-01-n0002")
        self.assertEqual(user.guza_wallet[0], "id-2000-01-01-n0000")
        self.assertEqual(user.guza_wallet[1], "id-2000-01-01-n0001")
        self.assertEqual(user.guza_wallet[2], "id-2000-01-01-n0002")
