import unittest

from app import app, beautiful


class Tests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def testHomepageRoute(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testJsonHomeRoute(self):
        response = self.client.get('/json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testBadRoute(self):
        response = self.client.get('/nada', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def testJSONEndpoint(self):
        with app.app_context():
            response1 = self.client.get(
                '/json/take_home_pay?gross_pay=5000&employer_match=1000&taxes_and_fees=3000'
            )
            self.assertEqual(response1.get_json(), '3000')

            response2 = self.client.get(
                '/json/take_home_pay?gross_pay=5000&employer_match=600&taxes_and_fees=2000,500,400'
            )
            self.assertEqual(response2.get_json(), '2700')

    def testBeautifulHandlesIndentation(self):
        """Test beautiful() properly cleans indented docstrings to prevent code block formatting."""
        # Simulating a typical indented function docstring
        indented_docstring = """
        Calculate the future value of an investment.

        Args:
            rate: Interest rate per period
            nper: Number of periods

        Returns:
            Future value as a float
        """

        result = beautiful(indented_docstring)

        # The key test: indented text should NOT be interpreted as code blocks
        # Markdown treats 4+ spaces of indentation as code blocks
        self.assertNotIn("<code>", result)
        self.assertNotIn("<pre>", result)

    def testBeautifulEmptyInput(self):
        """Test beautiful() handles empty input correctly."""
        self.assertEqual(beautiful(None), "")
        self.assertEqual(beautiful(""), "")


if __name__ == '__main__':
    unittest.main()
