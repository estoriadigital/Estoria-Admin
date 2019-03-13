# Django Project for Estoria de Espanna Digital Edition
This project consists of two apps:
  * [estoria_app](estoria_app): This app allows for easier management of various sections of the Estoria website.
    * Transcriptions: Upload new versions of the transcription files and rebuild the website from the files.
    * ReaderXML: Upload new versions of the reader XML file and rebuild the website from the file.
    * Baking: Take the javascript on-the-fly rendered pages from the live website and save them as static html files.
    * Critical Edition: Update the critical edition files.
  * [xmlconversion_app](xmlconversion_app): This app is to provide a simplified version of the XML conversion process, so that a user can find out how their XML will appear when run through the conversion scripts. For this, the user uploads an input XML file, which is split up and converted into chapter json files. These chapter json files are then combined with both standard and home written javascript, css, and font packages. The results is then returned to the user in a zip file for the user to download.

The python requirements are in [requirements.txt](requirements.txt). Both apps make use of Celery and this means that a suitable [Celery broker](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html) must be available (and configured in the settings file). The estoria_app also makes use of [Selenium](https://www.seleniumhq.org/) for the Baking task, to load the rendered webpages before they are saved as static files, and this, in turn requires a suitable webdriver (testing used [geckodriver](https://github.com/mozilla/geckodriver) v0.19.1).

There is an example [settings.py file](djangoproject/settings.py.in). This will need copying and editing before use. In this file, these will need pointing to appropriate paths:
  * SCRIPTS_LOCATION: location of the python script files that are used to process the XML files to produce the static files for the Estoria website.
  * RESOURCES_LOCATION: location of the extra resources that are included as part of the zip file produced by xmlconversion_app.
  * OUTPUT_LOCATION: location where the zip file output of the xmlconversion_app is stored. If necessary, create this directory and make sure that is writeable by Django.
  * ESTORIA_LOCATION: location of the live, static Estoria web pages.
  * BAKING_WEBPAGES_BASEURL: the url to get the live edition pages from during the baking process.

The apps are setup to use the existing management scripts, which means that these must exist or the tasks will fail - they are not supplied through this repository. Also, the main website files are not in this repository.

To run the tests:
  * manage.py test -v 2

To run the tests and check code coverage, with html code coverage output:
  * coverage run --source=. manage.py test -v 2; coverage html

The Django project was written by Simon Branford, with code review by Andrew Edmondson - both of [The Research Software Group, University of Birmingham](https://www.birmingham.ac.uk/bear-software). Some parts of [the resources in the xmlconversion_app](xmlconversion_app/resources) were  written by Zeth Green and Cat Smith. Licensing information for the original code is in [license](license).