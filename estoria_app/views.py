from .tasks import estoria_xml, reader_xml, translation_xml, cpsf_critical_xml, critical_edition_first, bake_chapters
from djangoproject.forms import UploadFileForm, RangeForm
from djangoproject.shared import validate_xml

from django.shortcuts import render
from django.urls import reverse
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
        scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, request.session['project'], 'edition/src/assets/scripts')
        if request.session['project'] == 'estoria-digital':
            data_path = settings.ESTORIA_DATA_PATH
        elif request.session['project'] == 'cpsf-digital':
            data_path = settings.CPSF_DATA_PATH

        task = celery_task.delay(data_path, scripts_path)
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

    return render(request, template, {'form': form, 'message': message, 'current_project': request.session['project']})


def index(request):
    """
    index page, which provides links to the other sections
    """
    if request.method == 'POST':
        request.session['project'] = request.POST.get('project')

    data = {}
    if 'project' in request.session:
        data['current_project'] = request.session['project']

    return render(request, 'estoria_app/index.html', data)


def transcriptions(request):
    """
    transcriptions page, deals with file upload and allows the user to spawn off the update task
    """
    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))
    transcription_location = os.path.join(settings.ESTORIA_BASE_LOCATION,
                                          request.session['project'],
                                          'transcriptions',
                                          'manuscripts')
    return _upload_and_process_xml(request, estoria_xml, transcription_location,
                                   'estoria_app/transcriptions.html',
                                   'Transcriptions')


def readerxml(request):
    """
    reader xml page, deals with file upload and allows the user to spawn off the update task
    """
    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

    transcription_location = os.path.join(settings.ESTORIA_BASE_LOCATION,
                                          request.session['project'],
                                          'transcriptions',
                                          'readerXML')
    return _upload_and_process_xml(request, reader_xml, transcription_location,
                                   'estoria_app/readerxml.html', 'ReaderXML')


def translation(request):
    """
    translation page, deals with file upload and allows the user to spawn off the update task
    """
    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

    transcription_location = os.path.join(settings.ESTORIA_BASE_LOCATION,
                                          request.session['project'],
                                          'transcriptions',
                                          'translationXML')
    return _upload_and_process_xml(request, translation_xml, transcription_location,
                                   'estoria_app/translation.html',
                                   'Translation')


def cpsf_critical(request):
    """
    cpsf_critical page, deals with file upload and allows the user to spawn off the update task
    """
    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

    transcription_location = os.path.join(settings.ESTORIA_BASE_LOCATION,
                                          request.session['project'],
                                          'transcriptions',
                                          'criticalXML')
    return _upload_and_process_xml(request, cpsf_critical_xml, transcription_location,
                                   'estoria_app/cpsf_critical.html',
                                   'CPSF Critical')


def apparatus(request):
    """
    baking - allows the user to select either a chapter to bake or a range of chapters
    """
    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

    message = ''
    form = RangeForm()
    if request.session['project'] == 'estoria-digital':
        data_path = settings.ESTORIA_DATA_PATH
    elif request.session['project'] == 'cpsf-digital':
        data_path = settings.CPSF_DATA_PATH
    with open(os.path.join(data_path, 'collations.json'), encoding='utf-8') as fp:
        data = json.load(fp, object_pairs_hook=collections.OrderedDict)
    maximum_chapter = int(next(reversed(data)))

    if 'job' in request.GET:
        """
        If we have a GET request and 'job' in the request then we show the user the status of the job
        """
        task_id = request.GET['job']
        task = AsyncResult(task_id)
        context = {'result': task.result,
                   'state': task.state,
                   'task_id': task_id,
                   'current_project': request.session['project'],
                   'title': 'Baking Chapters'}
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
            url = request.build_absolute_uri() + '/' + request.session['project']
            if request.session['project'] == 'estoria-digital':
                data_path = settings.ESTORIA_DATA_PATH
            elif request.session['project'] == 'cpsf-digital':
                data_path = settings.CPSF_DATA_PATH
            task = bake_chapters.delay(start, stop, url, data_path)

            return HttpResponseRedirect('?job={}'.format(task.id))
        else:
            message = 'There was a problem with the supplied chapters to bake!'
            form = RangeForm(request.POST)

    return render(request,
                  'estoria_app/app_list.html',
                  {'form': form,
                   'data': data,
                   'message': message,
                   'current_project': request.session['project']}
                   )


def chapter(request, project=None, chapter=None):

    if not project:
        if 'project' not in request.session:
            return HttpResponseRedirect(reverse('index'))
        else:
            project = request.session['project']

    data = {'chapter': chapter,
            'current_project': project}
    if project == 'estoria-digital':
        data['collations_path'] = os.path.join(settings.ESTORIA_EDITION_LOCATION,
                                               'collation', 'approved')
        data['edition_url'] = settings.ESTORIA_EDITION_LOCATION
    elif project == 'cpsf-digital':
        data['collations_path'] = os.path.join(settings.CPSF_EDITION_LOCATION,
                                               'collation', 'approved')
        data['edition_url'] = settings.CPSF_EDITION_LOCATION

    return render(request, 'estoria_app/chapter_check.html', data)


def sentence(request, context):

    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

    data = {'context': context,
            'current_project': request.session['project']}
    if request.session['project'] == 'estoria-digital':
        data['collations_path'] = os.path.join(settings.ESTORIA_EDITION_LOCATION, 'collation', 'approved')
        data['edition_url'] = settings.ESTORIA_EDITION_LOCATION
    elif request.session['project'] == 'cpsf-digital':
        data['collations_path'] = os.path.join(settings.CPSF_EDITION_LOCATION, 'collation', 'approved')
        data['edition_url'] = settings.CPSF_EDITION_LOCATION
    return render(request, 'estoria_app/sentence_check.html', data)


def critical(request):
    """
    critical edition page
    """

    if 'project' not in request.session:
        return HttpResponseRedirect(reverse('index'))

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
        if os.path.exists(os.path.join(settings.ESTORIA_BASE_LOCATION,
                                       request.session['project'],
                                       'collation',
                                       'approved')):
            scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, request.session['project'], 'edition/src/assets/scripts')
            if request.session['project'] == 'estoria-digital':
                data_path = settings.ESTORIA_DATA_PATH
            elif request.session['project'] == 'cpsf-digital':
                data_path = settings.CPSF_DATA_PATH

            task = critical_edition_first.delay(data_path, scripts_path)
            return HttpResponseRedirect('?job={}'.format(task.id))
        else:
            message = 'There is a problem. The collation does not appear to exist.'

    return render(request, 'estoria_app/critical.html', {'message': message, 'current_project': request.session['project']})
