from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit
from crispy_forms.bootstrap import StrictButton


class AddCommentForm(forms.Form):
  text = forms.CharField(widget=forms.Textarea(attrs={"rows": 7, "cols": 40}))

  helper = FormHelper()
  helper.form_show_labels = False
  helper.form_id = 'add_comment_form'

  helper.layout = Layout(Div(
    Field('text'),
    Submit('submit', 'Add comment', css_class="btn btn-primary")
  ))