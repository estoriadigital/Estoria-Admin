from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
from django.conf import settings

from selenium import webdriver
# from selenium.webdriver import FirefoxOptions

import subprocess
import logging
import os

logger = logging.getLogger(__name__)


@shared_task
def estoria_xml():
    """
    update the Estoria site with the current transcription XML files
    """
    logger.info('{}: estoria_xml task started'.format(current_task.request.id))
    logger.debug('{}: Estoria web location: {}'.format(current_task.request.id, settings.ESTORIA_LOCATION))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, settings.SCRIPTS_LOCATION))

    logger.debug('{}: run make_paginated_json.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_paginated_json.py', '-d', settings.DATA_PATH], cwd=settings.SCRIPTS_LOCATION)

    logger.debug('{}: run add_html_to_paginated_json.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'add_html_to_paginated_json.py', '-d', settings.DATA_PATH], cwd=settings.SCRIPTS_LOCATION)

    logger.debug('{}: run make_chapter_index_json.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_chapter_index_json.py', '-d', settings.DATA_PATH], cwd=settings.SCRIPTS_LOCATION)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def reader_xml():
    """
    update the Estoria site with the current reader XML file
    """
    logger.info('{}: reader_xml task started'.format(current_task.request.id))
    logger.debug('{}: Estoria web location: {}'.format(current_task.request.id, settings.ESTORIA_LOCATION))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, settings.SCRIPTS_LOCATION))

    logger.debug('{}: run make_reader.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_reader.py', '-d', settings.DATA_PATH], cwd=settings.SCRIPTS_LOCATION)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def critical_edition_first():
    """
    the first part of updating the critical edition
    """
    logger.info('{}: critical_edition_first task started'.format(current_task.request.id))
    logger.debug('{}: Estoria web location: {}'.format(current_task.request.id, settings.ESTORIA_LOCATION))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, settings.SCRIPTS_LOCATION))

    logger.debug('{}: run make_critical_chapter_verse_json.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_critical_chapter_verse_json.py', '-d', settings.DATA_PATH], cwd=settings.SCRIPTS_LOCATION)

    logger.debug('{}: run make_apparatus_index_page.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_apparatus_index_page.py'], cwd=settings.SCRIPTS_LOCATION)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def critical_edition_last():
    """
    the last part of updating the critical edition
    """
    logger.info('{}: critical_edition_last task started'.format(current_task.request.id))
    logger.debug('{}: Estoria web location: {}'.format(current_task.request.id, settings.ESTORIA_LOCATION))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, settings.SCRIPTS_LOCATION))

    logger.debug('{}: run make_chapter_index_json.py'.format(current_task.request.id))
    subprocess.check_call(['python', 'make_chapter_index_json.py'], cwd=settings.SCRIPTS_LOCATION)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def bake_chapters(start, stop):
    """
    Use Selenium to get the live javascript rendered webpage and then save it
    requires a geckodriver to be somewhere in the PATH
    :param start: start with this chapter
    :param stop: stop at this chapter (inclusive)
    """
    logger.info('{}: bake_chapters task started'.format(current_task.request.id))
    logger.debug('{}: Baking chapters: {} to {}'.format(current_task.request.id, start, stop))

    # opts = FirefoxOptions()
    # opts.add_argument("--headless")
    driver = webdriver.Firefox()

    for i in range(start, stop+1):
        logger.debug('{}: Bake chapter: {}'.format(current_task.request.id, i))
        url = settings.BAKING_WEBPAGES_BASEURL + 'chapter/?chapter={}'.format(i)
        driver.get(url)
        container = driver.find_element_by_class_name('container').get_attribute('innerHTML')
        with open(os.path.join(settings.ESTORIA_LOCATION, 'edition/critical', str(i) + '.html'), 'w',
                  encoding='utf-8') as f:
            f.write(container)

    logger.info('{}: complete'.format(current_task.request.id))
