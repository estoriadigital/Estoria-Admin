from .tasks import xmlconversion, replace_line
from .apps import XmlconversionAppConfig

from django.apps import apps
from django.test import TestCase
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings

from testfixtures import log_capture
from unittest.mock import patch
from types import SimpleNamespace
from celery import result
import celery
import tempfile
import re
import os


class TestXmlconversionApp(TestCase):
    """
    Test apps.py
    """
    def test_apps(self):
        self.assertEqual(XmlconversionAppConfig.name, 'xmlconversion_app')
        self.assertEqual(apps.get_app_config('xmlconversion_app').name, 'xmlconversion_app')


class TestXmlconversion(TestCase):
    """
    Test Celery tasks
    """
    @patch('subprocess.check_call')
    @patch('os.makedirs')
    @patch('shutil.move')
    @patch('shutil.copytree')
    @patch('shutil.copy')
    @patch('builtins.open', create=True)
    @patch('json.loads')
    @patch('shutil.rmtree')
    @patch('shutil.make_archive')
    @patch('xmlconversion_app.tasks.replace_line')
    @log_capture('xmlconversion_app.tasks')
    def test_xmlconversion_run_task(self, mocked_check_call, mocked_makedirs, mocked_move,
                                    mocked_copytree, mocked_copy, mocked_open, mocked_json_loads, mocked_rmtree,
                                    mocked_make_archive, mocked_replace_line, capture):
        """
        Test the xmlconversion task
        A pile of functions are mocked
        """
        self.task = xmlconversion.apply(args=('Y.xml', 'tmp'))
        self.results = self.task.get()
        self.assertEqual(self.task.state, 'SUCCESS')
        self.assertTrue(mocked_check_call.called)
        #self.assertTrue(mocked_check_output.called)
        self.assertTrue(mocked_makedirs.called)
        self.assertTrue(mocked_move.called)
        self.assertTrue(mocked_copytree.called)
        self.assertTrue(mocked_copy.called)
        self.assertTrue(mocked_rmtree.called)
        self.assertTrue(mocked_make_archive.called)
        self.assertTrue(mocked_replace_line.called)

        capture.check(
            ('xmlconversion_app.tasks', 'INFO', '{}: xmlconversion task started'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: Scripts location: {}'.format(self.task.id, os.path.join(settings.ESTORIA_BASE_LOCATION, 'estoria-digital/edition/src/assets/scripts'))),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: Resources location: {}'.format(self.task.id, settings.RESOURCES_LOCATION)),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: Output location: {}'.format(self.task.id, settings.OUTPUT_LOCATION)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: Temporary directory: {}'.format(self.task.id, 'tmp')),

            ('xmlconversion_app.tasks', 'DEBUG', '{}: create directory structure'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: add XML'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: copy over scripts'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: run make_paginated_json.py'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: run add_html_to_paginated_json.py'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: move edition/transcription/[dirname] to output/json'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: copy in the js/css/font packages to output'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: move edition/static/data/menu_data.js to '
             'output/static/js/data_menu.js and edit the second line'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG',
             '{}: zip up the result and copy to output location'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'DEBUG', '{}: delete the unneeded tmp folder'.format(self.task.id)),
            ('xmlconversion_app.tasks', 'INFO',
             '{}: complete, so return the zip filename {}'.format(self.task.id, re.sub('^/tmp/', '', 'tmp'))),
        )

    def test_replace_line(self):
        """
        Test the replace_line function
        Provide a temporary file, replace a line in it
        """
        with tempfile.NamedTemporaryFile('w', delete=False) as tfile:
            tfile.write('line one\nline two\nline three')
        replace_line(tfile.name, 2, 'new line two\n')
        with open(tfile.name) as tfile:
            filecontents = tfile.read()
        self.assertEqual(filecontents, 'line one\nnew line two\nline three')
        os.remove(tfile.name)


class TestIndexView(TestCase):
    """
    Test Index Views
    """
    def _mocked_xmlconversion(a, b):
        """
        fake the response of xmlconversion.delay()
        the two inputs are unimportant
        outputs an id of 'fakeid', so that task.id works
        """
        d = {'id': 'fakeid'}
        return SimpleNamespace(**d)

    def test_index_empty_get(self):
        """
        Empty GET request of the index page
        should get a form
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_index_nonsense_get(self):
        """
        Nonsense GET request of the index page
        should get a form
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_index_job_get(self):
        """
        'job' GET request of the index page
        should get the job status check page
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<p id="user-count">Checking the server for the task.</p>')

    def test_index_job_post(self):
        """
        'job' POST request of the index page
        should get a form
        """
        url = reverse('xmlconversion-index')
        response = self.client.post(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_index_nonsense_post(self):
        """
        Nonsense POST request of the index page
        should get a form
        """
        url = reverse('xmlconversion-index')
        response = self.client.post(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_index_upload_get(self):
        """
        'upload' GET request of the index page
        should get a form
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'upload': 'Upload'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_index_upload_empty_post(self):
        """
        'upload' POST request of the index page, without a file
        should get an error message
        """
        url = reverse('xmlconversion-index')
        response = self.client.post(url, {'upload': 'Upload'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'There was a problem with the file upload')

    @patch('xmlconversion_app.tasks.xmlconversion.delay', side_effect=_mocked_xmlconversion)
    @patch('tempfile.mkdtemp')
    @patch('builtins.open')
    def test_index_upload_xmlfile_post(self, mocked_task, mocked_mkdtemp, mocked_open):
        """
        'upload' POST request of the index page, with a valid XML file
        should set off the task and push the user to the job status page
        """
        url = reverse('xmlconversion-index')
        faked_file = ContentFile('<a><b></b></a>')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)
        self.assertTrue(mocked_mkdtemp.called)
        self.assertTrue(mocked_open.called)

    def test_index_upload_nonvalidxmlfile_post(self):
        """
        'upload' POST request of the index page, with a invalid XML file
        should get an error message
        """
        url = reverse('xmlconversion-index')
        faked_file = ContentFile('hello world')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'The uploaded file is not valid XML')

    def test_index_download_file_bad_id_get(self):
        """
        'file' GET request of the index page, with a invalid job id
        should get an error message
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'file': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')
        self.assertEqual(response.context['message'], 'There was a problem with the task id')

    @patch.object(celery.result.AsyncResult, 'result', '')
    def test_index_download_file_no_id_get(self):
        """
        'file' GET request of the index page, with a n job id
        should get an error message
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'file': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')
        self.assertEqual(response.context['message'], 'There was a problem with the task id')

    @patch.object(celery.result.AsyncResult, 'result', 'collations.json')
    def test_index_download_file_existent_file_get(self):
        """
        'file' GET request of the index page, with a valid job id and a real file
        should get the file back
        """
        output_location = settings.OUTPUT_LOCATION
        settings.OUTPUT_LOCATION = settings.ESTORIA_DATA_PATH
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'file': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        settings.OUTPUT_LOCATION = output_location

    @patch.object(celery.result.AsyncResult, 'result', 'onion')
    def test_index_download_file_nonexistent_file_get(self):
        """
        'file' GET request of the index page, with a valid job id and no file
        should get an error message
        """
        url = reverse('xmlconversion-index')
        response = self.client.get(url, {'file': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>XML to JSON Conversion</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')
        self.assertEqual(response.context['message'], 'There was a problem with the file download')
