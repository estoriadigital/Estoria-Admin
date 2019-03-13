from .tasks import xmlconversion
from djangoproject.forms import UploadFileForm
from djangoproject.shared import validate_xml

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from celery.result import AsyncResult
from django.conf import settings
import tempfile
import os


def index(request):
    """
    index page, user uploads a file and this spawns the task to process the upload
    """
    message = ''
    form = UploadFileForm()

    if 'job' in request.GET:
        """
        If we have a GET request and 'job' in the request then we show the user the status of the job
        """
        task_id = request.GET['job']
        task = AsyncResult(task_id)
        context = {'result': task.result, 'state': task.state, 'task_id': task_id}
        return render(request, 'xmlconversion_app/show_result.html', context)

    elif 'file' in request.GET:
        """
        If we have a GET request and 'file' in the request then we return the zip file to the user
        """
        task_id = request.GET['file']
        task = AsyncResult(task_id)
        if task.result:
            file_and_path = os.path.join(settings.OUTPUT_LOCATION, task.result)
            if ('/' not in task.result) and os.path.isfile(file_and_path):
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=' + task.result
                response.write(open(file_and_path, 'rb').read())
                return response
            else:
                message = 'There was a problem with the file download'
        else:
            message = 'There was a problem with the task id'

    elif request.POST.get('upload'):
        """
        If we have a POST request and 'upload' in the request then we handle the file upload form 
        """
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            xmlfile = request.FILES['xmlfile']
            if validate_xml(xmlfile.read()):
                tempdir = tempfile.mkdtemp()
                with open(os.path.join(tempdir, xmlfile.name), 'wb+') as destination:
                    for chunk in xmlfile.chunks():
                        destination.write(chunk)
                task = xmlconversion.delay(xmlfile.name, tempdir)
                return HttpResponseRedirect('?job=' + task.id)
            else:
                message = 'The uploaded file is not valid XML'
        else:
            message = 'There was a problem with the file upload'

    # If we had an error above, then 'message' will be set and we show the message and the form
    # If the request was not one of the handled POST or GETs then show the form and 'message' is an empty string
    return render(request, 'xmlconversion_app/index.html', {'form': form, 'message': message})
