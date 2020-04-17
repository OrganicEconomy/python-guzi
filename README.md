# python-guzi
A library to use Guzi in Python applications

## Run tests

```python
python -m unittest
```

## Usage

Create a simulator to generate users and make them live with their Guzis and Guzas.

Example of use :
```python
# Create a simulator with starting date on january the 3rd of 2010
simulator = Simulator(date(2010, 1, 3))

# Add users to the simulator
user1 = simulator.generate_user()
# A user born in the 80s
user_born_in_the_80 = simulator.generate_user(min_birth=date(1980, 1, 1), max_birth=date(1989, 12, 31))
# An adult user
major_user = simulator.generate_adult_user()

# Simulate the days passing
simulator.new_day()
simulator.new_day()
simulator.new_day()

# Or, to pass a week, a month, a year
simulator.new_days(7)
simulator.new_days(30)
simulator.new_days(365)

# Then make them spend between each other
user1.spend_to(major_user, 30)
user1.spend_to(user_born_in_the_80, 20)
```
