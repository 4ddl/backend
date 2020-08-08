from django import forms


class UploadImageForms(forms.Form):
    file = forms.ImageField()


class ImageNameForms(forms.Form):
    title = forms.CharField(max_length=50)


class UploadFileForms(forms.Form):
    file = forms.FileField(allow_empty_file=False)


class RequestFileForm(forms.Form):
    title = forms.CharField(max_length=150)
