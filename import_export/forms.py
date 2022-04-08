import os.path

from django import forms
from django.contrib.admin.helpers import ActionForm
from django.utils.translation import gettext_lazy as _


class ImportForm(forms.Form):
    import_file = forms.FileField(
        label=_('File to import')
        )
    input_format = forms.ChoiceField(
        label=_('Format'),
        choices=(),
        )

    def __init__(self, import_formats, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for i, f in enumerate(import_formats):
            choices.append((str(i), f().get_title(),))
        if len(import_formats) > 1:
            choices.insert(0, ('', '---'))

        self.fields['input_format'].choices = choices


class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    original_file_name = forms.CharField(widget=forms.HiddenInput())
    input_format = forms.CharField(widget=forms.HiddenInput())

    def clean_import_file_name(self):
        data = self.cleaned_data['import_file_name']
        data = os.path.basename(data)
        return data


class ExportForm(forms.Form):
    is_streaming_export = forms.BooleanField(label=_("Large datasets export"), required=False)
    file_format = forms.ChoiceField(
        label=_('Format'),
        choices=(),
        )

    def __init__(self, formats, streaming_formats, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for i, f in enumerate(formats):
            choices.append((str(i), f().get_title(),))
        if len(formats) > 1:
            choices.insert(0, ('', '---'))
            
        self.formats = formats
        self.streaming_formats = streaming_formats
        self.fields['file_format'].choices = choices 
        
        print(self.streaming_formats)
        
    def clean(self):
        cleaned_data = super().clean()
        is_streaming_export = cleaned_data.get("is_streaming_export", False)
        select_format = self.formats[int(cleaned_data["file_format"])]
        
        if is_streaming_export and select_format not in self.streaming_formats:
            self.add_error(
                "is_streaming_export", 
                _("{} extension does not support exporting large datasets.").format(
                    select_format().get_extension()
                ))
 
        return cleaned_data

def export_action_form_factory(formats):
    """
    Returns an ActionForm subclass containing a ChoiceField populated with
    the given formats.
    """
    class _ExportActionForm(ActionForm):
        """
        Action form with export format ChoiceField.
        """
        file_format = forms.ChoiceField(
            label=_('Format'), choices=formats, required=False)
    _ExportActionForm.__name__ = str('ExportActionForm')

    return _ExportActionForm
