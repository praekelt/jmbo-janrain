import re

from django.core.urlresolvers import reverse
from django.conf import settings

from preferences import preferences

from foundry.models import Member
from janrain.models import JanrainProfile
from janrain.models import STATUS_DIRTY, STATUS_SYNCED


# Pre-compute URL reversals since they can't change during Django process
PATHS = (reverse('complete-profile'), reverse('edit-profile'))


class JanrainMiddleware:

    def process_request(self, request):
        if request.META['PATH_INFO'] in PATHS:
            user = getattr(request, 'user', None)
            if (user is not None) and user.is_authenticated():
                # Possible error in JanrainProfile model. User is a foreign key
                # and not a one-to-one.
                janrain_profile = user.janrainprofile_set.all()[0]
                if request.META['REQUEST_METHOD'] == 'POST':
                    janrain_profile.status = STATUS_DIRTY
                    print 'status set to dirty'
                    janrain_profile.save()
                if request.META['REQUEST_METHOD'] == 'GET':
                    janrain_profile.status = STATUS_DIRTY
                    print 'Will sync now'
                    # TODO: update profile from Janrain data.
                    janrain_profile.status = STATUS_SYNCED
                    janrain_profile.save()
