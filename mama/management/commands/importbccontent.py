import os
from xml.dom.minidom import parse

from category.models import Category
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from mama.models import Link
from post.models import Post


class Command(BaseCommand):
    help = 'Imports raw Baby Center content.'

    def handle(self, *args, **options):
        links = {}

        bc_category, created = Category.objects.get_or_create(title="BC Content", slug="bc-content")
        pregnancy_category, created = Category.objects.get_or_create(title="My Pregnancy", slug="my-pregnancy")
        mama_category, created = Category.objects.get_or_create(title="MAMA A-to-Z", slug="mama-a-to-z")
        site = Site.objects.get_current()

        path = os.path.split(os.path.abspath(__file__))[0]
        pages = parse(os.path.join(path, 'raw_bc_content.txt')).childNodes[0]

        print "Creating posts..."
        for node in pages.getElementsByTagName('page'):
            categories = [bc_category, mama_category]
            pk = 6000 + int(node.getElementsByTagName('uid')[0].firstChild.data)
            title = node.getElementsByTagName('title')[0].firstChild.data
            content = node.getElementsByTagName('body')[0].toxml().lstrip('<body>').rstrip('</body>')
                
            prenatal = node.getElementsByTagName('prenatal')
            if prenatal:
                prenatal = prenatal[0].firstChild.data
                categories.append(Category.objects.get_or_create(title="Prenatal Week %s" % prenatal, slug="prenatal-week-%s" % prenatal)[0])
                
            postnatal = node.getElementsByTagName('postnatal')
            if postnatal:
                postnatal = prenatal[0].firstChild.data
                categories.append(Category.objects.get_or_create(title="Postnatal Week %s" % postnatal, slug="postnatal-week-%s" % postnatal)[0])
                   
            for link in node.getElementsByTagName('link'):
                if pk not in links:
                    links[pk] = []
                links[pk].append((6000 + int(link.attributes['uid'].value), link.firstChild.data))


            post, created = Post.objects.get_or_create(pk=pk)
            if created:
                post.title = title
                post.description = content[:100]
                post.content = content
                post.state = 'published'
                post.sites.add(site)
                post.primary_category = pregnancy_category
                post.comments_enabled = False
                post.anonymous_comments = False
                post.comments_closed = True
                for category in categories:
                    post.categories.add(category)
                post.save()
                print "Imported %s" % post

        print "Creating post links..."
        for source, targets in links.items():
            for target in targets:
                
                link, created = Link.objects.get_or_create(
                    source_id=source,
                    target_id=target[0],
                    title=target[1]
                )
                if created:
                    print "Created link %s" % link

        print "Done!"
