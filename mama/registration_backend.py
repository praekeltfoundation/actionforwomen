from userprofile.backends.simple import SimpleBackend
from mama.forms import RegistrationForm


class MamaBackend(SimpleBackend):

    def get_form_class(self, request):
        # Override this here to prevent a circular import between mama models
        # and forms.
        return RegistrationForm

    def register(self, request, **kwargs):
        """
        Create and immediately log in a new user.

        This is a customization of normal userprofile
        backend to remove email field.
        """
        kwargs['email'] = ''
        return super(MamaBackend, self).register(request, **kwargs)

    def post_registration_redirect(self, request, user):
        # Set alias from uername
        profile = user.profile
        if not profile.alias:
            profile.alias = user.username
            profile.save()

        return ('registration_done', (), {})
