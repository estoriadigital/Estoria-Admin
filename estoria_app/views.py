from .tasks import estoria_xml, reader_xml, critical_edition_first, bake_chapters
from djangoproject.forms import UploadFileForm, RangeForm
from djangoproject.shared import validate_xml

from django.shortcuts import render
from django.http import HttpResponseRedirect
from celery.result import AsyncResult
from django.conf import settings
import os
import json
import collections

# TODO: everything in here is to be restricted, via a http digest password


def _upload_and_process_xml(request, celery_task, file_location, template, title):
    """
    combined function for the transcriptions and readerxml pages
    :param request: the Django request
    :param celery_task: the name of the Celery task to be run
    :param file_location: the destination for the xml file to be written too
    :param template: the template for render() to use
    :return: the render object
    """
    message = ''
    form = UploadFileForm()

    if 'job' in request.GET:
        """
        If we have a GET request and 'job' in the request then we show the user the status of the job
        """
        task_id = request.GET['job']
        task = AsyncResult(task_id)
        context = {'result': task.result, 'state': task.state, 'task_id': task_id, 'title': title}
        return render(request, 'estoria_app/show_result.html', context)

    elif request.POST.get('rebuild'):
        """
        If we have a POST request and 'rebuild' in the request then we set off the relevant task
        and send the user to the job result page
        """
        task = celery_task.delay()
        return HttpResponseRedirect('?job={}'.format(task.id))

    elif request.POST.get('upload'):
        """
        If we have a POST request and 'upload' in the request then we handle the file upload form
        """
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            xmlfile = request.FILES['xmlfile']
            if validate_xml(xmlfile.read()):
                with open(os.path.join(file_location, xmlfile.name), 'wb+') as destination:
                    for chunk in xmlfile.chunks():
                        destination.write(chunk)
                message = 'File uploaded'
            else:
                message = 'The uploaded file is not valid XML'
        else:
            message = 'There was a problem with the file upload'

    # If we had an error above, then 'message' will be set and we show the message and the form
    # If the request was not one of the handled POST or GETs then show the form and 'message' is an empty string
    return render(request, template, {'form': form, 'message': message})


def index(request):
    """
    index page, which provides links to the other sections
    """
    return render(request, 'estoria_app/index.html', {})


def transcriptions(request):
    """
    transcriptions page, deals with file upload and allows the user to spawn off the update task
    """
    return _upload_and_process_xml(request, estoria_xml, os.path.join(settings.ESTORIA_LOCATION, 'transcriptions', 'manuscripts'),
                                   'estoria_app/transcriptions.html', 'Transcriptions')


def readerxml(request):
    """
    reader xml page, deals with file upload and allows the user to spawn off the update task
    """
    return _upload_and_process_xml(request, reader_xml, os.path.join(settings.ESTORIA_LOCATION, 'transcriptions', 'readerXML'),
                                   'estoria_app/readerxml.html', 'ReaderXML')


def apparatus(request):
    """
    baking - allows the user to select either a chapter to bake or a range of chapters
    """
    message = ''
    form = RangeForm()

    with open(os.path.join(settings.ESTORIA_LOCATION, 'edition/apparatus/collations.json'), encoding='utf-8') as fp:
        data = json.load(fp, object_pairs_hook=collections.OrderedDict)
    maximum_chapter = int(next(reversed(data)))

    if 'job' in request.GET:
        """
        If we have a GET request and 'job' in the request then we show the user the status of the job
        """
        task_id = request.GET['job']
        task = AsyncResult(task_id)
        context = {'result': task.result, 'state': task.state, 'task_id': task_id, 'title': 'Baking Chapters'}
        return render(request, 'estoria_app/show_result.html', context)

    elif request.POST.get('range') or request.POST.get('one'):
        """
        If we have a POST request and 'range' or 'one' is in the request then we check that the input is valid
        If it is valid then we set off the bake_chapters task and send the user to the job result page
        """
        if request.POST.get('range'):
            if request.POST.get('start_chapter').isdigit():
                start = int(request.POST.get('start_chapter'))
            else:
                start = -1
            if request.POST.get('stop_chapter').isdigit():
                stop = int(request.POST.get('stop_chapter'))
            else:
                stop = -1
        else:
            if request.POST.get('chapter').isdigit():
                start = stop = int(request.POST.get('chapter'))
            else:
                start = stop = -1

        if 1 <= start <= stop <= maximum_chapter:
            task = bake_chapters.delay(start, stop)
            return HttpResponseRedirect('?job={}'.format(task.id))
        else:
            message = 'There was a problem with the supplied chapters to bake!'
            form = RangeForm(request.POST)

    return render(request, 'estoria_app/app_list.html',
                  {'form': form, 'data': data, 'message': message, 'location': settings.BAKING_WEBPAGES_BASEURL})


def chapter(request, chapter):
        data = {'chapter': chapter,
                'collations_path': os.path.join(settings.ESTORIA_EDITION_LOCATION, 'data', 'collation', 'approved')}
        return render(request, 'estoria_app/chapter_check.html', data)

def sentence(request, context):
    data = {'context': context,
            'collations_path': os.path.join(settings.ESTORIA_EDITION_LOCATION, 'data', 'collation', 'approved')}
    return render(request, 'estoria_app/sentence_check.html', data)


def critical(request):
    """
    critical edition page
    """
    message = ''
    if 'job' in request.GET:
        """
        If we have a GET request and 'job' in the request then we show the user the status of the job
        """
        task_id = request.GET['job']
        task = AsyncResult(task_id)
        context = {'result': task.result, 'state': task.state, 'task_id': task_id, 'title': 'Critical Edition'}
        return render(request, 'estoria_app/show_result.html', context)

    elif request.POST.get('rebuildfirst'):
        """
        If we have a POST request and 'rebuildfirst' in the request then we set off the critical_edition_first task
        and send the user to the job result page
        """
        if os.path.islink(os.path.join(settings.ESTORIA_LOCATION, 'edition/apparatus/collation')):
            task = critical_edition_first.delay()
            return HttpResponseRedirect('?job={}'.format(task.id))
        else:
            message = 'There is a problem. The collation does not appear to exist.'

    return render(request, 'estoria_app/critical.html', {'message': message})
