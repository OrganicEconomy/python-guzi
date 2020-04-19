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
from guzi.models import User

# Create users
user1 = User("unique_id1", birthdate=date(1989, 11, 28))
user2 = User("unique_id2", birthdate=date(1998, 9, 5))

# create their Guzis (it's like having a new day)
for i in range(10):
    user1.create_daily_guzis(date(2020, 4, i))

# Then make them spend between each other
user1.spend_to(user2, 3)
user1.spend_to(user2, 2)
```
