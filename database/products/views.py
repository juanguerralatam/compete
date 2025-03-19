from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from rest_framework import generics
from rest_framework.response import Response
from .models import Products
from .serializers import ProductsSerializer

class ProductsListView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

class ProductsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

def Show(request):
    try:
        # Get the products with all fields
        products = Products.objects.values("id", "name", "price", "cost", "description")
        
        data = {
            'products': list(products)
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    success_url = reverse_lazy('products:list')

# Delete a product
class ProductsDeleteView(DeleteView):
    model = Products
    template_name = 'products/products_confirm_delete.html'
    success_url = reverse_lazy('products:list')

# Function-based view for products dashboard
def products_dashboard(request):
    products = Products.objects.all()
    # Calculate product metrics
    total_products = products.count()
    avg_price = sum(product.price for product in products) / total_products if total_products > 0 else 0
    avg_margin = sum(product.price - product.cost for product in products) / total_products if total_products > 0 else 0
    
    context = {
        'products': products,
        'total_products': total_products,
        'avg_price': avg_price,
        'avg_margin': avg_margin,
    }
    return render(request, 'products/dashboard.html', context)
