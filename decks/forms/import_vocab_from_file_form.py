from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit
from crispy_forms.bootstrap import StrictButton
from django.urls import reverse_lazy

class ImportVocabFromFileForm(forms.Form):
  uploaded_vocabulary_file = forms.FileField()

  def __init__(self, deck_id, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.helper = FormHelper()
    self.helper.form_show_labels = False
    self.helper.form_id = 'import_vocabulary_from_file_form'
    self.helper.layout = Layout(Div(
      Submit('submit', 'Import from file', css_class="btn btn-primary"),
      Div(
        Field('uploaded_vocabulary_file', template='japyonary/field_nomargin.html'),
        css_class="px-3"
      ),
      css_class='d-flex'
    ))