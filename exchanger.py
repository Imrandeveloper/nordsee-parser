import os
import sys
import json
import time
import logging
import requests

from splinter import Browser

logging.basicConfig(filename='logs.log', level=logging.INFO)

"""Settings for local testing on Linux/Mac with Chrome driver"""

LINUX_PLATFORM = 'linux'
MAC_PLATFORM = 'darwin'

WEB_DRIVERS = {
    LINUX_PLATFORM: 'chromedriver_linux_x64',
    MAC_PLATFORM: 'chromedriver_darwin'
}

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
try:
    DRIVER_PATH = os.path.join(CURRENT_PATH, 'drivers',
                               WEB_DRIVERS[sys.platform])
except:
    raise Exception


class Exchanger:
    """
    Class to apply for job with user data
    """

    DOWNLOADS_DIR = 'downloads'
    DEFAULT_VALUES = {
        'german_level': 'Fließend',
        'nationality': 'EU mit unbefristeter Arbeitserlaubnis',
        'source': 'JobUFO',
        'country': 'Deutschland'
    }

    def __init__(self, vacancy_url, user_data):
        """
        Init class
        :param vacancy_url: url of vacancy page
        :param user_data: dict with user data
        """
        self.browser = self._setup_browser()
        self.vacancy_url = vacancy_url
        self.user_data = user_data

    @staticmethod
    def _setup_browser():
        """
        Prepare splinter browser
        :return: Browser
        """
        options = {'executable_path': DRIVER_PATH, 'headless': True}
        return Browser('chrome', **options)

    def _open_page(self):
        """
        Visit vacancy page and apply for job
        """
        logging.info('Open page')
        self.browser.visit(self.vacancy_url)
        self.browser.find_by_id('btn_online_application').click()

    def _fill_inputs(self):
        """
        Fill required fields (standard inputs)
        """
        logging.info('Fill unputs')
        # fill first name
        self.browser.fill('bewerbung_form[vorname]',
                          self.user_data['first_name'])
        # fill last name
        self.browser.fill('bewerbung_form[nachname]',
                          self.user_data['last_name'])
        # fill street
        self.browser.fill('bewerbung_form[strasse]',
                          self.user_data['street'])
        # fill postal code
        self.browser.fill('bewerbung_form[plz]',
                          self.user_data['postal_code'])
        # fill city
        self.browser.fill('bewerbung_form[ort]', self.user_data['city'])
        # fill phone
        self.browser.fill('bewerbung_form[telefon]',
                          self.user_data['phone'])
        # fill email
        self.browser.fill('bewerbung_form[mail]', self.user_data['email'])
        # fill birthday
        self.browser.fill('bewerbung_form[geburtsdatum]',
                          self.user_data['birthday'])
        self.browser.find_by_id('handy').last.click()

    def _select_sex(self):
        """
        Fill select input 'sex'
        """
        logging.info('Fill sex')
        self.browser.execute_script("window.scrollTo(398, 16)")
        self.browser.find_by_id('sex_w-button').click()
        value = 'Herr' if self.user_data['gender'] == 'M' else 'Frau'
        self.browser.find_by_css('.ui-selectmenu-open').find_by_text(
            value).last.click()

    def _select_country(self):
        """
        Fill select input 'country'
        """
        logging.info('Fill country')
        self.browser.find_by_id('country-button').click()
        self.browser.find_by_css('.ui-selectmenu-open').find_by_text(
            self.DEFAULT_VALUES['country']).last.click()

    def _select_nationality(self):
        """
        Fill select input 'nation'
        """
        logging.info('Fill nationality')
        self.browser.find_by_id('nation-button').click()
        # fill input with default value
        self.browser.find_by_css('.ui-selectmenu-open').find_by_text(
            self.DEFAULT_VALUES['nationality']).last.click()

    def _select_source(self):
        """
        Fill select input 'source'
        """
        logging.info('Fill source')
        self.browser.find_by_id('wie_gefunden-button').click()
        # fill input with default value
        self.browser.find_by_css('.ui-selectmenu-open').find_by_text(
            self.DEFAULT_VALUES['source']).last.click()

    def _select_german_level(self):
        """
        Fill select input 'german level'
        """
        logging.info('Fill german level')
        self.browser.find_by_id('berufsausbildung_m_sb-button').click()
        # fill input with default value
        self.browser.find_by_css('.ui-selectmenu-open').find_by_text(
            self.DEFAULT_VALUES['german_level']).last.click()

    def _fill_selects(self):
        """
        Fill required selects
        """
        self._select_sex()
        self._select_country()
        self._select_nationality()
        self._select_source()
        self._select_german_level()

    def _download_file(self):
        """
        Download cv file
        :return: str file path
        """
        logging.info('Download file')
        file_url = self.user_data['cv_path']
        r = requests.get(file_url, allow_redirects=True)
        filename = file_url.rsplit('/', 1)[1]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        downloads_dir = os.path.join(current_dir, self.DOWNLOADS_DIR)

        # create directory to save downloaded cv file if it does not exists
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        file_path = os.path.join(downloads_dir, filename)
        try:
            open(file_path, 'wb').write(r.content)
        except Exception as e:
            logging.info('Can not download file: {}'.format(str(e)))
        return file_path

    def _upload_file(self):
        """
        Upload file
        """
        logging.info('Upload file')
        file_path = self._download_file()
        try:
            self.browser.attach_file('anlage2', file_path)
        except Exception as e:
            logging.info('Can not upload file: {}'.format(str(e)))
        # wait until the file is uploaded
        while self.browser.is_element_not_present_by_css('.modal_link'):
            time.sleep(1)

    def _click_agree(self):
        """
        Click agree
        """
        logging.info('Click agree')
        while self.browser.is_element_not_present_by_id('agreement'):
            time.sleep(1)
        self.browser.find_by_id('agreement').find_by_css(
            '.agreement_new').last.click()

    def _submit(self):
        """
        Submit vacancy form
        """
        logging.info('Click submit')
        self.browser.find_by_id('btn_online_application_send').click()

    def _has_error(self):
        """
        Check submit page for error
        """
        logging.info('Check error')
        try:
            self.browser.is_element_not_present_by_css('.error_msg', 3)
            error_msg = self.browser.find_by_css('.error_msg').first.text
            return error_msg
        except Exception:
            return False

    def run(self):
        """
        Run process of applying job
        """
        self._open_page()
        self._upload_file()
        self._fill_inputs()
        self._fill_selects()
        self._click_agree()
        self._submit()
        error = self._has_error()
        if error:
            logging.info('Can not submit form :{}'.format(error))
        else:
            logging.info('Submitted successfully')
        self.browser.quit()


if __name__ == "__main__":
    test_url = 'https://karriere.nordsee.com/de/' \
               'Verkaeufer-Mitarbeiter-Restaurant-mw-in-Berlin-de-j2496.html'
    test_data = json.load(open('nordsee_test.json'))
    parser = Exchanger(user_data=test_data, vacancy_url=test_url)
    parser.run()
