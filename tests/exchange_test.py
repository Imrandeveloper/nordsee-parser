import json
import os
import sys
import pathlib
import unittest

sys.path.append('..')

from exchanger import Exchanger

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PAGES_DIR_NAME = 'pages'
PAGES_DIR = os.path.join(CURRENT_DIR, PAGES_DIR_NAME)

APPLY_PAGE_FILENAME = 'apply_job.html'
APPLY_PAGE_FILEPATH = os.path.join(PAGES_DIR, APPLY_PAGE_FILENAME)

TEST_URL = 'https://karriere.nordsee.com/de/Verkaeufer-Mitarbeiter-Restaurant-mw-in-Berlin-de-j2496.html'
TEST_DATA_FILENAME = 'nordsee_test.json'


def save_page_content(html=None):
    """
    Save page content to use in tests
    :param html: html code to save
    :return: file path 
    """
    # create directory to save downloaded pages if it does not exists
    if not os.path.exists(PAGES_DIR):
        os.makedirs(PAGES_DIR)

    try:
        open(APPLY_PAGE_FILEPATH, 'w').write(html)
    except Exception as e:
        print('Can not download page: {}'.format(str(e)))
    return APPLY_PAGE_FILEPATH


class ExchangeTestCase(unittest.TestCase):
    """
    Exchage tests
    """
    def setUp(self):
        test_data = json.load(open(TEST_DATA_FILENAME))
        self.exchanger = Exchanger(user_data=test_data, vacancy_url=TEST_URL)
        self._get_apply_page_content()
        self._visit_test_page()

    def _get_apply_page_content(self):
        """
        Get and save content of the test page if it does not exists
        """
        if not os.path.exists(APPLY_PAGE_FILEPATH):
            html = self.exchanger._open_page()
            save_page_content(html)

    def _visit_test_page(self):
        """
        Visit test page via webdriver 
        """
        file_url = pathlib.Path(APPLY_PAGE_FILEPATH).as_uri()
        self.exchanger.browser.visit(file_url)

    def test_download_file(self):
        """
        Test download_file method 
        """
        file_path = self.exchanger._download_file()
        self.assertTrue(os.path.isfile(file_path))
        # remove test file
        try:
            os.remove(file_path)
        except OSError:
            pass

    def test_fill_inputs(self):
        """
        Test fill_inputs method 
        """
        result = self.exchanger._fill_inputs()
        self.assertTrue(result)

    def test_click_agree(self):
        """
        Test click_agree method
        :return: 
        """
        agree_clicked = self.exchanger._click_agree()
        self.assertTrue(agree_clicked)

if __name__ == '__main__':
    unittest.main()
