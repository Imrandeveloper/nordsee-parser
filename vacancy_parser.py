import os
import logging
import requests as rq

from lxml import etree
from pyquery import PyQuery as pq
from fake_useragent import UserAgent

logging.basicConfig(filename='logs.log', level=logging.INFO)


class NordseeParser:
    """
    Parser for https://karriere.nordsee.com
    """

    VACANCY_LIST_URL = 'https://karriere.nordsee.com/de/stellenangebote.html'
    UA_SUFFIX = 'JobUFO GmbH'
    OUTPUT_DIR = 'parsed_xml'
    OUTPUT_FILENAME = 'nordsee.xml'

    def __init__(self):
        """
        Initialize parser
        """
        self.user_agent = UserAgent()

    @property
    def _request_settings(self):
        """
        Settings to make requests with random user agent
        :return: dict with settings
        """
        return {
            'timeout': 60,
            'headers': {'User-Agent': '{} {}'.format(self.user_agent.random,
                                                     self.UA_SUFFIX)},
            'verify': False,
        }

    def _get_page_content(self, url, params=None):
        try:
            return rq.get(url, params=params, **self._request_settings).content
        except Exception as e:
            logging.info('Can not get page: {}'.format(str(e)))

    def _get_pages_amount(self):
        """
        Get vacancy pages amount
        :return: int
        """
        content = self._get_page_content(url=self.VACANCY_LIST_URL)
        d = pq(content)

        pages_amount = int(d('.nav_item:last a').text())
        logging.info('Count of vacancies pages is {}'.format(pages_amount))
        return pages_amount

    def _get_common_vacancy_info(self, page=0):
        """
        Get common vacancy info from vacancy list page
        :param page: int page number
        :return: list of common vacancy info
        """
        vacancy_info_list = []
        params = {'start': page * 20}
        content = self._get_page_content(url=self.VACANCY_LIST_URL, params=params)
        d = pq(content)

        rows = d('#joboffers tbody tr').items()
        for row in rows:
            common_info = {
                'url': row.find('.real_table_col1 a').attr('href'),
                'title': row.find('.real_table_col1 a').text(),
                'location': row.find('.real_table_col2').text(),
                'position': row.find('.real_table_col4').text()
            }
            vacancy_info_list.append(common_info)
        logging.info('Urls parsed')
        return vacancy_info_list

    def _get_vacancy_data(self, vacancy_url=None):
        """
        Get data from vacancy page
        :param vacancy_url: vacancy url
        :return: dict with vacancy data
        """
        content = self._get_page_content(url=vacancy_url)
        d = pq(content)

        logging.info('Vacancies data got')
        content = d('.emp_nr_innerframe')

        search_from_el = d('.trenner')
        details = search_from_el.nextAll().filter(
            lambda i, this: not pq(this).hasClass('abschluss'))

        vacancy_data = {
            'introduction': content.find('.einleitungstext').text(),
            'short_description': content.find('.mitteltext').text(),
            'details': details.text(),
            'conclusion': content.find('.abschluss').text()
        }
        return vacancy_data

    def _save_to_xml(self, vacancy_list):
        """
        Save parsed vacancies to xml file
        :param vacancy_list: list of vacancies info
        :return: str filepath
        """
        root = etree.Element('vacancies')
        for data in vacancy_list:
            vacancy = etree.SubElement(root, 'vacancy')
            etree.SubElement(vacancy, 'url').text = data['url']
            etree.SubElement(vacancy, 'title').text = data['title']
            etree.SubElement(vacancy, 'location').text = data['location']
            etree.SubElement(vacancy, 'position').text = data['position']
            etree.SubElement(vacancy, 'introduction').text = \
                data['introduction']
            etree.SubElement(vacancy, 'short_description').text = \
                data['short_description']
            etree.SubElement(vacancy, 'details').text = \
                data['details']
            etree.SubElement(vacancy, 'conclusion').text = \
                data['conclusion']

        current_dir = os.path.dirname(os.path.realpath(__file__))
        dir_to_export = os.path.join(current_dir, self.OUTPUT_DIR)

        # create directory to save parsed xml if it does not exists
        if not os.path.exists(dir_to_export):
            os.makedirs(dir_to_export)

        filepath = os.path.join(dir_to_export, self.OUTPUT_FILENAME)

        tree = etree.ElementTree(root)
        tree.write(filepath, pretty_print=True, xml_declaration=True,
                   encoding='utf-8')
        return filepath

    def run(self):
        """
        Run parsing process
        :return:
        """
        vacancy_list = []
        pages_amount = self._get_pages_amount()

        for page in range(pages_amount):
            vacancy_common_info = self._get_common_vacancy_info(page)
            for info_item in vacancy_common_info:
                vacancy_data = self._get_vacancy_data(info_item['url'])
                vacancy_data.update(info_item)
                vacancy_list.append(vacancy_data)

        self._save_to_xml(vacancy_list)
        return True


if __name__ == "__main__":
    parser = NordseeParser()
    parser.run()
