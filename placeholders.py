from faker import Faker
from id_generator import incrementing_id, HealthPlan  # Import your custom incrementing_id function

# Set a seed at the class level if you need reproducibility
Faker.seed(0)

# Instantiate the Faker instance
fake = Faker()

# Dictionary to store both the method and an example value for each placeholder
fake_methods = {}

# Populate fake_methods_with_examples with all callable Faker methods and an example value
for provider in fake.providers:
    for attribute_name in dir(provider):
        if not attribute_name.startswith("_"):
            try:
                # Fetch the attribute and check if it's callable
                attr = getattr(fake, attribute_name)
                if callable(attr):
                    # Generate a sample value using the function
                    example_value = attr()
                    fake_methods[attribute_name] = {
                        "method": attr,
                        "example": example_value
                    }
            except (AttributeError, TypeError):
                continue

# Add the custom incrementing_id function with a sample value
fake_methods['incrementing_id'] = {
    "method": incrementing_id,
    "example": incrementing_id()
}

fake_methods['healthplan_city'] = {
    "method": "",
    "example": "city name"
}

fake_methods['healthplan_county'] = {
    "method": "",
    "example": "city name"
}

fake_methods['healthplan_zip'] = {
    "method": "",
    "example": "city name"
}

fake_methods['healthplan_state'] = {
    "method": "",
    "example": "city name"
}