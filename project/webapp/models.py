# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import re
from os import sys

from model_utils import Choices

import html2text
import requests
import lxml.html
from lxml import etree


@python_2_unicode_compatible
class Content(models.Model):
    """a content on the web, identified by the URL and the XPATH expression"""

    STATUS_NOT_CHANGED = 0
    STATUS_CHANGED = 1
    STATUS_ERROR = 2
    STATUS_CHOICES = (
        (STATUS_CHANGED, 'modificato'),
        (STATUS_NOT_CHANGED, 'invariato'),
        (STATUS_ERROR, 'contiene errori')
    )
    TODO = (
        ('yes', 'Yes'),
        ('no', 'No')
    )

    title = models.CharField(
        max_length=250,
        verbose_name=_("Denominazione della fonte"),
        help_text="""usare la sequenza IT - Nome, dove: I-Istituzione
                     [C|G], T-tipo[R|P|C], Nome (es. CR - Lazio)"""
    )
    url = models.URLField()
    xpath = models.CharField(blank=True, max_length=250)
    regexp = models.CharField(blank=True, null=True, max_length=250,
                              verbose_name=_("Espressione regolare"))
    meat = models.TextField(blank=True, null=True, verbose_name=_("Contenuto significativo"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Note"))
    verified_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Timestamp")
    )
    verification_status = models.IntegerField(
        null=True,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_CHANGED,
        verbose_name=_("Stato")
    )
    verification_error = models.CharField(
        blank=True, null=True, max_length=250,
        verbose_name=_("Errore")
    )
    todo = models.CharField(max_length=3, choices=TODO, null=True, blank=True)

    class Meta:
        verbose_name = 'contenuto'
        verbose_name_plural = 'contenuti'

    def __str__(self):
        return self.title


    def get_live_meat(self):
        """
        requests content from URI, using XPATH, returns cleanest possible textual content
        """
        res = requests.get(self.url)
        parser = lxml.html.HTMLParser(remove_comments=True)
        tree = lxml.html.fromstring(res.content, parser=parser)

        # extract html_element using content.xpath
        html_elements = tree.xpath(self.xpath)
        if (len(html_elements)):
            html_element = html_elements[0]
        else:
            raise NameError('xpath non trova niente: %s' % self.xpath)

        # transform it into a string, extracting text content
        p = re.compile(self.regexp)
        content = p.sub('', html_element.text_content())

        html2text.UNICODE_SNOB = 1
        return html2text.html2text(content)


    def verify(self, dryrun=False):
        """verifies that live content is different from content in DB"""
        live = self.get_live_meat().\
            replace("\n", " ").replace("\t", " ").\
            replace(chr(160), " ").\
            strip(" ")
        stored = self.meat.\
            replace("\n", " ").replace("\t", " ").\
            replace(chr(160), " ").\
            strip(" ")
        if  (live != stored):
            self.verification_status = self.STATUS_CHANGED
        else:
            self.verification_status = self.STATUS_NOT_CHANGED
        self.verified_at = timezone.now()

        if dryrun == False:
            self.save()
        return self.verification_status



    def update(self):
        """updates db with live content; align verification status"""
        self.meat = self.get_live_meat()
        self.verification_status = self.STATUS_NOT_CHANGED
        self.verification_error = None
        self.verified_at = None
        self.save()




@python_2_unicode_compatible
class Recipient(models.Model):
    """a recipient of notifications about changes on web contents"""

    name = models.CharField(
        blank=True, max_length=100,
        verbose_name='Nome')
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'destinatario'
        verbose_name_plural = 'destinatari'


    def __str__(self):
        return self.name
