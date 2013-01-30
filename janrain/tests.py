import unittest

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase
from django.test.client import Client

from gallery import views
from gallery.models import Gallery, GalleryImage, VideoEmbed, VideoFile
from photologue.models import PhotoSize

