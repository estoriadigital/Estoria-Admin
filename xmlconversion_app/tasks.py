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


def replace_line(filename, linenum, text):
    """
    replace the specified line number with the supplied text
    this sorts out the menus, without having to deal with how the user has named the file
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines[linenum-1] = text
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)



@shared_task
def xmlconversion(xml_filename, tempdir):
    """
    xml processing script
    """
    # TODO consider hard coded paths in here and if any should be variables or constants
    logger.info('{}: xmlconversion task started'.format(current_task.request.id))
    logger.debug('{}: Scripts location: {}'.format(current_task.request.id, settings.SCRIPTS_LOCATION))
    logger.debug('{}: Resources location: {}'.format(current_task.request.id, settings.RESOURCES_LOCATION))
    logger.debug('{}: Output location: {}'.format(current_task.request.id, settings.OUTPUT_LOCATION))
    logger.debug('{}: Temporary directory: {}'.format(current_task.request.id, tempdir))

    try:
        logger.debug('{}: create directory structure'.format(current_task.request.id))
        os.makedirs(os.path.join(tempdir, 'transcriptions/manuscripts'))
        os.makedirs(os.path.join(tempdir, 'edition/static/data'))
        os.makedirs(os.path.join(tempdir, 'edition/scripts'))
        os.makedirs(os.path.join(tempdir, 'output/static'))

        logger.debug('{}: add XML'.format(current_task.request.id))
        shutil.move(os.path.join(tempdir, xml_filename), os.path.join(tempdir, 'transcriptions/manuscripts/'))

        logger.debug('{}: copy over scripts'.format(current_task.request.id))
        shutil.copy(os.path.join(settings.SCRIPTS_LOCATION, 'make_paginated_json.py'),
                    os.path.join(tempdir, 'edition/scripts/'))
        shutil.copy(os.path.join(settings.SCRIPTS_LOCATION, 'add_html_to_paginated_json.py'),
                    os.path.join(tempdir, 'edition/scripts/'))

        logger.debug('{}: run make_paginated_json.py'.format(current_task.request.id))
        subprocess.check_output([ 'python3', 'make_paginated_json.py'], cwd=os.path.join(tempdir, 'edition/scripts/'), stderr=subprocess.STDOUT)

        logger.debug('{}: run add_html_to_paginated_json.py'.format(current_task.request.id))
        subprocess.check_call(['python3', 'add_html_to_paginated_json.py'], cwd=os.path.join(tempdir, 'edition/scripts/'))

        logger.debug('{}: move edition/transcription/[dirname] to output/json'.format(current_task.request.id))
        dirname = xml_filename.replace('.xml', '')
        shutil.copytree(os.path.join(tempdir, 'edition/transcription/', dirname), os.path.join(tempdir, 'output/json'))


        # shutil.copytree(os.path.join(settings.ESTORIA_LOCATION, 'edition/dist/fonts'),
        #                 os.path.join(tempdir, 'output/static/fonts'))
        logger.debug(os.listdir(os.path.join(tempdir, 'output/static/')))
        shutil.copy(os.path.join(settings.RESOURCES_LOCATION, 'estoria.js'), os.path.join(tempdir, 'output/'))
        shutil.copy(os.path.join(settings.RESOURCES_LOCATION, 'estoria.css'), os.path.join(tempdir, 'output/'))

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



        index_string = index_string.replace('%ABBRVTD%', ''.join(abbreviated_list))
        index_string = index_string.replace('%EXPNDD%', ''.join(expanded_list))
        with open(os.path.join(tempdir, 'output/index.html'), 'w') as outfile:
            outfile.write(index_string)


        # logger.debug('{}: move edition/static/data/menu_data.js to '
        #              'output/static/js/data_menu.js and edit the second line'.format(current_task.request.id))
        # shutil.copy(os.path.join(tempdir, 'edition/static/data/menu_data.js'), os.path.join(tempdir, 'output/static/js/'))
        #
        # # This replaces the second line of the file with a standard line
        # # This means that the javascript in estoria.js will know how to access the menu data
        # replace_line(os.path.join(tempdir, 'output/static/js/menu_data.js'), 2, '    "json": [')

        logger.debug('{}: zip up the result and copy to output location'.format(current_task.request.id))
        zipname = re.sub('^' + tempfile.gettempdir() + '/', '', tempdir)
        shutil.make_archive(os.path.join(settings.OUTPUT_LOCATION, zipname), 'zip', os.path.join(tempdir, 'output/'))
    finally:
        logger.debug('{}: delete the unneeded tmp folder'.format(current_task.request.id))
        shutil.rmtree(tempdir)

    logger.info('{}: complete, so return the zip filename {}'.format(current_task.request.id, zipname))
    return '{0}.zip'.format(zipname)
