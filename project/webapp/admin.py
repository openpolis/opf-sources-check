from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_admin_row_actions import AdminRowActionsMixin
from django_object_actions import DjangoObjectActions
from django.utils import timezone

from .models import Content, Recipient, OrganisationType


class ContentAdmin(DjangoObjectActions, AdminRowActionsMixin, admin.ModelAdmin):
    list_display = ('_linked_title',
                    'verified_at',
                    '_status_and_message')
    search_fields = ('title', 'notes')
    list_filter = ('verification_status', 'organisation_type')
    fieldsets = (
        (None, {
            'fields': ('title', 'organisation_type', 'notes', 'url', 'xpath',
                       'regexp', 'content'),
            'classes': ['wide', 'extrapretty']
        }),
        ('Verification', {
            'fields': ('verified_at', 'verification_status', 'verification_error')
        })
    )
    readonly_fields = (
    'content', 'verified_at', 'verification_status', 'verification_error')

    def _linked_title(self, obj):
        return '%s <a href="%s" target="_blank"><img ' \
               'src="/static/images/extlink.gif" alt="vai" title="vai alla ' \
               'url: %s"</a>' % (
        obj.title, obj.url, obj.url)

    _linked_title.allow_tags = True
    _linked_title.short_description = 'Identificativo della URL'

    def _status_and_message(self, obj):
        status = obj.verification_status
        if obj.verification_status == 0:
            msg = "IMMUTATO"
        elif obj.verification_status == 1:
            msg = 'CAMBIATO - <a href="/diff/%s" target="_blank"><img ' \
                  'src="/static/images/extlink.gif" alt="vai"/> ' \
                  'visualizza ' \
                  'le differenze</a>' % obj.id
        else:
            msg = obj.verification_error

        return ("%s - %s" % (status, msg))

    _status_and_message.allow_tags = True
    _status_and_message.short_description = 'Status'

    def update(self, request, queryset):
        for obj in queryset:
            obj.update()

    update.short_description = "Aggiorna contenuto dai siti live"

    def verify(self, request, queryset):
        for obj in queryset:
            obj.verify()

    verify.short_description = "Verifica differenze sui siti live"


    def change_view(self, request, object_id, form_url='', extra_context=None):

        # implement custom actions into change view
        if request.method == 'POST' and '_extra_action' in request.POST.keys():
            redirect = True
            content = self.get_object(request, object_id)
            if request.POST['_extra_action'] == 'Aggiorna':
                content.update()
            if request.POST['_extra_action'] == 'Verifica':
                verification_status = content.verify()
                if verification_status == Content.STATUS_ERROR:
                    redirect = False
                    msg = "{0} durante la verifica di {1} (id: {2})".format(
                        content.verification_error, content.title,
                        content.id
                    )
                    messages.add_message(request, messages.WARNING, msg)
                else:
                    msg = \
                        "{0} (id: {1}) - {2}".format(
                            content.title,
                            content.id,
                            content.get_verification_status_display().upper(),
                        )
                    messages.add_message(request, messages.SUCCESS, msg)

            # redirect to list or same page, based on above results
            # errors keep you in the current page,
            opts = self.model._meta
            preserved_filters = self.get_preserved_filters(request)
            if redirect:
                redirect_url = reverse('admin:%s_%s_changelist' %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
            else:
                redirect_url = request.path

            redirect_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, redirect_url
            )
            return HttpResponseRedirect(redirect_url)

        else:
            # normal courses of events
            return super(ContentAdmin, self).change_view(
                request, object_id, form_url, extra_context=extra_context,
            )

    actions = [update, verify,]


    def publish_this(self, request, obj):
        pass

    publish_this.label = "Publish"  # optional
    publish_this.short_description = "Submit this article to The Texas Tribune"

    change_actions = ('publish_this',)

    def get_row_actions(self, obj):
        row_actions = [
            {'label': 'Verifica', 'action': 'verify', 'enabled': False},

        ]
        row_actions += super(ContentAdmin, self).get_row_actions(obj)
        return row_actions

admin.site.register(Content, ContentAdmin)
admin.site.register(Recipient)
admin.site.register(OrganisationType)
