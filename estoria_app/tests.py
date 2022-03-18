from .tasks import reader_xml, estoria_xml, critical_edition_first, bake_chapters
from .apps import EstoriaAppConfig

from django.apps import apps
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
from testfixtures import log_capture
from unittest.mock import patch
from selenium.webdriver import FirefoxOptions
import selenium
import os


def mocked_check_call(args, cwd):
    """"
    mock subprocess.check_call
    """
    return True


class TestEstoriaApp(TestCase):
    """
    Test apps.py
    """
    def test_apps(self):
        self.assertEqual(EstoriaAppConfig.name, 'estoria_app')
        self.assertEqual(apps.get_app_config('estoria_app').name, 'estoria_app')


class Test1EstoriaXml(TestCase):
    """
    Test estoria_xml Celery task
    """
    @log_capture('estoria_app.tasks')
    @patch('subprocess.check_call', side_effect=mocked_check_call)
    def test_estoria_xml_run_task(self, capture, mocked_check_call):
        """
        test the estoria_xml Celery task
        """
        data_path = settings.ESTORIA_DATA_PATH
        scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, 'estoria-digital/editions/src/assets/scripts')
        self.task = estoria_xml.apply(args=[data_path, scripts_path])
        self.results = self.task.get()
        self.assertEqual(self.task.state, 'SUCCESS')

        capture.check(
            ('estoria_app.tasks', 'INFO', '{}: estoria_xml task started'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG',
             '{}: Data path: {}'.format(self.task.id, settings.ESTORIA_DATA_PATH)),
            ('estoria_app.tasks',
             'DEBUG', '{}: Scripts location: {}'.format(self.task.id,
                                                        os.path.join(settings.ESTORIA_BASE_LOCATION,
                                                                     'estoria-digital/editions/src/assets/scripts'))),
            ('estoria_app.tasks', 'DEBUG', '{}: run make_paginated_json.py'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG', '{}: run add_html_to_paginated_json.py'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG', '{}: run make_chapter_index_json.py'.format(self.task.id)),
            ('estoria_app.tasks', 'INFO', '{}: complete'.format(self.task.id)),
        )


class Test2ReaderXml(TestCase):
    """
    Test reader_xml Celery task
    """
    @log_capture('estoria_app.tasks')
    @patch('subprocess.check_call', side_effect=mocked_check_call)
    def test_reader_xml_run_task(self, capture, mocked_check_call):
        """
        Test reader_xml Celery task
        """
        data_path = settings.ESTORIA_DATA_PATH
        scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, 'estoria-digital/editions/src/assets/scripts')
        self.task = reader_xml.apply(args=[data_path, scripts_path])
        self.results = self.task.get()
        self.assertEqual(self.task.state, 'SUCCESS')

        capture.check(
            ('estoria_app.tasks', 'INFO', '{}: reader_xml task started'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG',
             '{}: Data path: {}'.format(self.task.id, settings.ESTORIA_DATA_PATH)),
            ('estoria_app.tasks',
             'DEBUG', '{}: Scripts location: {}'.format(self.task.id,
                                                        os.path.join(settings.ESTORIA_BASE_LOCATION,
                                                                     'estoria-digital/editions/src/assets/scripts'))),
            ('estoria_app.tasks', 'DEBUG', '{}: run make_reader.py'.format(self.task.id)),
            ('estoria_app.tasks', 'INFO', '{}: complete'.format(self.task.id)),
        )


class Test3CriticalEditionFirst(TestCase):
    """
    Test test_critical_edition_first_run_task Celery task
    """
    @log_capture('estoria_app.tasks')
    @patch('subprocess.check_call', side_effect=mocked_check_call)
    def test_critical_edition_first_run_task(self, capture, mocked_check_call):
        """
        Test test_critical_edition_first_run_task Celery task
        """
        data_path = settings.ESTORIA_DATA_PATH
        scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, 'estoria-digital/editions/src/assets/scripts')
        self.task = critical_edition_first.apply(args=[data_path, scripts_path])
        self.results = self.task.get()
        self.assertEqual(self.task.state, 'SUCCESS')

        capture.check(
            ('estoria_app.tasks', 'INFO', '{}: critical_edition_first task started'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG',
             '{}: Data path: {}'.format(self.task.id, settings.ESTORIA_DATA_PATH)),
            ('estoria_app.tasks',
             'DEBUG', '{}: Scripts location: {}'.format(self.task.id,
                                                        os.path.join(settings.ESTORIA_BASE_LOCATION,
                                                                     'estoria-digital/editions/src/assets/scripts'))),
            ('estoria_app.tasks', 'DEBUG', '{}: run make_critical_chapter_verse_json.py'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG', '{}: run make_apparatus_index_page.py'.format(self.task.id)),
            ('estoria_app.tasks', 'INFO', '{}: complete'.format(self.task.id)),
        )


class Test4BakeChapters(TestCase):
    """
    Test bake_chapters Celery task
    """
    @patch.object(selenium.webdriver.FirefoxOptions, 'add_argument')
    @patch('selenium.webdriver.Firefox')
    @patch('builtins.open')
    @log_capture('estoria_app.tasks')
    def test_bake_chapters_run_task(self, capture, mocked_open, mocked_firefox):
        """
        Test bake_chapters Celery task
        """
        baking_url = os.path.join(settings.ADMIN_TOOLS_LOCATION, 'apparatus/estoria-digital')
        data_path = settings.ESTORIA_DATA_PATH
        self.task = bake_chapters.apply(args=(101, 101, baking_url, data_path))
        self.results = self.task.get()
        self.assertEqual(self.task.state, 'SUCCESS')
        self.assertTrue(mocked_open.called)
        self.assertTrue(mocked_firefox.called)

        capture.check(
            ('estoria_app.tasks', 'INFO', '{}: bake_chapters task started'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG', '{}: Baking chapters: 101 to 101'.format(self.task.id)),
            ('estoria_app.tasks', 'DEBUG', '{}: Bake chapter: 101'.format(self.task.id)),
            ('estoria_app.tasks', 'INFO', '{}: complete'.format(self.task.id)),
        )


# class Test5CriticalEditionLast(TestCase):
#     """
#     Test critical_edition_last Celery task
#     """
#     @log_capture('estoria_app.tasks')
#     @patch('subprocess.check_call', side_effect=mocked_check_call)
#     def test_critical_edition_last_run_task(self, capture):
#         """
#         Test critical_edition_last Celery task
#         """
#         self.task = critical_edition_last.apply()
#         self.results = self.task.get()
#         self.assertEqual(self.task.state, 'SUCCESS')
#
#         capture.check(
#             ('estoria_app.tasks', 'INFO', '{}: critical_edition_last task started'.format(self.task.id)),
#             ('estoria_app.tasks', 'DEBUG',
#              '{}: Estoria web location: {}'.format(self.task.id, settings.ESTORIA_LOCATION)),
#             ('estoria_app.tasks', 'DEBUG', '{}: Scripts location: {}'.format(self.task.id, settings.SCRIPTS_LOCATION)),
#             ('estoria_app.tasks', 'DEBUG', '{}: run make_chapter_index_json.py'.format(self.task.id)),
#             ('estoria_app.tasks', 'INFO', '{}: complete'.format(self.task.id)),
#         )


class TestIndexView(TestCase):
    """
    Test Index Views
    """
    def test_index_empty_get(self):
        """
        Test the simple index page is returned
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p>Management tools for the website.</p>')

    def test_index_nonempty_get(self):
        """
        Test the simple index page is returned
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('index')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p>Management tools for the website.</p>')


    # TODO add tests for selection of project if none selected


class TestTranscriptionsView(TestCase):
    """
    Test Transcriptions Views
    """
    def test_transcriptions_empty_get(self):
        """
        Empty GET request of the transcriptions page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Transcriptions</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_transcriptions_nonsense_get(self):
        """
        Nonsense GET request of the transcriptions page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Transcriptions</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_transcriptions_nonsense_post(self):
        """
        Nonsense POST request of the transcriptions page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.post(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Transcriptions</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_transcriptions_job_get(self):
        """
        'job' GET request of the transcriptions page
        should get the job status check page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.get(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Transcriptions</h1>')
        self.assertContains(response, '<p id="user-count">Checking the server for the task.</p>')

    @patch('estoria_app.tasks.estoria_xml.delay')
    def test_transcriptions_rebuild_post(self, mocked_task):
        """
        'rebuild' POST request of the transcriptions page
        should set off the task and push the user to the job status page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.post(url, {'rebuild': 'Rebuild'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)

    def test_transcriptions_upload_empty_post(self):
        """
        'upload' POST request of the transcriptions page, without a file
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        response = self.client.post(url, {'upload': 'Upload'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'There was a problem with the file upload')

    def test_transcriptions_upload_xmlfile_post(self):
        """
        'upload' POST request of the transcriptions page, with a valid XML file
        should upload the file and report success
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        faked_file = ContentFile('<a><b></b></a>')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'File uploaded')
        os.remove(os.path.join(settings.ESTORIA_BASE_LOCATION, session['project'], 'transcriptions/manuscripts/test.xml'))

    def test_transcriptions_upload_nonxmlfile_post(self):
        """
        'upload' POST request of the transcriptions page, with an invalid XML file
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('transcriptions')
        faked_file = ContentFile('hello world')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'The uploaded file is not valid XML')


class TestReaderxmlView(TestCase):
    """
    Test Reader XML Views
    """
    def test_readerxml_empty_get(self):
        """
        Empty GET request of the readerxml page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>ReaderXML</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_readerxml_nonsense_get(self):
        """
        Nonsense GET request of the readerxml page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>ReaderXML</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_readerxml_nonsense_post(self):
        """
        Nonsense POST request of the readerxml page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.post(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>ReaderXML</h1>')
        self.assertContains(response, '<form method="post" enctype="multipart/form-data">')

    def test_readerxml_job_get(self):
        """
        'job' GET request of the readerxml page
        should get the job status check page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.get(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>ReaderXML</h1>')
        self.assertContains(response, '<p id="user-count">Checking the server for the task.</p>')

    @patch('estoria_app.tasks.reader_xml.delay')
    def test_readerxml_rebuild_post(self, mocked_task):
        """
        'rebuild' POST request of the readerxml page
        should set off the task and push the user to the job status page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.post(url, {'rebuild': 'Rebuild'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)

    def test_readerxml_upload_empty_post(self):
        """
        'upload' POST request of the readerxml page, without a file
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        response = self.client.post(url, {'upload': 'Upload'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'There was a problem with the file upload')

    def test_readerxml_upload_xmlfile_post(self):
        """
        'upload' POST request of the readerxml page, with a valid XML file
        should upload the file and report success
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        faked_file = ContentFile('<a><b></b></a>')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'File uploaded')
        os.remove(os.path.join(settings.ESTORIA_BASE_LOCATION, session['project'], 'transcriptions/readerXML/test.xml'))

    def test_readerxml_upload_nonxmlfile_post(self):
        """
        'upload' POST request of the readerxml page, with an invalid XML file
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('readerxml')
        faked_file = ContentFile('hello world')
        faked_file.name = 'test.xml'
        response = self.client.post(url, {'upload': 'Upload', 'xmlfile': faked_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'The uploaded file is not valid XML')


class TestBakingView(TestCase):
    """
    Test Baking Views
    """
    def test_baking_empty_get(self):
        """
        Empty GET request of the baking page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')

    def test_baking_nonsense_get(self):
        """
        Nonsense GET request of the baking page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')

    def test_baking_nonsense_post(self):
        """
        Nonsense POST request of the baking page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')

    def test_baking_job_get(self):
        """
        'job' GET request of the baking page
        should get the job status check page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.get(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking Chapters</h1>')
        self.assertContains(response, '<p id="user-count">Checking the server for the task.</p>')

    @patch('estoria_app.tasks.bake_chapters.delay')
    def test_baking_sensible_range_post(self, mocked_task):
        """
        'range' POST request of the baking page, with sensible input
        should set off the task and push the user to the job status page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'range': 'Bake', 'start_chapter': 9, 'stop_chapter': 10})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)

    def test_baking_backwards_range_post(self):
        """
        'range' POST request of the baking page, with impossible input
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'range': 'Bake', 'start_chapter': 10, 'stop_chapter': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')
        self.assertEqual(response.context['message'], 'There was a problem with the supplied chapters to bake!')

    def test_baking_nonnumerical_range_post(self):
        """
        'range' POST request of the baking page, with non-numeric input
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'range': 'Bake', 'start_chapter': 'aaa', 'stop_chapter': 'bbb'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')
        self.assertEqual(response.context['message'], 'There was a problem with the supplied chapters to bake!')

    @patch('estoria_app.tasks.bake_chapters.delay')
    def test_baking_sensible_one_post(self, mocked_task):
        """
        'one' POST request of the baking page, with sensible input
        should set off the task and push the user to the job status page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'one': 'Bake', 'chapter': 5})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)

    def test_baking_nonnumerical_one_post(self):
        """
        'one' POST request of the baking page, with non-numerical input
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'one': 'Bake', 'chapter': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')
        self.assertEqual(response.context['message'], 'There was a problem with the supplied chapters to bake!')

    def test_baking_above_maximum_one_post(self):
        """
        'one' POST request of the baking page, with above maximum possible chapter input
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('apparatus')
        response = self.client.post(url, {'one': 'Bake', 'chapter': 1000000})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Baking</h1>')
        self.assertContains(response, '<form method="post">')
        self.assertEqual(response.context['message'], 'There was a problem with the supplied chapters to bake!')


class TestCriticalView(TestCase):
    """
    Test Critical Edition Views
    """
    def test_critical_empty_get(self):
        """
        Empty GET request of the critical edition page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('critical')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Critical Edition</h1>')
        self.assertContains(response, '<form method="post">')

    def test_critical_nonsense_get(self):
        """
        Nonsense GET request of the critical edition page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('critical')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Critical Edition</h1>')
        self.assertContains(response, '<form method="post">')

    def test_critical_nonsense_post(self):
        """
        Nonsense POST request of the critical edition page
        should get a form
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('critical')
        response = self.client.post(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Critical Edition</h1>')
        self.assertContains(response, '<form method="post">')

    def test_critical_job_get(self):
        """
        'job' GET request of the critical edition page
        should get the job status check page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('critical')
        response = self.client.get(url, {'job': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Critical Edition</h1>')
        self.assertContains(response, '<p id="user-count">Checking the server for the task.</p>')

    @patch('estoria_app.tasks.critical_edition_first.delay')
    def test_critical_rebuild_first_post(self, mocked_task):
        """
        'rebuildfirst' POST request of the critical edition page
        should set off the task and push the user to the job status page
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        url = reverse('critical')
        response = self.client.post(url, {'rebuildfirst': 'Rebuild First Part'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('?job='))
        self.assertTrue(mocked_task.called)

    def test_critical_rebuild_first_with_non_existent_page_post(self):
        """
        'rebuildfirst' POST request of the critical edition page when the collation index does not exist on the server
        (the problem with the index is done by messing, temporarily, with the file locations)
        should get an error message
        """
        session = self.client.session
        session['project'] = 'estoria-digital'
        session.save()
        estoria_location = settings.ESTORIA_DATA_PATH
        settings.ESTORIA_DATA_PATH = 'this_does_not_exist'
        url = reverse('critical')
        response = self.client.post(url, {'rebuildfirst': 'Rebuild First Part'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Critical Edition</h1>')
        self.assertContains(response, '<form method="post">')
        self.assertEqual(response.context['message'], 'There is a problem. The collation does not appear to exist.')
        settings.ESTORIA_DATA_PATH = estoria_location

    # @patch('estoria_app.tasks.critical_edition_last.delay')
    # def test_critical_rebuild_last_post(self, mocked_task):
    #     """
    #     'rebuildlast' POST request of the critical edition page
    #     should set off the task and push the user to the job status page
    #     """
    #     url = reverse('critical')
    #     response = self.client.post(url, {'rebuildlast': 'Rebuild Last Part'})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response['Location'].startswith('?job='))
