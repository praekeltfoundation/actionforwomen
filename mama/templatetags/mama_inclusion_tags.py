from category.models import Category
from django import template
from jmbo.models import ModelBase

register = template.Library()
    
@register.inclusion_tag('mama/inclusion_tags/ages_and_stages.html', takes_context=True)
def ages_and_stages(context):
    return context
    
@register.inclusion_tag('mama/inclusion_tags/home_category_block_listing.html')
def home_category_block_listing(slug):
    category = Category.objects.get(slug__exact=slug)
    object_list = ModelBase.permitted.filter(categories__slug=category.slug).filter(categories__slug='featured')

    return {
        'category': category,
        'object_list': object_list,
    }

@register.inclusion_tag('mama/inclusion_tags/home_category_content_listing.html')
def home_category_content_listing(slug):
    category = Category.objects.get(slug__exact=slug)
    object_list = ModelBase.permitted.filter(categories__slug=category.slug).filter(categories__slug='featured')

    return {
        'category': category,
        'object_list': object_list,
    }

@register.inclusion_tag('mama/inclusion_tags/home_subcategory_listing.html')
def home_subcategory_listing(category_slug):
    category = Category.objects.get(slug__exact=category_slug)
    return {
        'category': category,
        'object_list': category.children,
    }
