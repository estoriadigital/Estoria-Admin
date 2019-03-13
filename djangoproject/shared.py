from django.http import HttpResponse
from celery.result import AsyncResult
from lxml import etree
from io import BytesIO
import json


def validate_xml(xml_to_check):
    """
    validate the xml of the supplied input
    :param xml_to_check: bytes object which is the xml to be validated
    :return: True or False
    """
    try:
        etree.parse(BytesIO(xml_to_check))
        return True
    except etree.XMLSyntaxError:
        return False


def poll_state(request):
    """
    check the current state of a task
    :param request: the Django request
    :return: the HttpResponse object
    """
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            context = {'result': task.result, 'state': task.state }
        else:
            context = {'result': 'No task_id in the request', 'state': 'FAILURE'}
    else:
        context = {'result': 'This is not an ajax request', 'state': 'FAILURE'}

    json_data = json.dumps(context)
    return HttpResponse(json_data, content_type='application/json')
