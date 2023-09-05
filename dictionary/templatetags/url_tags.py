from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_with_updated_query(context, **kwargs):
  query = context['request'].GET.copy()
  for k, v in kwargs.items():
    query[k] = v
  return query.urlencode()