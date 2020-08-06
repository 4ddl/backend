from django import forms


class UploadImageForms(forms.Form):
    file = forms.ImageField()


class ImageNameForms(forms.Form):
    title = forms.CharField(max_length=50)
