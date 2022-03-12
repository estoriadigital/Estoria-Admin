from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
from django.conf import settings
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import subprocess
import logging
import os

logger = logging.getLogger(__name__)
python_path = os.path.join(settings.VIRTUAL_ENV_PATH, 'bin', 'python3')

@shared_task
def estoria_xml(data_path, scripts_path):
    """
    update the Estoria site with the current transcription XML files
    """
    logger.info('{}: estoria_xml task started'.format(current_task.request.id))
    logger.debug('{}: Data path: {}'.format(current_task.request.id, data_path))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))

    logger.debug('{}: run make_paginated_json.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_paginated_json.py', '-d', data_path], cwd=scripts_path)

    logger.debug('{}: run add_html_to_paginated_json.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'add_html_to_paginated_json.py', '-d', data_path], cwd=scripts_path)

    logger.debug('{}: run make_chapter_index_json.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_chapter_index_json.py', '-d', data_path], cwd=scripts_path)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def reader_xml(data_path, scripts_path):
    """
    update the Estoria site with the current reader XML file
    """
    logger.info('{}: reader_xml task started'.format(current_task.request.id))
    logger.debug('{}: Data path: {}'.format(current_task.request.id, data_path))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))

    logger.debug('{}: run make_reader.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_reader.py', '-d', data_path], cwd=scripts_path)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def translation_xml(data_path, scripts_path):
    """
    update the Estoria site with the current reader XML file
    """
    logger.info('{}: translation_xml task started'.format(current_task.request.id))
    logger.debug('{}: Data path: {}'.format(current_task.request.id, data_path))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))

    logger.debug('{}: run make_translation.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_translation.py', '-d', data_path], cwd=scripts_path)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def cpsf_critical_xml(data_path, scripts_path):
    """
    update the Estoria site with the current reader XML file
    """
    logger.info('{}: cpsf_critical_xml task started'.format(current_task.request.id))
    logger.debug('{}: Data path: {}'.format(current_task.request.id, data_path))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))

    logger.debug('{}: run make_cpsf_critical.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_cpsf_critical.py', '-d', data_path], cwd=scripts_path)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def critical_edition_first(data_path, scripts_path):
    """
    the first part of updating the critical edition
    """
    logger.info('{}: critical_edition_first task started'.format(current_task.request.id))
    logger.debug('{}: Data path: {}'.format(current_task.request.id, data_path))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))

    logger.debug('{}: run make_critical_chapter_verse_json.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_critical_chapter_verse_json.py', '-d', data_path], cwd=scripts_path)

    logger.debug('{}: run make_verse_page_index_json.py'.format(current_task.request.id))
    subprocess.check_call([python_path, 'make_verse_page_index_json.py', '-d', data_path], cwd=scripts_path)

    logger.info('{}: complete'.format(current_task.request.id))


@shared_task
def bake_chapters(start, stop, baking_url, data_path):
    """
    Use Selenium to get the live javascript rendered webpage and then save it
    requires a geckodriver to be somewhere in the PATH
    :param start: start with this chapter
    :param stop: stop at this chapter (inclusive)
    """
    logger.info('{}: bake_chapters task started'.format(current_task.request.id))
    logger.debug('{}: Baking chapters: {} to {}'.format(current_task.request.id, start, stop))
    try:
        os.makedirs(os.path.join(data_path, 'critical'))
    except FileExistsError:
        pass

    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    for i in range(start, stop+1):
        logger.debug('{}: Bake chapter: {} at {}'.format(current_task.request.id, i, baking_url))
        url = baking_url + '/chapter/{}'.format(i)
        driver.get(url)
        container = driver.find_element_by_class_name('container').get_attribute('innerHTML')
        with open(os.path.join(data_path, 'critical', str(i) + '.html'), 'w',
                  encoding='utf-8') as f:
            f.write(container)

    logger.info('{}: complete'.format(current_task.request.id))
