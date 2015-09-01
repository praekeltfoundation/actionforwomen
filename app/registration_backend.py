from userprofile.backends.simple import SimpleBackend


class MamaBackend(SimpleBackend):

    def register(self, request, **kwargs):
        """
        Create and immediately log in a new user.

        This is a customization of normal userprofile
        backend to remove email field.
        """
        data = request.POST.dict()
        kwargs['email'] = data['username']
        return super(MamaBackend, self).register(request, **kwargs)

    def post_registration_redirect(self, request, user):
        profile = user.profile
        data = request.POST.dict()
        if not profile.alias:
            profile.alias = data['alias']
            profile.gender = data['gender']
            profile.year_of_birth = data['year_of_birth'] if data['year_of_birth'].isdigit() else None
            profile.identity = data['identity']
            profile.save()

        return ('registration_done', (), {})
