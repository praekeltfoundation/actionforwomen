import os
from xml.dom.minidom import parse

from category.models import Category
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from mama.models import Link
from post.models import Post
from django.template.defaultfilters import linebreaksbr


class Command(BaseCommand):
    help = 'Hotfix script to correct BC content linebreaks.'

    def handle(self, *args, **options):
        print "This is a hotfix script to correct BC content linebreaks. You should not have to use it."
        import pdb; pdb.set_trace()
        path = os.path.split(os.path.abspath(__file__))[0]
        pages = parse(os.path.join(path, 'raw_bc_content.txt')).childNodes[0]

        print "Creating posts..."
        for node in pages.getElementsByTagName('page'):
            pk = 6000 + int(node.getElementsByTagName('uid')[0].firstChild.data)
            post = Post.objects.get(pk=pk)
            content = linebreaksbr(node.getElementsByTagName('body')[0].toxml().lstrip('<body>').rstrip('</body>'))
            post.content = content
            post.save()
            print 'Corrected "%s" linebreaks' % post

        print "Done!"
