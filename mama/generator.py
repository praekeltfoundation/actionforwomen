from mama import models
from category.models import Category
models.add_field(Category)

def gen_posts(category_title, category_slug, category_color, count):
    objects = []
    for i in range(1, count):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "%s Post %s Title" % (category_title, i),
                "description": "%s Post %s Description" % (category_title, i),
                "content": "%s Post %s Content" % (category_title, i),
                "state": "published",
                "sites": [1, ],
                "primary_category": {
                    "model": "category.Category",
                    "fields": {
                        "title": category_title,
                        "slug": category_slug,
                        "color": category_color,
                    },
                },
            },
        })
        if (i % 5 == 0):
            objects[-1]['fields']['categories'] = [{
                "model": "category.Category",
                "fields": {
                    "title": "Featured",
                    "slug": "featured",
                },
            }, ]
    return objects


def generate():
    objects = []

    objects += gen_posts('Articles', 'articles', 'purple', 20)
    objects += gen_posts('MAMA A-to-Z', 'mama-a-to-z', 'dorange', 20)
    objects += gen_posts('Life Guides', 'life-guides', 'yorange', 20)
    objects += gen_posts("Moms Stories", 'moms-stories', 'maroon', 20)

    objects.append({
        "model": "poll.Poll",
        "fields": {
            "title": "Poll 1 Title",
            "state": "published",
            "sites": [1, ],
            "categories": [{
                "model": "category.Category",
                "fields": {
                    "title": "Featured",
                    "slug": "featured",
                },
            }, ],
        },
    })

    return objects
