from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from backend import views as backend_views
from backup import views as backup_views


urlpatterns = [
    url(r'^uams/', include('authen.urls')),
    url(r'^$',  RedirectView.as_view(url="/admin")),
    url(r'^admin/', admin.site.urls),

    url(r'^backend/lock$', backend_views.account_lock),
    url(r'^backend/unlock$', backend_views.account_unlock),
    url(r'^backup/count_valid_strategy$', backup_views.count_valid_strategy),
    url(r'^backup/recovery$', backup_views.recovery),
    url(r'^backup/recovery_check$', backup_views.recovery_check),
]
