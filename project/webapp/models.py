# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import re

import html2text
import requests
import lxml.html


@python_2_unicode_compatible
class OrganisationType(models.Model):
    """the type of source, describes the kind of organisation the content is
    about"""

    name = models.CharField(
        max_length=250,
        verbose_name=_("Denominazione"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'tipo di organizzazione'
        verbose_name_plural = 'tipi di organizzazione'

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

    title = models.CharField(
        max_length=250,
        verbose_name=_("Denominazione della fonte"),
        help_text="""usare la sequenza IT - Nome, dove: I-Istituzione
                     [C|G], T-tipo[R|P|C], Nome (es. CR - Lazio)"""
    )
    organisation_type = models.ForeignKey(
        OrganisationType,
        verbose_name=_("Tipo di organizzazione")
    )
    url = models.URLField()
    xpath = models.CharField(blank=True, max_length=250)
    regexp = models.CharField(
        blank=True, null=True, max_length=250,
        verbose_name=_("Espressione regolare")
    )
    content = models.TextField(
        blank=True, null=True,
        verbose_name=_("Contenuto significativo")
    )
    notes = models.TextField(
        blank=True, null=True,
        verbose_name=_("Note")
    )
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

    class Meta:
        verbose_name = 'contenuto'
        verbose_name_plural = 'contenuti'

    def __str__(self):
        return self.title


    def get_live_content(self):
        """
        requests content from URI, using XPATH,

        :return: 2-tuple
          cleanest possible textual content, or error message,
          along with response status code
          when xpath failes status code is 900
        """

        res = requests.get(self.url)
        if res.status_code != 200:
            return (res.status_code, "URL")

        parser = lxml.html.HTMLParser(remove_comments=True)
        tree = lxml.html.fromstring(res.content, parser=parser)

        # extract html_element using content.xpath
        html_elements = tree.xpath(self.xpath)
        if (len(html_elements)):
            html_element = html_elements[0]
        else:
            return (900, "XPATH")

        # transform it into a string, extracting text content
        p = re.compile(self.regexp)
        content = p.sub('', html_element.text_content())

        html2text.UNICODE_SNOB = 1
        return (200, html2text.html2text(content))

    def verify(self, dryrun=False):
        """verifies that live content is different from content in DB"""
        (resp_code, resp_content) = self.get_live_content()

        if resp_code != 200:
            self.verification_status = Content.STATUS_ERROR
            self.verification_error = "ERRORE {0} ({1})".format(
                resp_code, resp_content
            )
        else:
            resp_content = resp_content.\
                replace("\n", " ").replace("\t", " ").\
                replace(chr(160), " ").\
                strip(" ")

            if self.content:
                stored_content = self.content.\
                    replace("\n", " ").replace("\t", " ").\
                    replace(chr(160), " ").\
                    strip(" ")
            else:
                stored_content = ''

            if  (resp_content != stored_content):
                self.verification_status = self.STATUS_CHANGED
            else:
                self.verification_status = self.STATUS_NOT_CHANGED

            self.verification_error = None

        self.verified_at = timezone.now()
        if dryrun == False:
            self.save()

        return self.verification_status

    def update(self):
        """updates db with live content; align verification status"""
        (resp_code, resp_content) = self.get_live_content()

        if resp_code != 200:
            self.verification_status = Content.STATUS_ERROR
            self.verification_error = "ERRORE {0} ({1})".format(
                resp_code, resp_content
            )
        else:
            resp_content = resp_content. \
                replace("\n", " ").replace("\t", " "). \
                replace(chr(160), " "). \
                strip(" ")

        self.content = self.get_live_content()
        self.verification_status = self.STATUS_NOT_CHANGED
        self.verification_error = None
        self.verified_at = timezone.now()
        self.save()

    def get_inhabitants(self):
        """
        search number of inhabitants in api3.openpolis.it/locations
        the content's title is supposed to be:
        CC - ID - City name (PR) or CC - City name

        :return: number of inhabitants ad integer
        """
        m = re.match(r'^.*-\s*(.*?)\s*\((.*)\)\s*', self.title)
        if m is None:
            raise Exception("Incorrect title format: {0}".format(self.title))

        city_name = m.group(1).strip()
        api_url = "http://api3.openpolis.it/territori/locations.json" + \
                  "?loc_type=c&nameiexact={0}".format(city_name)
        res = requests.get(api_url)
        if res.status_code == 404:
            raise Exception("404 error while requesting @api3.openpolis.it")
        r = res.json()
        if r['count'] == 0:
            raise Exception(
                "City {0} not found @api3.openpolis.it".format(city_name))
        if r['count'] > 1:
            raise Exception("City {0} found more than once "
                            "@api3.openpolis.it".format(city_name))

        return r['results'][0]['inhabitants']


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
