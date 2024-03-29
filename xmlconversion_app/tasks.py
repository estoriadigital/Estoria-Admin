from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
from django.conf import settings

import os
import shutil
import re
import logging
import subprocess
import tempfile
import json

logger = logging.getLogger(__name__)


@shared_task
def xmlconversion(xml_filename, tempdir):
    """
    xml processing script
    """
    scripts_path = os.path.join(settings.ESTORIA_BASE_LOCATION, 'estoria-digital/edition/src/assets/scripts')
    # TODO consider hard coded paths in here and if any should be variables or constants
    logger.info('{}: xmlconversion task started'.format(current_task.request.id))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, scripts_path))
    logger.debug('{}: Resources location: {}'.format(current_task.request.id, settings.RESOURCES_LOCATION))
    logger.debug('{}: Output location: {}'.format(current_task.request.id, settings.OUTPUT_LOCATION))
    logger.debug('{}: Temporary directory: {}'.format(current_task.request.id, tempdir))

    try:
        logger.debug('{}: create directory structure'.format(current_task.request.id))
        os.makedirs(os.path.join(tempdir, 'transcriptions/manuscripts'))
        os.makedirs(os.path.join(tempdir, 'edition/static/data'))
        os.makedirs(os.path.join(tempdir, 'edition/src/assets/scripts'))
        os.makedirs(os.path.join(tempdir, 'output/static'))

        logger.debug('{}: add XML'.format(current_task.request.id))
        shutil.move(os.path.join(tempdir, xml_filename), os.path.join(tempdir, 'transcriptions/manuscripts/'))

        logger.debug('{}: copy over scripts'.format(current_task.request.id))

        shutil.copy(os.path.join(scripts_path, 'make_paginated_json.py'),
                    os.path.join(tempdir, 'edition/src/assets/scripts/'))
        shutil.copy(os.path.join(scripts_path, 'add_html_to_paginated_json.py'),
                    os.path.join(tempdir, 'edition/src/assets/scripts/'))
        logger.debug('{}: run make_paginated_json.py'.format(current_task.request.id))
        python_path = os.path.join(settings.VIRTUAL_ENV_PATH, 'bin', 'python3')
        subprocess.check_output([python_path, 'make_paginated_json.py', '-d', os.path.join(tempdir, 'edition/static/data')], cwd=os.path.join(tempdir, 'edition/src/assets/scripts/'), stderr=subprocess.STDOUT)

        logger.debug('{}: run add_html_to_paginated_json.py'.format(current_task.request.id))
        subprocess.check_call([python_path, 'add_html_to_paginated_json.py', '-d', os.path.join(tempdir, 'edition/static/data')], cwd=os.path.join(tempdir, 'edition/src/assets/scripts/'))

        logger.debug('{}: move edition/transcription/[dirname] to output/json'.format(current_task.request.id))
        dirname = xml_filename.replace('.xml', '')
        shutil.copytree(os.path.join(tempdir, 'edition/static/data/transcription/', dirname), os.path.join(tempdir, 'output/json'))

        logger.debug('{}: copy in the js/css/font packages to output'.format(current_task.request.id))
        shutil.copytree(os.path.join(settings.RESOURCES_LOCATION, 'deps'), os.path.join(tempdir, 'output/static/deps'))
        shutil.copy(os.path.join(settings.RESOURCES_LOCATION, 'estoria.js'), os.path.join(tempdir, 'output/static/'))
        shutil.copy(os.path.join(settings.RESOURCES_LOCATION, 'estoria.css'), os.path.join(tempdir, 'output/static/'))

        logger.debug('{}: build html from generated json files'.format(current_task.request.id))
        menu = json.loads(open(os.path.join(tempdir, 'edition/static/data/menu_data.js')).read().replace('MENU_DATA = ', ''))
        index_string = open(os.path.join(settings.RESOURCES_LOCATION, 'index.html')).read()

        abbreviated_list = []
        expanded_list = []
        for file in menu[dirname]:
            data = json.loads(open(os.path.join(tempdir, 'output/json', '{}.json'.format(file))).read());
            abbreviated_list.append('<div class="panel-body" id="abbr-{}"><span class="page">{}</span>'.format(data['name'], data['name']))
            abbreviated_list.append(data['html_abbrev'])
            abbreviated_list.append('</div>')

            expanded_list.append('<div class="panel-body" id="abbr-{}"><span class="page">{}</span>'.format(data['name'], data['name']))
            expanded_list.append(data['html'])
            expanded_list.append('</div>')

        index_string = index_string.replace('%SGLM%', dirname)
        index_string = index_string.replace('%ABBRVTD%', ''.join(abbreviated_list))
        index_string = index_string.replace('%EXPNDD%', ''.join(expanded_list))
        with open(os.path.join(tempdir, 'output/index.html'), 'w') as outfile:
            outfile.write(index_string)

        logger.debug('{}: zip up the result and copy to output location'.format(current_task.request.id))
        zipname = re.sub('^' + tempfile.gettempdir() + '/', '', tempdir)
        shutil.make_archive(os.path.join(settings.OUTPUT_LOCATION, zipname), 'zip', os.path.join(tempdir, 'output/'))
    finally:
        logger.debug('{}: delete the unneeded tmp folder'.format(current_task.request.id))
        shutil.rmtree(tempdir)

    logger.info('{}: complete, so return the zip filename {}'.format(current_task.request.id, zipname))
    return '{0}.zip'.format(zipname)
