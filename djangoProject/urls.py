from django.contrib import admin
from django.urls import path
from AutoCar.views import LoginView, LogoutUserView, RegisterView, AddCarView, AddChangeView, RefuelView, ReplenishView, BaseView, \
    ReportView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('main/', BaseView.as_view(), name='base'),
    path('register/', RegisterView.as_view(), name='register'),
    path('add_car/', AddCarView.as_view(), name='add_car'),
    path('user/<int:car_id>/', AddCarView.as_view(), name='car_details'),
    path('add_change/', AddChangeView.as_view(), name='add_change'),
    path('refuel/', RefuelView.as_view(), name='refuel'),
    path('replenish/', ReplenishView.as_view(), name='replenish'),
    path('car_details/', ReportView.as_view(), name='report'),
    path('logout/', LogoutUserView.as_view(), name='logout')
]
