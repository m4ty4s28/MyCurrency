from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backbase_app.urls')),
]

admin.site.site_header = "My Currency"
admin.site.site_title = "Administration My Currency"
admin.site.index_title = "Welcome to Administrator My Currency"
