from category.models import Category
from django import template
from jmbo.models import ModelBase

register = template.Library()
    
    
@register.inclusion_tag('mama/inclusion_tags/category_featured_listing.html')
def category_featured_listing(slug):
    category = Category.objects.get(slug__exact=slug)
    object_list = ModelBase.objects.filter(categories__slug=category.slug).filter(categories__slug='featured')

    return {
        'category': category,
        'object_list': object_list,
    }
