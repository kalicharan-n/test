# placeholders.py

from faker import Faker
from id_generator import incrementing_id  # Import incrementing_id from id_generator

fake = Faker()

# Placeholder mappings
fake_methods = {
    'street_address': fake.street_address,
    'first_name': fake.first_name,
    'incrementing_id': incrementing_id
}
