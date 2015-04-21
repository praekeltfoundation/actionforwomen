from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from jmbo.view_modifiers import ViewModifier
from jmbo.view_modifiers.items import GetItem


class PopularItem(GetItem):
    def modify(self, queryset):
        sql = 'SELECT COUNT(*) from %s WHERE %s.object_pk=CAST(%s.%s as TEXT) AND %s.content_type_id=%s' % (
            Comment._meta.db_table,
            Comment._meta.db_table,
            queryset.model._meta.db_table,
            queryset.model._meta.pk.attname,
            Comment._meta.db_table,
            ContentType.objects.get_for_model(queryset.model).pk,
        )
        return queryset.extra(select={'extra_comment_count': sql}).order_by(\
                '-extra_comment_count', '-created')


class PopularViewModifier(ViewModifier):
    def __init__(self, request, base_url=None, *args, **kwargs):
        self.items = [
            PopularItem(
                request=request,
                title="Popular",
                get={'name': 'by', 'value': 'popular'},
                base_url=base_url,
                default=False,
            ),
        ]
        super(PopularViewModifier, self).__init__(request, *args, **kwargs)
