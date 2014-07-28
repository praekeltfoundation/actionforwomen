from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from mama.sites.vlive.yw_forms import PMLYourStoryForm
from jmboyourwords.models import YourStoryEntry, YourStoryCompetition


class PMLYourStoryView(FormView):
    form_class = PMLYourStoryForm
    template_name = 'yourwords/your_story.html'

    def get_context_data(self, **kwargs):
        context = super(PMLYourStoryView, self).get_context_data(**kwargs)
        competition = get_object_or_404(
            YourStoryCompetition, pk=self.kwargs['competition_id'])
        context['competition'] = competition
        context['competition_id'] = competition.id
        return context

    def get_initial(self):
        initial = super(PMLYourStoryView, self).get_initial()
        initial['next'] = reverse('moms_stories_object_list')
        user = self.request.user
        initial['name'] = user.username
        initial['competition_id'] = self.kwargs['competition_id']

        if not user.is_anonymous and user.email:
            initial['email'] = user.email
        else:
            initial['email'] = 'unspecified@askmama.mobi'
        return initial

    def form_valid(self, form):
        competition = get_object_or_404(
            YourStoryCompetition,
            pk=int(form.cleaned_data['competition_id']))
        YourStoryEntry.objects.create(
            your_story_competition=competition,
            user=self.request.user,
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            text=form.cleaned_data['text'],
            terms=True
        )
        return super(PMLYourStoryView, self).form_valid(form)

    def get_success_url(self):
        return reverse('moms_stories_object_list')
