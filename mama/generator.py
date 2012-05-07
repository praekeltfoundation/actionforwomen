def generate():
    objects = []
    for i in range(1, 30):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "Article %s Title" % i,
                "content": "Article %s Content" % i,
                "state": "published",
                "sites": [1,],
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": "Articles",
                        "slug": "articles",
                    },
                },],
            },
        })
        if (i % 5 == 0):
            objects[-1]['fields']['categories'] += [{
                "model": "category.Category",
                "fields": {
                    "title": "Featured",
                    "slug": "featured",
                },
            },]

    for i in range(1, 30):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "Moms Stories %s Title" % i,
                "content": "Moms Stories %s Content" % i,
                "state": "published",
                "sites": [1,],
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": "Moms Stories",
                        "slug": "moms-stories",
                    },
                },],
            },
        })
        if (i % 5 == 0):
            objects[-1]['fields']['categories'] += [{
                "model": "category.Category",
                "fields": {
                    "title": "Featured",
                    "slug": "featured",
                },
            },]

    return objects
