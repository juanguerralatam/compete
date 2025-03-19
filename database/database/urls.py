from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

# Import all views from various apps
from basic_info.views import (
    BasicInfoListView, 
    BasicInfoDetailView,
    Show
)
from operations.views import (
    OperationsListView,
    OperationsDetailView,
    operations_dashboard,
    get_last_comment
)
from products.views import (
    ProductsListView,
    ProductsDetailView,
    products_dashboard
)
from ads.views import (
    AdsListView,
    AdsDetailView,
    ads_dashboard
)
from deparment_mkt.views import DepartmentMktListView, DepartmentMktDetailView, Show
from deparment_rd.views import DepartmentRDListView, DepartmentRDDetailView, Show

from comment.views import CommentListView, CommentDetailView, get_last_comment

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Basic Info Endpoints
    path('basic_info/', BasicInfoListView.as_view(), name='basic-info-list'),
    path('basic_info/<int:pk>/', BasicInfoDetailView.as_view(), name='basic-info-detail'),
    
    # Operations Endpoints
    path('operations/', OperationsListView.as_view(), name='operations-list'),
    path('operations/<int:pk>/', OperationsDetailView.as_view(), name='operations-detail'),
    path('operations/dashboard/', operations_dashboard, name='operations-dashboard'),
    
    # Products Endpoints  
    path('products/', ProductsListView.as_view(), name='products-list'),
    path('products/<int:pk>/', ProductsDetailView.as_view(), name='products-detail'),
    path('products/dashboard/', products_dashboard, name='products-dashboard'),
    
    # Ads Endpoints
    path('ads/', AdsListView.as_view(), name='ads-list'),
    path('ads/<int:pk>/', AdsDetailView.as_view(), name='ads-detail'),
    
    # Comment Endpoints
    path('comment/', CommentListView.as_view(), name='comment-list'),
    path('comment/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comment/last/', get_last_comment, name='comment-last'),
    
    # Redirect root to admin
    path('', RedirectView.as_view(url='admin/'), name='root-redirect'),
]