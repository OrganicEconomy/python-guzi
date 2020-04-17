import unittest
from datetime import date

from guzi.models import User, Simulator

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


class TestSimulator(unittest.TestCase):

    def test_generate_user(self):
        simulator = Simulator()
        
        simulator.generate_user()

        self.assertEqual(len(simulator.user_pool), 1)

    def test_generate_user_called_multiple_times(self):
        simulator = Simulator()
        
        simulator.generate_user()
        simulator.generate_user()

        self.assertEqual(len(simulator.user_pool), 2)
        self.assertNotEqual(simulator.user_pool[0].id, simulator.user_pool[1].id)

    def test_generate_adult_user(self):
        simulator = Simulator()
        
        for i in range(10):
            simulator.generate_adult_user()

        self.assertEqual(len(simulator.user_pool), 10)

        for i in range(10):
            user = simulator.user_pool[i]
            self.assertTrue(simulator.user_pool[i].age() >= 18, "User {} (born {}) is only {} years old".format(user.id, user.birthdate, user.age()))

    def test_new_day_must_create_daily_guzis_in_users_wallets(self):
        """
        new_day should add the daily Guzis of all users. Here 1 each as the
        total_accumulated is always 0.
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.generate_adult_user()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 1)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)

    def test_new_day_must_check_balance_of_all_users(self):
        """
        a new_day should set the balance of each user back to 0 and add the
        bonuses to the users total_accumulated (which goes from 0 to 1)
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            user = simulator.generate_adult_user()
            user.balance.income.append("1234")

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 1)

    def test_new_day_must_check_outdated_guzis_of_all_users(self):
        """
        new_day should move Guzis in guzi_wallet older than 30 days to the
        total_accumulated of it's owner
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            user = simulator.generate_adult_user()
            user.create_daily_guzis(date(2000, 1, 1))

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 0)

        simulator.new_days(30)

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 1)

    def test_new_day_must_create_daily_guzas_in_users_wallets(self):
        """
        new_day should add the daily Guzas of all users. Here 1 each as the
        total_accumulated is always 0.
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.generate_adult_user()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)

    def test_new_day_must_check_outdated_guzas_of_all_users(self):
        """
        new_day should move Guzas in guza_wallet older than 30 days to the
        guza_trashbin of it's owner
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(1):
            user = simulator.generate_adult_user()

        for i in range(1):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_trashbin), 0)

        simulator.new_days(31)

        for i in range(1):
            # 31 because at 30, a Guzi was outdated and increased the daily earn
            # to 2/day
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 31)
            self.assertEqual(len(simulator.user_pool[i].guza_trashbin), 1)

    def test_new_day_multiple_times(self):
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.generate_adult_user()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()
        simulator.new_day()
        simulator.new_day()

        self.assertEqual(simulator.current_date, date(2000, 1, 4))
        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 3)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 3)

    def test_new_days(self):
        """
        Running new_days(15) should increase guzi_wallet & guza_wallet of 
        15*1 (as total_accumulated = 0) = 15
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.generate_adult_user()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_days(15)

        self.assertEqual(simulator.current_date, date(2000, 1, 16))
        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 15)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 15)
