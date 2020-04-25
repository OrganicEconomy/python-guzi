# python-guzi
A library to use Guzi in Python applications

## Run tests

```python
python -m unittest
```

## Usage

Class User contains every Guzi relative information a user would need :
    - guzi wallet
    - guza waller
    - total accumulated
    - balance

For now, a Guzi (and a Guza) is just a string, an identifier defining what it is. So it has no dedicated class. Maybe it will, but for now, nope.

Example of use :
```python
from datetime import date
from guzi.models import User

# Create users
user1 = User("unique_id1", birthdate=date(1989, 11, 28))
user2 = User("unique_id2", birthdate=date(1998, 9, 5))

# create their Guzis (it's like having a new day)
for i in range(1, 10):
    user1.create_daily_guzis(date(2020, 4, i))

# Then make them spend between each other
user1.spend_to(user2, 3)
user1.spend_to(user2, 2)
```

Class Company contains every Guzi relative information a company would need :
    - guza_wallet

A Company has also an engaged strategy. An engaged User can be a paid employee or some kind of shareholder. When a User is engaged to a Company for a number of times (for example User1 engaged 4 times), it means that 4 of the Guzis the Company will get paid with will go to this User.

An engaged User is different of a founder User : founder User only get paid when all engaged Users have been fully paid. Founder only get the profit.

For example, an employee in the company would be engaged and would get his or her salary every month. He or she could aslo be part of the founders and then, if the company earns more than necessary to pay salaries, the bonus (the profit) would go to this salaried too.

Usage:
```python
from datetime import date
from guzi.models import User, Company, DefaultEngagedStrategy

# Create users
user1 = User("unique_id1", birthdate=date(1989, 11, 28))
user2 = User("unique_id2", birthdate=date(1998, 9, 5))

# Create company
founders = [user1, user2]
company = Company("unique_id", founders)

# Create users Guzas
for i in range(1, 10):
    user1.create_daily_guzis(date(2020, 4, i))
    user2.create_daily_guzis(date(2020, 4, i))

# Users can give Guzas to the company
user1.give_guzas_to(company, 3)
user2.give_guzas_to(company, 9)

# Then company can spend those Guzas, for example to buy something to user1
# who could sell something usefull for the company
company.spend_to(user1, 6)
user1.check_balance()
assert(len(user1.total_accumulated) == 6-3)
```
