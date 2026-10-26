from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Inicio de sesión (usa el sistema de usuarios de Django, con contraseñas cifradas)
    path('login/', auth_views.LoginView.as_view(template_name='veterinaria/login.html',
                                                redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.inicio, name='inicio'),

    # Mascotas
    path('mascotas/', views.mascotas, name='mascotas'),
    path('mascotas/nueva/', views.mascota_form, name='nueva_mascota'),
    path('mascotas/<int:pk>/', views.ficha, name='ficha'),
    path('mascotas/<int:pk>/editar/', views.mascota_form, name='editar_mascota'),
    path('mascotas/<int:pk>/baja/', views.dar_baja, name='dar_baja'),
    path('mascotas/<int:pk>/reactivar/', views.reactivar, name='reactivar'),
    path('mascotas/<int:pk>/consulta/', views.nueva_consulta, name='nueva_consulta'),
    path('mascotas/<int:pk>/vacuna/', views.registrar_vacuna, name='registrar_vacuna'),

    # Dueños
    path('duenos/', views.duenos, name='duenos'),
    path('duenos/nuevo/', views.dueno_form, name='nuevo_dueno'),
    path('duenos/<int:pk>/editar/', views.dueno_form, name='editar_dueno'),

    # Turnos y recordatorios
    path('turnos/', views.turnos, name='turnos'),
    path('turnos/<int:pk>/cancelar/', views.cancelar_turno, name='cancelar_turno'),
    path('turnos/<int:pk>/atender/', views.atender_turno, name='atender_turno'),
    path('turnos/<int:pk>/whatsapp/', views.recordar_turno, name='recordar_turno'),
    path('vacunas/<int:pk>/whatsapp/', views.recordar_vacuna, name='recordar_vacuna'),

    # Especies y razas
    path('especies/', views.especies, name='especies'),
]
