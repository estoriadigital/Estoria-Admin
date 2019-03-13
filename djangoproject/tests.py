from .shared import validate_xml, poll_state

from django.test import TestCase
from django.urls import reverse
import json


class TestIndexView(TestCase):
    """
    Test Index Views
    """
    def test_index_empty_get(self):
        """
        Empty GET request of the index page
        """
        url = reverse('base')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ValidateXMLTest(TestCase):
    """
    Test the validate XML function
    """
    def test_invalid_xml_should_be_false(self):
        """
        test with invalid xml
        should get False
        """
        xml = b'<a><b></c></a>'
        self.assertIs(validate_xml(xml), False)

    def test_valid_xml_should_be_true(self):
        """
        test with valid xml
        should get True
        """
        xml = b'<a><b></b></a>'
        self.assertIs(validate_xml(xml), True)


class PollStateTest(TestCase):
    """
    Test the PollStateTest function
    """
    def test_poll_state_nonajax(self):
        """
        test with a non ajax GET
        should be rejected
        """
        response = self.client.get(reverse('poll_state'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertJSONEqual(json.dumps(response.json()),
                             json.dumps({'result': 'This is not an ajax request', 'state': 'FAILURE'}))

    def test_poll_state_ajax_no_task_id(self):
        """
        test with a ajax GET, but no id
        should be rejected
        """
        response = self.client.post(reverse('poll_state'), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertJSONEqual(json.dumps(response.json()),
                             json.dumps({'result': 'No task_id in the request', 'state': 'FAILURE'}))

    def test_poll_state_ajax_with_task_id(self):
        """
        test with a ajax GET and id
        should get correct response
        """
        response = self.client.post(reverse('poll_state'), {'task_id': 'aaa'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
