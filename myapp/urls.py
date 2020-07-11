from django.urls import path, include # for defined path template to conect with url

from myapp.views import (
    BasePage,
)# with out import views can't show templates html page

urlpatterns = [
    #path('', Apartments.as_view(), name='apartments'),
    path('parus/', BasePage.as_view(), name='indx'),
    #path('repg/', GestReportByReseption.as_view(), name='app-rep-g'),
    #path('repm/', MigrateReportByReseption.as_view(), name='app-rep-m'),
    #path('repmc/', MigrateCompanyReportByReseption.as_view(), name='app-rep-m-c'),
    #path('cntrrep/', MigrateCountryReportByReseption.as_view(), name='cntr-rep'),
]