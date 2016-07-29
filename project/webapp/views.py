import difflib
from django.shortcuts import render_to_response
from webapp.models import *

def diff(request, content_id):
    """
    generates a diff view, using difflib.HtmlDiff() method
    on live and stored html content
    
    each view means a request to the URI
    """
    content = Content.objects.get(pk=content_id)
    live = content.get_live_meat().splitlines(1)
    stored = content.meat.splitlines(1)
    diff = difflib.HtmlDiff().make_table(stored, live, context=True, numlines=2)    
    return render_to_response("diff.html", { 'content': content, 'diff': diff } )