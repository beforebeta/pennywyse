# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def render_response(template_file, request, context={}):
    my_context = context
    return render_to_response(template_file, my_context, context_instance=RequestContext(request))

def index(request):
    return render_response("index.html", request)