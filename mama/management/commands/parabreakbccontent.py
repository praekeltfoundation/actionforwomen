import os
from xml.dom.minidom import parse

from django.core.management.base import BaseCommand
from django.template.defaultfilters import linebreaks


class Command(BaseCommand):
    help = 'Hotfix script to correct BC content paragraph breaks.'

    def handle(self, *args, **options):
        from post.models import Post
        print "This is a hotfix script to correct BC content paragraph breaks. You should not have to use it."
        import pdb; pdb.set_trace()
        path = os.path.split(os.path.abspath(__file__))[0]
        pages = parse(os.path.join(path, 'raw_bc_content.txt')).childNodes[0]

        print "Creating posts..."
        for node in pages.getElementsByTagName('page'):
            pk = 6000 + int(node.getElementsByTagName('uid')[0].firstChild.data)
            post = Post.objects.get(pk=pk)
            content = linebreaks(node.getElementsByTagName('body')[0].toxml().lstrip('<body>').rstrip('</body>').replace('\n<ul>\n', '<ul>').replace('</li>\n', '</li>').replace('\n', '\n\n')).replace('\n', '').replace('<p></p>', '')
            post.content = content
            post.save()
            print 'Corrected "%s" paragraph breaks' % post

        print "Done!"
