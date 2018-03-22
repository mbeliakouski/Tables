from django import forms


# class CsvFileField(forms.FileField):
#
#     def to_python(self, data):
#         print(data.name)
#         return super().to_python(data)


class UploadFileForm(forms.Form):
    
    file = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control-file',
            'accept': '.csv',
            
        }
    ),
        label='Select CSV file',

    )
