from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import generics
from .models import Products
from .serializers import ProductsSerializer

# List all products
class ProductsListView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

# View details of a specific product
class ProductsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

# Create a new product
class ProductsCreateView(CreateView):
    model = Products
    template_name = 'products/products_form.html'
    fields = ['name', 'price', 'cost', 'description']
    success_url = reverse_lazy('products:list')

# Update an existing product
class ProductsUpdateView(UpdateView):
    model = Products
    template_name = 'products/products_form.html'
    fields = ['name', 'price', 'cost', 'description']
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
