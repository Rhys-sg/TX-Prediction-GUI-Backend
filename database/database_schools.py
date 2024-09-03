import bcrypt
from database import Database 

# Initialize database
db = Database('database.db')

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

# Querying schools
expected_schools = [(school1_name, school1_domain), (school2_name, school2_domain)]
assert db.query_schools() == expected_schools

assert db.query_school_by_domain('school1.edu') == school1_name

# Variables for terms
term1_name = 'Spring 2024'
term2_name = 'Fall 2024'

# Inserting terms
assert db.insert_term(term1_name, school1_name)
assert db.insert_term(term2_name, school1_name)
assert db.insert_term(term1_name, school2_name)
assert db.insert_term(term2_name, school2_name)

# Querying terms by school
expected_terms_school1 = [term1_name, term2_name]
expected_terms_school2 = [term1_name, term2_name]
assert db.query_terms_by_school(school1_name) == expected_terms_school1
assert db.query_terms_by_school(school2_name) == expected_terms_school2

# Variables for ligation orders
ligation_order1 = ('Group A', 'Order 1', 'Sequence A', '2024-07-11', 'John, Jane')
ligation_order2 = ('Group B', 'Order 2', 'Sequence B', '2024-07-12', 'Alice, Bob')

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
hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Inserting an account with hashed password
assert db.insert_account(user_email, school1_name, user_first_name, user_last_name, hashed_password)
assert not db.insert_account(user_email, school1_name, user_first_name, user_last_name, hashed_password)

# Variables for observations
sequence = 'ATCG'
observation_email = 'example@email.com'
value = -1
students = 'John Doe, Jane Smith'
notes = 'Example notes'
date = '2024-07-11'

# Insert observations
assert db.insert_observation(sequence, observation_email, value, students, notes, date)
assert db.insert_observation(sequence, observation_email, value, students, notes, date)

# Query observations by sequence
assert db.query_observations_by_sequence(sequence)

# Closing the database connection
db.close()

# Deleting the database file
assert db.delete_database()
