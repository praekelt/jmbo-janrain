import re

from django.core.urlresolvers import reverse
from django.conf import settings

from preferences import preferences

from foundry.models import Member
from janrain.models import JanrainProfile
from janrain.models import STATUS_DIRTY, STATUS_SYNCED

class JanrainMiddleware:

    def process_request(self, request):
        if request.META['PATH_INFO'] in [reverse('complete-profile'),
        reverse('edit-profile')]:
            username = request.META['AUTHENTICATED_USER']
            user = Member.objects.get(username=username)
            janrain_profile = JanrainProfile.objects.get(user=user)
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
