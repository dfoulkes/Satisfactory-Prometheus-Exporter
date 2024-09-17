import unittest
from app.satisfactory_api import get_api_token, get_server_stats

class TestSatisfactoryAPI(unittest.TestCase):
    def test_get_api_token(self):
        # Add your test cases here
        token = get_api_token()  # Call the function to test
        print(token)
        pass

    def test_get_server_status(self):
        # Add your test cases here
        token = get_api_token()  # Call the function to test
        stats = get_server_stats(token)  # Call the function to test
        print(stats)
        pass


if __name__ == '__main__':
    unittest.main()