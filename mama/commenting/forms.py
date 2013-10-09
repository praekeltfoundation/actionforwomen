import re

from django import forms
from preferences import preferences
from django.contrib.comments.forms import CommentForm

class MamaCommentForm(CommentForm):
    def clean_comment(self):
        super(MamaCommentForm, self).clean_comment()

        """
        Check for banned patterns and silence sensitive patterns.
        """
        comment = self.cleaned_data['comment']

        # Check for banned patterns.
        banned_patterns = preferences.SitePreferences.comment_banned_patterns
        if banned_patterns:
            for pattern in banned_patterns.split('\n'):
                pattern = pattern.replace('\r', '').replace('*', "\*").replace('.', "\.")
                match = re.search(pattern.lower(), comment.lower())
                if match:
                    raise forms.ValidationError("Please don't post inappropriate content(%s). "
                                                "Your action has been noted." % match.group())

        # Silence sensative patterns.
        silenced_patterns = preferences.SitePreferences.comment_silenced_patterns
        if silenced_patterns:
            for pattern in silenced_patterns.split('\n'):
                pattern = pattern.replace('\r', '')
                comment = re.sub(
                    pattern,
                    lambda x: '*' * len(x.group()),
                    comment,
                    flags=re.DOTALL
                )
                comment = re.sub(
                    pattern.lower(),
                    lambda x: '*' * len(x.group()),
                    comment,
                    flags=re.DOTALL
                )

        return comment
