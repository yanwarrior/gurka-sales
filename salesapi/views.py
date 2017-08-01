from rest_framework import generics
from rest_framework.response import Response
from sales.models import Product, Order, OrderDetail
from .serializers import ProductSerializer, OrderSerializer


class ProductList(generics.ListCreateAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	# TODO: adding search Product !


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_field = 'sku'


class ProductDeleteBulk(generics.DestroyAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer

	def delete(self, *args, **kwargs):
		Product.objects.all().delete()
		return Response({})


class OrderList(generics.ListCreateAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer


class OrderDetail(generics.RetrieveAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	lookup_field = 'order_number'