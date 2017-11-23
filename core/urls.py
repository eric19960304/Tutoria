from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^home/$', views.homepage, name='homepage'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^search/$', views.searchTutor, name='search_tutor'),
    url(r'^booktutor/(?P<tutor_id>[0-9]+)$', views.bookTutor, name='book_tutor'),
    url(r'^message/$', views.message, name='message'),
    url(r'^timetable/$', views.viewTimetable, name='view_timetable'),
    url(r'^wallet/$', views.viewWallet, name='view_wallet'),
    url(r'^notification/$', views.notification, name='view_notification'),
    url(r'^tutorprofile/(?P<tutor_id>[0-9]+)$', views.viewTutorProfile, name='view_tutor_profile'),
    url(r'^reviewtutor/(?P<url_token>\w+)/$', views.reviewTutor, name="review_tutor"),
    url(r'^profile/$', views.editProfile, name='edit_profile'),
    url(r'^topup/$', views.addToWallet, name='add_to_wallet'),
    url(r'^withdraw/$', views.drawFromWallet, name='draw_from_wallet'),
    url(r'^adminwithdraw/$', views.adminDrawFromWallet, name='admin_draw_from_wallet'),

    url(r'^adminwallet/$', views.adminWallet, name='admin_wallet'),
    url(r'^password/$', views.changePassword, name='change_password'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

]