from django import forms


class UploadFileForm(forms.Form):
    xmlfile = forms.FileField(label='Select a file')


class RangeForm(forms.Form):
    start_chapter = forms.IntegerField(label='Start at chapter', min_value=1)
    stop_chapter = forms.IntegerField(label='Stop at chapter', min_value=1)
