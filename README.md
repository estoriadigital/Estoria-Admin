Django Project for Estoria de Espanna Digital Edition
----

This project consists of two apps:
  * [estoria_app](estoria_app): This app allows for easier management of various sections of the Estoria website and the CPSF website.
    * Transcriptions: Upload new versions of the transcription files and rebuild the website from the files.
    * ReaderXML: Upload new versions of the reader XML file and rebuild the website from the file.
    * Translation: Upload a new translation file and rebuild the website from the file (CPSF only).
    * CPSF critical: Upload a new cpsf critical XML file and rebuild the website from the file (CPSF only).
    * Critical Edition: Update the preparation files for the critical edition.
    * Baking: Rebuild the critical edition files from the collations created in the collation editor. For this to work the collation data must have been sym linked to the appropriate data directory as described in the edition repositories.
  * [xmlconversion_app](xmlconversion_app): This app is to provide a simplified version of the XML conversion process, so that a user can find out how their XML will appear when run through the conversion scripts. For this, the user uploads an input XML file, which is split up and converted into chapter json files which are then combined into a single html file. Thesefiles are then combined with both standard and home written javascript, css, and font packages. The results is then returned to the user in a zip file for the user to download.

The python requirements are in [requirements.txt](requirements.txt). Both apps make use of Celery and this means that a suitable [Celery broker](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html) must be available (and configured in the settings file). The estoria_app also makes use of [Selenium](https://www.seleniumhq.org/) for the Baking task, to load the rendered webpages before they are saved as static files, and this, in turn requires a suitable webdriver (testing used [geckodriver](https://github.com/mozilla/geckodriver) v0.30.0).

There is an example [settings.py file](djangoproject/settings.py.in). This will need copying and editing before use. In this file, these will need pointing to appropriate paths:
  * RESOURCES_LOCATION: location of the extra resources that are included as part of the zip file produced by xmlconversion_app.
  * OUTPUT_LOCATION: location where the zip file output of the xmlconversion_app is stored. If necessary, create this directory and make sure that is writeable by Django.
  * ESTORIA_DATA_PATH: The full path to the location of the data directory (including the data directory) in the served version of the estoria edition.
  * CPSF_DATA_PATH: The full path to the location of the data directory (including the data directory) in the served version of the cpsf edition.
  * ESTORIA_BASE_LOCATION:
  * VIRTUAL_ENV_PATH: path to the virtual environment for these tools
  * ESTORIA_EDITION_LOCATION: The URL for the estoria edition
  * CPSF_EDITION_LOCATION: The URL for the cpsf edition
  * ADMIN_TOOLS_LOCATION: The URL for these admin tools


The apps are setup to use the existing management scripts, which means that these must exist or the tasks will fail - they are not supplied through this repository. Also, the main website files are not in this repository.

All tasks in this app are sensitive to file ownership. Most things in this app, the edition serving locations and data location for the edition repositories must be owned by the user running nginx. On ubuntu this is www-data.

To run the tests:
  * manage.py test -v 2

To run the tests and check code coverage, with html code coverage output:
  * coverage run --source=. manage.py test -v 2; coverage html

The Django project was written by Simon Branford, with code review by Andrew Edmondson - both of [The Research Software Group, University of Birmingham](https://www.birmingham.ac.uk/bear-software). Some parts of [the resources in the xmlconversion_app](xmlconversion_app/resources) were written by Zeth Green and Catherine Smith. Licensing information for the original code is in [license](license).

It was revised and updated to Django 3.2 by Catherine Smith in March 2022.
Major changes in the revision are:

* the estoria_app now works with either the estoria edition or the cpsf edition
* the 'baking' process is now only available through the django app rather than using its own web service
* the xmlconversion app produces a html page containing all pages of the transcripton as browser security features no longer allow json to be loaded via local files

To reference the code in Estoria Admin, please use the following: [![DOI](https://zenodo.org/badge/175478994.svg)](https://zenodo.org/badge/latestdoi/175478994)
