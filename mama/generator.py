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
    

def gen_posts(category_title, category_slug, count):
    objects = []
    for i in range(1, count):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "%s Post %s Title" % (category_title, i),
                "content": "%s Post %s Content" % (category_title, i),
                "state": "published",
                "sites": [1,],
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": category_title,
                        "slug": category_slug,
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


def generate():
    objects = []

    objects += gen_posts('Articles', 'articles', 20)
    objects += gen_posts('Health', 'health', 20)
    objects += gen_posts('Lifestyle', 'lifestyle', 20)
    objects += gen_posts('Stories', 'stories', 20)
    
    objects.append({
        "model": "poll.Poll",
        "fields": {
            "title": "Poll 1 Title",
            "state": "published",
            "sites": [1,],
            "categories": [{
                "model": "category.Category",
                "fields": {
                    "title": "Featured",
                    "slug": "featured",
                },
            },],
        },
    })

    """
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
  
    for i in range(1, 20):
        objects.append({
            "model": "poll.Poll",
            "fields": {
                "title": "Poll %s Title" % i,
                "state": "published",
                "sites": [1,],
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": "Todays Poll",
                        "slug": "todays-poll",
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

    return objects
