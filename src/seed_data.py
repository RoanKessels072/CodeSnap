from database.db import get_db_session
from models.user import User
from models.exercise import Exercise

def seed_exercises():
    db = get_db_session()
    
    try:
        existing = db.query(Exercise).first()
        if existing:
            print("Exercises already exist. Skipping...")
            return
        
        exercises = [
            Exercise(
                name="Hello World",
                description="Write a program that prints 'Hello, World!' to the console.",
                difficulty=1,
                starter_code="# Write your code here    ",
                language="python",
                test_cases=[
                    {
                        "input": "",
                        "expected_output": "Hello, World!",
                        "description": "Basic output test"
                    }
                ],
                reference_solution="print('Hello, World!')"
            ),
            
            Exercise(
                name="Sum Two Numbers",
                description="Write a function that takes two numbers and returns their sum.",
                difficulty=1,
                starter_code="def add(a, b):\n    # Write your code here\n    pass\n\nprint(add(5, 3))",
                language="python",
                test_cases=[
                    {"input": "5, 3", "expected_output": "8"},
                    {"input": "10, 20", "expected_output": "30"},
                    {"input": "0, 0", "expected_output": "0"}
                ],
                reference_solution="def add(a, b):\n    return a + b\n\nprint(add(5, 3))"
            ),
            
            Exercise(
                name="Reverse a String",
                description="Write a function that reverses a given string.",
                difficulty=2,
                starter_code="def reverse_string(s):\n    # Write your code here\n    pass\n\nprint(reverse_string('hello'))",
                language="python",
                test_cases=[
                    {"input": "hello", "expected_output": "olleh"},
                    {"input": "python", "expected_output": "nohtyp"},
                    {"input": "a", "expected_output": "a"}
                ],
                reference_solution="def reverse_string(s):\n    return s[::-1]\n\nprint(reverse_string('hello'))"
            ),
            
            Exercise(
                name="Find Maximum",
                description="Write a function that finds the maximum number in a list.",
                difficulty=2,
                starter_code="def find_max(numbers):\n    # Write your code here\n    pass\n\nprint(find_max([1, 5, 3, 9, 2]))",
                language="python",
                test_cases=[
                    {"input": "[1, 5, 3, 9, 2]", "expected_output": "9"},
                    {"input": "[10, 20, 5]", "expected_output": "20"},
                    {"input": "[-1, -5, -3]", "expected_output": "-1"}
                ],
                reference_solution="def find_max(numbers):\n    return max(numbers)\n\nprint(find_max([1, 5, 3, 9, 2]))"
            ),
            
            Exercise(
                name="FizzBuzz",
                description="Print numbers 1-15. For multiples of 3 print 'Fizz', multiples of 5 print 'Buzz', multiples of both print 'FizzBuzz'.",
                difficulty=3,
                starter_code="# Write your FizzBuzz code here\n",
                language="python",
                test_cases=[
                    {"input": "", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"}
                ],
                reference_solution="for i in range(1, 16):\n    if i % 15 == 0:\n        print('FizzBuzz')\n    elif i % 3 == 0:\n        print('Fizz')\n    elif i % 5 == 0:\n        print('Buzz')\n    else:\n        print(i)"
            ),
            
            Exercise(
                name="Palindrome Checker",
                description="Write a function that checks if a string is a palindrome (reads the same forwards and backwards).",
                difficulty=3,
                starter_code="def is_palindrome(s):\n    # Write your code here\n    pass\n\nprint(is_palindrome('racecar'))",
                language="python",
                test_cases=[
                    {"input": "racecar", "expected_output": "True"},
                    {"input": "hello", "expected_output": "False"},
                    {"input": "noon", "expected_output": "True"}
                ],
                reference_solution="def is_palindrome(s):\n    return s == s[::-1]\n\nprint(is_palindrome('racecar'))"
            ),
            
            Exercise(
                name="Count Vowels",
                description="Write a function that counts the number of vowels (a, e, i, o, u) in a string.",
                difficulty=2,
                starter_code="def count_vowels(s):\n    # Write your code here\n    pass\n\nprint(count_vowels('hello world'))",
                language="python",
                test_cases=[
                    {"input": "hello world", "expected_output": "3"},
                    {"input": "aeiou", "expected_output": "5"},
                    {"input": "xyz", "expected_output": "0"}
                ],
                reference_solution="def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')\n\nprint(count_vowels('hello world'))"
            ),
            
            Exercise(
                name="Factorial",
                description="Write a function that calculates the factorial of a number.",
                difficulty=3,
                starter_code="def factorial(n):\n    # Write your code here\n    pass\n\nprint(factorial(5))",
                language="python",
                test_cases=[
                    {"input": "5", "expected_output": "120"},
                    {"input": "3", "expected_output": "6"},
                    {"input": "0", "expected_output": "1"}
                ],
                reference_solution="def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n\nprint(factorial(5))"
            ),
            
            Exercise(
                name="Prime Number Checker",
                description="Write a function that checks if a number is prime.",
                difficulty=4,
                starter_code="def is_prime(n):\n    # Write your code here\n    pass\n\nprint(is_prime(17))",
                language="python",
                test_cases=[
                    {"input": "17", "expected_output": "True"},
                    {"input": "4", "expected_output": "False"},
                    {"input": "2", "expected_output": "True"}
                ],
                reference_solution="def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprint(is_prime(17))"
            ),
            
            Exercise(
                name="Fibonacci Sequence",
                description="Write a function that returns the nth Fibonacci number.",
                difficulty=4,
                starter_code="def fibonacci(n):\n    # Write your code here\n    pass\n\nprint(fibonacci(7))",
                language="python",
                test_cases=[
                    {"input": "7", "expected_output": "13"},
                    {"input": "1", "expected_output": "1"},
                    {"input": "10", "expected_output": "55"}
                ],
                reference_solution="def fibonacci(n):\n    if n <= 2:\n        return 1\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(7))"
            )
        ]
        
        for exercise in exercises:
            db.add(exercise)
        
        db.commit()
        print(f"Added {len(exercises)} exercises successfully!")
        
    except Exception as e:
        print(f"Error adding exercises: {e}")
        db.rollback()
    finally:
        db.close()

def seed_admin_user():
    db = get_db_session()
    
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists. Skipping...")
            return
        
        admin = User(
            keycloak_id="admin-default-id",
            email="admin@codesnap.com",
            username="admin"
        )
        
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def seed_all():
    print("Seeding database with initial data...")
    
    seed_admin_user()
    seed_exercises()
    
    print("Seeding complete!")

if __name__ == '__main__':
    seed_all()