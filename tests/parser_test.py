import os
import sys
import requests as rq
import unittest

from pyquery import PyQuery as pq
from unittest.mock import patch

sys.path.append('..')

from vacancy_parser import NordseeParser


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PAGES_DIR_NAME = 'pages'
PAGES_DIR = os.path.join(CURRENT_DIR, PAGES_DIR_NAME)

LIST_PAGE_URL = 'https://karriere.nordsee.com/de/stellenangebote.html'
LIST_PAGE_FILENAME = 'vacancy_list.html'
VACANCY_PAGE_FILENAME = 'vacancy_info.html'

LIST_PAGE_FILEPATH = os.path.join(PAGES_DIR, LIST_PAGE_FILENAME)
VACANCY_PAGE_FILEPATH = os.path.join(PAGES_DIR, VACANCY_PAGE_FILENAME)


def get_test_page(page_type=None, url=None):
    """
    Get page to use in tests
    :param page_type: page wth vacancies list or page with vacancy details 
    :param url: page url 
    :return: file path 
    """
    r = rq.get(url)
    # create directory to save downloaded pages if it does not exists
    if not os.path.exists(PAGES_DIR):
        os.makedirs(PAGES_DIR)

    file_path = LIST_PAGE_FILEPATH if page_type == 'list' else VACANCY_PAGE_FILEPATH
    try:
        open(file_path, 'wb').write(r.content)
    except Exception as e:
        print('Can not download page: {}'.format(str(e)))
    return file_path


class ParserTestCase(unittest.TestCase):
    """
    Parser tests
    """
    def setUp(self):
        self.parser = NordseeParser()
        # check vacancies list file
        if not os.path.exists(LIST_PAGE_FILEPATH):
            get_test_page(page_type='list', url=LIST_PAGE_URL)

        # prepare test content from file
        self.list_page_content = pq(filename=LIST_PAGE_FILEPATH)

        # check vacancies details file
        if not os.path.exists(VACANCY_PAGE_FILEPATH):
            with patch.object(NordseeParser, '_get_page_content',
                              return_value=self.list_page_content):
                result = self.parser._get_common_vacancy_info(page=0)
            # get first vacancy url to save test page
            vacancy_url = result[0]['url']
            get_test_page(url=vacancy_url)

        # prepare test content from file
        self.vacancy_page_content = pq(filename=VACANCY_PAGE_FILEPATH)

    def test_get_pages_amount(self):
        """
        Test get_pages_amount method
        """
        with patch.object(NordseeParser, '_get_page_content',
                          return_value=self.list_page_content):
            result = self.parser._get_pages_amount()
            self.assertIsNotNone(result)
            self.assertEqual(type(result), int)

    def test_get_common_vacancy_info(self):
        """
        Test get_common_vacancy_info method
        """
        with patch.object(NordseeParser, '_get_page_content',
                          return_value=self.list_page_content):
            result = self.parser._get_common_vacancy_info(page=0)
            self.assertEqual(type(result), list)
            self.assertNotEqual(len(result), 0)

    def test_get_vacancy_data(self):
        """
        Test get_vacancy_data method
        """
        with patch.object(NordseeParser, '_get_page_content',
                          return_value=self.vacancy_page_content):
            result = self.parser._get_vacancy_data()
            self.assertEqual(type(result), dict)
            self.assertIn('introduction',result)
            self.assertIn('short_description', result)
            self.assertIn('details', result)
            self.assertIn('conclusion', result)

if __name__ == '__main__':
    unittest.main()
