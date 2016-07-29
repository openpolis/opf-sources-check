from django.core.management.base import BaseCommand, CommandError
from webapp.models import Content
import datetime


class Command(BaseCommand):
    help = """
        Get live content,
        from specified URI's ids, or from all URIs marked as TODO.
        Use to bulk-update sources.
    """

    def add_arguments(self, parser):
        parser.add_argument('id', nargs='*', type=int)

        parser.add_argument('--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Execute a dry run: no db is written.'
        )
        parser.add_argument('--html',
            action='store_true',
            dest='showhtml',
            default=False,
            help='Show html code.'
        )
        parser.add_argument('--offset',
            action='store',
            type=int,
            dest='offset',
            default=0,
            help='Force offset <> 0'
        )
        parser.add_argument('--limit',
            action='store',
            type=int,
            dest='limit',
            default=0,
            help='Force offset <> 0'
        )


    def handle(self, *args, **options):
        offset = options['offset']
        limit = options['limit']

        if len(args) == 0:
            if (limit > 0):
                contents = Content.objects.filter(todo='yes')[
                           offset:(offset + limit)]
            else:
                contents = Content.objects.filter(todo='yes')[offset:]
        else:
            contents = Content.objects.filter(id__in=args)

        if (len(contents) == 0):
            print("no content to get this time")

        for cnt, content in enumerate(contents):
            err_msg = ''
            try:
                content.update()
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
                    print("{0}/{1} - {2} while processing {3} (id: {4})".format(
                        cnt + 1, len(contents), err_msg, content.title, content.id
                    ))
                else:
                    print(
                        "{0}/{1} - {2} (id: {3}) - AGGIORNATO".format(
                            cnt + 1, len(contents), content.title,
                            content.id
                        )
                    )
                    if options['showhtml'] == True:
                        print("Meaningful content: %s") % content.get_live_meat()
                    if options['dryrun'] == False:
                        content.save()
