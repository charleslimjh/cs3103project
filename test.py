import unittest
import coordination_test_app
import random

class CoordinationTest(unittest.TestCase):
    # Test coordinated access to the DB by different processes
    def test_db_coordination(self):
        num_links = random.randint(1, 250) * 10
        result = coordination_test_app.run(num_links)
        self.assertEqual(result, num_links, f"Coordination access test failed | Expected: {num_links} Actual: {result}")  # Assert that the total number of URLs accessed by different processes is equal to 100

if __name__ == '__main__':
    unittest.main()
