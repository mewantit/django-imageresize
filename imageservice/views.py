from django.http import HttpResponse, Http404
import imagemagick
from django.conf import settings

def resize_image(request, file_name_without_extension, width, height, file_extension):
    width = int(width)
    height = int(height)
    
    if height > settings.RESIZE_MAX_HEIGHT or width > settings.RESIZE_MAX_WIDTH:
        raise Http404
    
    source_file = "%s/%s%s" % (settings.MEDIA_ROOT, file_name_without_extension, file_extension)
    target_file = "%s/%s.%dx%d%s" % (settings.MEDIA_CACHE_ROOT, file_name_without_extension, width, height, file_extension)   
    
    try:
        imagemagick.resize(source_file, target_file, width, height)    
    except Exception, e:
        raise Http404(e)
        
    return render_image_to_response(target_file)

# Needed to be able to mock built in open function
def _open(file_name):
    return open(file_name, 'rb')

def render_image_to_response(image_file_name):
    img = _open(image_file_name).read()
    return HttpResponse(img, mimetype='image/%s' % image_file_name.split(".")[-1])