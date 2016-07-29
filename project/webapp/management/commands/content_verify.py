from optparse import make_option
import difflib
import datetime
import sys

from django.core.management.base import BaseCommand, CommandError

from webapp.models import Content

class Command(BaseCommand):
  args = '<id> <id>'
  help = 'Verify specified content'

  option_list = BaseCommand.option_list + (
    make_option('--dryrun',
        action='store_true',
        dest='dryrun',
        default=False,
        help='Execute a dry run: no db is written.'),
    make_option('--meat',
        action='store_true',
        dest='showmeat',
        default=False,
        help='Show extracted text'),
    make_option('--diff',
        action='store_true',
        dest='showdiff',
        default=False,
        help='Show diff code.'),
    make_option('--offset',
        action='store',
        type='int',
        dest='offset',
        default=0,
        help='Force offset <> 0'),
    make_option('--limit',
        action='store',
        type='int',
        dest='limit',
        default=0,
        help='Force offset <> 0'),
  )
      
  
  def handle(self, *args, **options):
    offset = options['offset']
    limit = options['limit']
    
    if len(args) == 0:
      if (limit > 0):
        contents = Content.objects.filter(todo='yes')[offset:(offset+limit)]
      else:
        contents = Content.objects.filter(todo='yes')[offset:]
    else:
      contents = Content.objects.filter(id__in=args)
    
    if (len(contents) == 0):
      print("no content to check this time")
     
    for cnt, content in enumerate(contents):
      err_msg = ''
      try:
        verification_status = content.verify(options['dryrun'])
      except IOError:
        err_msg = "Errore: Url non leggibile: %s" % (content.url)
      except Exception as e:
        err_msg = "Errore sconosciuto: %s" % (e)
      finally:
        if err_msg != '':
          if options['dryrun'] == False:
            content.verification_status = Content.STATUS_ERROR
            content.verification_error = err_msg
            content.verified_at = datetime.datetime.now()
            content.save()
          print ("{0}/{1} - {2} while processing {3} (id: {4})".format(
              cnt+1, len(contents), err_msg, content.title, content.id
          ))
        else:
          print (
              "{0}/{1} - {2} is {3} (id: {4})".format(
                  cnt+1, len(contents), content.title,
                  verification_status, content.id
             )
          )
          if options['showmeat'] == True:
            print ("Meaningful content: %s") % content.get_live_meat()
          if options['showdiff'] == True:
            live = content.get_live_meat().splitlines(1)
            stored = content.meat.splitlines(1)
            diff = difflib.ndiff(live, stored)
            print ("".join(diff))
        
    
  

