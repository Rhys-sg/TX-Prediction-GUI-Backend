from database import Database 

# Initialize database
db = Database('database_test.db')
db.delete_database()
db = Database('database_test.db')

# Variables for schools
school1_name = 'school1'
school1_domain = 'school1.edu'
school2_name = 'school2'
school2_domain = 'school2.edu'
school_invalid_domain = 'school.edu'

# Inserting schools
assert db.insert_school(school1_name, school1_domain)
assert not db.insert_school(school1_name, school_invalid_domain)
assert db.insert_school(school2_name, school2_domain)
assert not db.insert_school('school', school2_domain)

# Querying schools and domains
assert db.query_schools_domains() == [(school1_name, school1_domain), (school2_name, school2_domain)]
assert db.query_schools() == [school1_name, school2_name]
assert db.query_domains() == [school1_domain, school2_domain]
assert db.query_school_by_domain('school1.edu') == school1_name

# Querying schools by domains
assert db.query_school_by_domain('school1.edu') == school1_name

# Variables for terms
term1_name = 'Spring 2024'
term2_name = 'Fall 2024'

# Inserting terms
assert db.insert_term(term1_name, school1_name)
assert not db.insert_term(term1_name, school1_name)
assert db.insert_term(term2_name, school1_name)
assert db.insert_term(term1_name, school2_name)
assert db.insert_term(term2_name, school2_name)

# Querying terms by school
expected_terms_school1 = [term1_name, term2_name]
expected_terms_school2 = [term1_name, term2_name]
assert db.query_terms_by_school(school1_name) == expected_terms_school1
assert db.query_terms_by_school(school2_name) == expected_terms_school2

# Variables for ligation orders
ligation_order1 = ('Order 1', 'Sequence A', '2024-07-11', 'John, Jane')
ligation_order2 = ('Order 2', 'Sequence B', '2024-07-12', 'Alice, Bob')

# Inserting ligation orders using school and term names
assert db.insert_ligation_order(school1_name, term1_name, *ligation_order1)
assert db.insert_ligation_order(school2_name, term2_name, *ligation_order2)

# Querying ligation orders by school and term
expected_ligation_orders_school1_term1 = [ligation_order1]
expected_ligation_orders_school2_term2 = [ligation_order2]
assert db.query_ligation_orders_by_school_and_term(school1_name, term1_name) == expected_ligation_orders_school1_term1
assert db.query_ligation_orders_by_school_and_term(school2_name, term2_name) == expected_ligation_orders_school2_term2

# Variables for accounts
user_email = 'user@example.com'
user_first_name = 'John'
user_last_name = 'Doe'
user_password = 'password123'

# Inserting an account
assert db.insert_account(user_email, school1_name, user_first_name, user_last_name, user_password)
assert not db.insert_account(user_email, school1_name, user_first_name, user_last_name, user_password)

# Logging in a user
assert db.login_account(user_email, user_password)
assert not db.login_account('', user_password)
assert db.query_first_name_by_email(user_email) == user_first_name
assert db.query_last_name_by_email(user_email) == user_last_name

# Variables for observations
sequence = 'ATCG'
observation_email = 'example@email.com'
value1 = -1
value2 = -5
students = 'John Doe, Jane Smith'
notes = 'Example notes'
date = '2024-07-11'

# Insert observations
assert db.insert_observation(sequence, observation_email, value1, students, notes, date)
assert db.insert_observation(sequence, observation_email, value2, students, notes, date)

# Query observations by sequence
assert db.query_observations_by_sequence(sequence) == [(observation_email, value1, students, notes, date),
                                                       (observation_email, value2, students, notes, date)]

assert db.query_average_observed_TX_by_sequence(sequence) == (value1 + value2) / 2

# Closing the database connection
db.close()

# Deleting the database file
assert db.delete_database()
