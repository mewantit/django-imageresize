from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('views',
    url(r'^(?P<file_name_without_extension>[^.]+)\.(?P<width>\d+)x(?P<height>\d+)(?P<file_extension>(\.\w+)?)$', views.resize_image),
)

