from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def mxit_combine(context, *args):
    combination = ''
    for arg in args:
        try:
            template_variable = template.Variable(arg)
            actual_arg = template_variable.resolve(context)
        except template.VariableDoesNotExist:
            actual_arg = arg
        combination += actual_arg

    return combination


@register.inclusion_tag('inclusion_tags/mxit_title_bar.html')
def mxit_title_bar(foreground_color, background_color, text):

    return {'foreground_color': foreground_color, 'background_color': background_color, 'text': text}
