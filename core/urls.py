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
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]