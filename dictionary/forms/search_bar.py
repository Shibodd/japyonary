from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div
from crispy_forms.bootstrap import StrictButton

class SearchBarForm(forms.Form):
  query = forms.CharField(required=False)
  lang = forms.ChoiceField(choices=[('en', 'English'), ('ja', 'Japanese')], required=True)

  helper = FormHelper()
  helper.form_show_labels = False
  helper.form_id = 'dictionary-search-bar-form'
  helper.form_method = 'get'
  helper.layout = Layout(
      Div(
        Field('lang', template='dictionary/field_nomargin.html'),
        Field('query', placeholder='Enter kanji, kana, romaji or english', wrapper_class='flex-grow-1 mb-0', template='dictionary/field_nomargin.html'),
        StrictButton('<i class="bi bi-search"></i>', type="submit", css_class="btn"),
        css_class='d-flex m-0 p-0'
      )
    )