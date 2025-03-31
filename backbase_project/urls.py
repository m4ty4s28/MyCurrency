from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(("backbase_app.urls", 'v1'), namespace='v1')),

]

admin.site.site_header = "My Currency"
admin.site.site_title = "Administration My Currency"
admin.site.index_title = "Welcome to Administrator My Currency"
