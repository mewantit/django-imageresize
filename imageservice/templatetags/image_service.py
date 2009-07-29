from django import template
from django.template.defaultfilters import stringfilter
register = template.Library() 
@register.filter
@stringfilter
def resize(url, size):
    (path, slash, file_ending) = url.rpartition("/")
    (url_without_file_ending, delim, file_ending) = file_ending.rpartition(".")
    if url_without_file_ending == "":
        url_without_file_ending, file_ending = file_ending, ""
    return path + slash + url_without_file_ending + "." + size + delim + file_ending