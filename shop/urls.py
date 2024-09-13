from django.contrib import admin
from django.urls import path, include
from .views import ManagerProductsAddView, ManagerProductsUpdateView, OrderConfirmationView, PaymentView, ProductListView, ProductDetailView, SignUp, CustomLoginView, CustomLogoutView, CartDetailView, AddToCartView, RemoveToCartView, OrderCreateView, AddAlertView, ManagerDashboardView, ManagerOrdersView, ManagerProductsView, ManagerOrdersUpdateView, ManagerProductsDeleteView, UserOrdersView
from .views import gmail_mail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', ProductListView.as_view(), name="product_list"),
    path('category/<slug:category_slug>', ProductListView.as_view(), name="product_list_by_category"),
    path('product/<slug:slug>', ProductDetailView.as_view(), name="product_detail"),

    path('signup/', SignUp.as_view(), name = "signup"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('cart/', CartDetailView.as_view(), name='cart'),
    path('cart/add/<slug:slug>', AddToCartView.as_view(), name='cart_add'),
    path('cart/remove/<slug:slug>', RemoveToCartView.as_view(), name='cart_remove'),

    path('order/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),

    path('alert/add/<slug:slug>', AddAlertView.as_view(), name='make_alert'),
    
    path('manager/', ManagerDashboardView.as_view(), name='manager_dashboard'),

    path('manager/orders/', ManagerOrdersView.as_view(), name='manager_orders'),
    path('manager/order/<int:pk>', ManagerOrdersUpdateView.as_view(), name='update_order'),

    path('manager/products/', ManagerProductsView.as_view(), name='manager_products'),
    path('manager/product/<slug:slug>', ManagerProductsUpdateView.as_view(), name='update_product'),
    path('manager/product/add/', ManagerProductsAddView.as_view(), name='add_product'),
    path('manager/product/delete/<slug:slug>', ManagerProductsDeleteView.as_view(), name='delete_product'),

    path('payment/<int:order_id>', PaymentView.as_view(), name = 'payment'),

    path('my-orders/', UserOrdersView.as_view(), name='user_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)