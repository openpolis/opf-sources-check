import difflib
from django.shortcuts import render_to_response
from webapp.models import *

def diff(request, content_id):
    """
    generates a diff view, using difflib.HtmlDiff() method
    on live and stored html content

    each view means a request to the URI
    """
    obj = Content.objects.get(pk=content_id)
    (resp_code, resp_content) = obj.get_live_content()

    live = resp_content.splitlines(1)
    if obj.content:
        stored = obj.content.splitlines(1)
    else:
        stored = ''
    diff = difflib.HtmlDiff().make_table(stored, live, context=True, numlines=2)
    return render_to_response("diff.html", { 'content': obj, 'diff': diff } )
