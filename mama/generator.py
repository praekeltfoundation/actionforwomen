def gen_subcat_content(parent, children):
    objects = []
    for child in children:
        i = 1
        for j in range(i, i + 10):
            objects.append({
                "model": "post.Post",
                "fields": {
                    "title": "%s %s Title" % (child[0], j - i + 1),
                    "content": "%s %s Content" % (child[0], j - i + 1),
                    "state": "published",
                    "sites": [1,],
                    "categories": [{
                        "model": "category.Category",
                        "fields": {
                            "title": child[0],
                            "slug": child[1],
                            "parent": {
                                "model": "category.Category",
                                "fields": {
                                    "title": parent[0],
                                    "slug": parent[1],
                                },
                            },
                        },
                    },],
                },
            })
        i += 10
    return objects


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
  

    objects += gen_subcat_content(('BC Content', 'bc-content'), [('HIV', 'hiv'), ('Labour & Birth', 'labour-birth'), ('Pregnancy', 'pregnancy')])
    objects += gen_subcat_content(('MAMA SA', 'mama-sa'), [('Planning your family', 'planning-your-family'), ('Single parenting', 'single-parenting'), ('The good dad guide', 'the-good-dad-guide')])
   
    """
    for i in range(1, 30):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "MAMA SA %s Title" % i,
                "content": "MAMA SA %s Content" % i,
                "state": "published",
                "sites": [1,],
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": "MAMA SA",
                        "slug": "mama-sa",
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
    """

    return objects
