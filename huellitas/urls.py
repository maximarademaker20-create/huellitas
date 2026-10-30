from django.urls import include, path

urlpatterns = [
    path('', include('usuarios.urls')),
    path('', include('veterinaria.urls')),
]
