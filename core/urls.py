from django.conf.urls import url
from django.contrib.auth import views as auth_views
from core import views
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^home/$', views.homepage, name='homepage'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^search/$', views.searchTutor, name='search_tutor'),
    url(r'^booktutor/(?P<tutor_id>[0-9]+)$', views.bookTutor, name='book_tutor'),
    url(r'^booksuccess/$', views.afterBooked, name='after_booked'),
    url(r'^timetable/$', views.viewTimetable, name='view_timetable'),
    url(r'^cancel/$', views.cancelSession, name='cancel_session'),
    url(r'^wallet/$', views.viewWallet, name='view_wallet'),
    url(r'^message/$', views.notification, name='view_notification'),
]