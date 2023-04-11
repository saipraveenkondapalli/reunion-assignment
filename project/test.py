from project.models import User

# 5 dummy users with name email and passwords
User(name="john", email="john@example.com", password ="password123").save()
# michael, david, mark, paul
User(name="michael", email="michael@example.com", password ="password123").save()
User(name="david", email="david@example.com", password = "password123").save()
User(name="mark", email="mark@example.com", password="password123").save()
User(name="paul", email="paul@example.com", password="password123").save()
