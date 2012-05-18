from category.models import Category
from post.models import Post

pregnancy_category = Category.objects.get(slug='my-pregnancy')
mama_category = Category.objects.get(slug='mama-a-to-z')

for post in Post.objects.filter(categories__slug='bc-content'):
    post.categories.remove(pregnancy_category)
    post.categories.remove(mama_category)
    if post.title.startswith('Month '):
        print "Pregnancy post %s" % post
        post.primary_category = pregnancy_category
    else:
        print "Mama post %s" % post
        post.primary_category = mama_category

    post.save()
