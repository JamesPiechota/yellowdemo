from django.conf.urls import patterns, include, url
import demo.views

urlpatterns = patterns('',
    url(r'^$', demo.views.create)
)