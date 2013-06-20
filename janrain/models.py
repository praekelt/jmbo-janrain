from datetime import datetime
import requests

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
from foundry.models import Member

# Get imports and errors right for json/simplejson
try:
    import simplejson as json
except ImportError:
    import json

try:
    JSONDecodeError = json.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError

# Janrain client id and secret
JANRAIN_URL = settings.JANRAIN_URL

STATUS_SYNCED = 1
STATUS_DIRTY = 2
STATUS_CONFLICT = 4

base_payload = {'client_id': settings.JANRAIN_CLIENT_ID,
           'client_secret': settings.JANRAIN_CLIENT_SECRET,
           'type_name': 'user',
           }

# Mapping user and profile fields to Janrain equivalents. Each tuple is in the
# form (jmbo_name, janrain_name).
field_mappings = (
    ('first_name', 'givenName'),
    ('last_name', 'familyName'),
    ('email', 'email'),
    ('username', 'displayName'),
    )

# TODO: Provide a way for the field mappings to be overridden from settings.py

def map_user_to_janrain(user):
    """
    Given a user object, provide a dictionary of mapped fields and values to
    give to Janrain to update the user.
    """
    maps = {x[0]:x[1] for x in field_mappings}
    attributes = {}
    user_fields = ('first_name', 'last_name', 'username', 'email')

    for field in user_fields:
        value = getattr(user, field, None)
        if value:
            attributes[maps[field]] = value

    return attributes

#TODO: This is for reference only. Remove.
"""
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'))
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

from prefs:
last_login
date_joined
image
date_taken
view_count
crop_from
effect
facebook_id
twitter_username
address
city
zipcode
province
dob
gender
about_me
mobile_number
receive_sms
receive_email
country
is_profile_complete
    """

@receiver(user_logged_in)
def on_user_logged_in(sender, **kwargs):
    """
    Receiver for when the user logs in. It's placed here on recommendation of
    the Django docs.
    """
    print 'user logged in'
    user = kwargs['user']

    # Get or create the user's Janrain profile
    janrain_profile, created = JanrainProfile.objects.get_or_create(user=user)

    if not janrain_profile:
        janrain_profile = JanrainProfile(user=user)

    # TODO: The following parts may be slow, since the calls are synchronous.
    # Consider queueing.

    # Try to find a user on Janrain to tie to our own user.
    # If no corresponding Janrain user exists, create one.
    # TODO: For now, we don't try to tie these up. We just create a user if we
    # don't have a uuid.
    payload = base_payload.copy()
    if janrain_profile.janrain_uuid:
        # Just update the last logged in time on Janrain. TODO
        pass
    else:
        # Create a Janrain user.
        user_attributes = map_user_to_janrain(user)
        payload ['attributes'] = json.dumps(user_attributes)
        response = requests.post("%s/entity.create" % JANRAIN_URL, data=payload)
        # TODO: Handle response codes other than 200
        struct = json.loads(response.content)
        if struct['stat'] == 'ok':
            janrain_profile.janrain_uuid = struct['uuid']

    janrain_profile.save()    
    # Populate the profile of the logged-in user, if possible.

@receiver(post_save, sender=Member)
def on_user_profile_saved(sender, **kwargs):
    """
    Receiver for when the user profile is saved. Push to Janrain.
    """

    # On initial profile save during registration, just return.
    janrain_profiles = JanrainProfile.objects.filter(user=kwargs['instance'])
    if len(janrain_profiles) == 0:
        print 'Initial profile save'
        return

    janrain_profile = janrain_profiles[0]
    
    # The dirty status is set on profile form save. This prevents spurious
    # overwrites and allows us to retrigger an update if this fails.
    if janrain_profile.status == STATUS_DIRTY:
        payload = base_payload.copy()
        payload['uuid'] = janrain_profile.janrain_uuid
        user_attributes = map_user_to_janrain(janrain_profile.user)
        payload['value'] = json.dumps(user_attributes)
        response = requests.post("%s/entity.update" % JANRAIN_URL, data=payload)
        # TODO: Handle response codes other than 200
        struct = json.loads(response.content)
        if struct['stat'] == 'ok':
            janrain_profile.status = STATUS_SYNCED
            janrain_profile.last_synced = datetime.now()
            #TODO: last synced time set
            janrain_profile.save()


class JanrainProfile(models.Model):

    user = models.ForeignKey(
        User, 
        unique=True,
    )
    
    janrain_uuid = models.CharField(
        max_length=128,
        blank=True, 
        null=True,
    )

    last_synced = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )

    # Status indicator. Might be refactored to flags.
    status = models.PositiveIntegerField(
        default=0, 
    )

    def __unicode__(self):
        return self.user.username
    
