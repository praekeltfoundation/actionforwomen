from django import template

register = template.Library()


@register.inclusion_tag('inclusion_tags/mxit_title_bar.html')
def mxit_title_bar(foreground_color, background_color, text):

    return {'foreground_color': foreground_color, 'background_color': background_color, 'text': text}
