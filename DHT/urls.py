from django.urls import path
from . import views, api

urlpatterns = [
    path("api/data/", api.Dlist, name='json'),
    path('index/', views.table, name='table'),
    path('api/data/myChart/', views.graphique, name='myChart'),
    path('api/data/chart-data/', views.chart_data, name='chart-data'),
    path('api/data/chart-data-jour/', views.chart_data_jour, name='chart-data-jour'),
    path('api/data/chart-data-semaine/', views.chart_data_semaine, name='chart-data-semaine'),
    path('api/data/chart-data-mois/', views.chart_data_mois, name='chart-data-mois'),
   path('api/data/download-pdf/', views.download_pdf, name='download_pdf'),

    path('', views.index_view, name='home'),
]
