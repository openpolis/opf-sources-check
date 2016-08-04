from django.core.management.base import BaseCommand, CommandError

from webapp.models import Content

class Command(BaseCommand):
  help = 'List all contents in the DB ID, title and verification status'

  def handle(self, **options):
    for content in Content.objectsall():
      print("{0.id} - \"{0.title}\" ({0.verification_status})".format(content))
