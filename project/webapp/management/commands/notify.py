from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from webapp.models import Content, Recipient

class Command(BaseCommand):
    help = 'Notify variations, if necessary, to all recipients'

    def add_arguments(self, parser):
        parser.add_argument('--dryrun',
                            action='store_true',
                            dest='dryrun',
                            default=False,
                            help='Execute a dry run: no db is written.'
                            )

    def handle(self, *args, **options):
        msg_txt = ""
        msg_html = ""

        modified_contents = Content.objects.filter(verification_status=Content.STATUS_CHANGED)
        failed_contents = Content.objects.filter(verification_status=Content.STATUS_ERROR)

        if modified_contents.count():
            msg_txt += "Cambiamenti:\n"
            msg_html += "Questo l'elenco dei siti cambiati: <br/><ul " \
                        "style=\"list-style-type:none\">"
            for content in modified_contents:
                msg_txt += " - {0.title}\n".format(content)
                msg_html += """
                  <li>
                    <a href="http://verificafonti.openpolis.it/sitescheck/content/{0.id}">
                        {0.title}
                    </a>
                    (<a href="http://verificasiti.openpolis.it/diff/{0.id})">diff</a>)
                  </li>
                """.format(content)
            msg_html += "</ul>"

        if failed_contents.count():
            msg_txt += "Errori:\n"
            msg_html += "Questo l'elenco dei siti con errori: <br/><ul style=\"list-style-type:none\">"
            for content in failed_contents:
                msg_txt += " - {0.title}\n".format(content)
                msg_html += """
                  <li><a href="{0.url}">{0.title}</a></li>
                """.format(content)
            msg_html += "</ul>"

        if msg_txt != '':
            recipients = []
            for recipient in Recipient.objects.all():
                recipients.append(recipient.email)
            print("recipients: " + "; ".join(recipients))

            if  options['dryrun'] != True:
                try:
                    subject = '[Openpolis] Cambiamento nei siti sotto controllo!'
                    msg = EmailMultiAlternatives(subject, msg_txt, settings.DEFAULT_FROM_EMAIL, recipients)
                    msg.attach_alternative(msg_html, "text/html")
                    msg.send()
                    print("ok")
                except:
                    print("error sending email")
            else:
                print("will not send a bit; it's a dry run!")
        else:
            print("No changes detected!")
