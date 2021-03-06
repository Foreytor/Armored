from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from tasks.views import *
from finance.views import *

urlpatterns = [
    path("", UserAccountsList.as_view(), name='accountsList'),
    path("<int:pk>/", TranslationDetals.as_view(), name='translationDetals'),
    path("starttranslation/", StartTranslation.as_view(), name='starttranslation'),
    path("translationlistuser/", TranslationListUser.as_view(),
         name='translationlistuser'),
    path("searchlist/", SearchList.as_view(), name='searchlist'),
    path("accountList/", AccountList.as_view(), name='accountList'),
    path("accountsdetals/<int:pk>/",
         AccountsDetals.as_view(), name='accountsdetals'),
]


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
