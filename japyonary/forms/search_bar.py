from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from crispy_forms.bootstrap import StrictButton

class SearchBarForm(forms.Form):
  query = forms.CharField(required=False)

  def __init__(self, placeholder, mode_choices=None, mode_field_name='mode', form_id='search_bar_form', method='get', *args, **kwargs):
    super().__init__(*args, **kwargs)

    if mode_choices and mode_field_name:
      self.mode_field_name = mode_field_name
      self.fields[self.mode_field_name] = forms.ChoiceField(choices=mode_choices, required=True)
    else:
      self.mode_field_name = None

    self.helper = FormHelper()
    self.helper.form_show_labels = False
    self.helper.form_id = form_id
    self.helper.form_method = method

    layout_fields = []
    if self.mode_field_name:
      layout_fields.append(Field(self.mode_field_name, template='japyonary/field_nomargin.html'))

    layout_fields.append(Field('query', placeholder=placeholder, wrapper_class='flex-grow-1 mb-0', template='japyonary/field_nomargin.html'))
    layout_fields.append(StrictButton('<i class="bi bi-search"></i>', type="submit", css_class="btn"))

    self.helper.layout = Layout(Div(*layout_fields, css_class='d-flex m-0 p-0'))  