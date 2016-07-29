from django.core.management.base import BaseCommand, CommandError

from webapp.models import Content

class Command(BaseCommand):
  help = 'List all contents in the DB that are marked as todo, printing out ID, title and verification status'
  
  def handle(self, **options):
    for content in Content.objects.filter(todo='yes'):
      print("{0.id} - \"{0.title}\" ({0.verification_status})".format(content))
