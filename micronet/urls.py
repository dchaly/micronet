from django.conf.urls import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^$', views.show, name='show'),
    url(r'show_script', views.get_script, name='show_script'),

    url(r'new_node', views.new_node, name='new_node'),
    url(r'new_connection', views.new_connection, name='new_connection'),

    url(r'delete_node', views.delete_node, name='delete_node'),
    url(r'delete_connection', views.delete_connection, name='delete_connection'),

    url(r'set_connection_info', views.set_connection_info, name='set_connection_info'),
    url(r'set_node_label', views.set_node_label, name='set_node_label'),

    url(r'get_script', views.get_script, name='get_script'),
]