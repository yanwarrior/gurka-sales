from rest_framework import generics
from rest_framework.response import Response
from sales.models import Product, Order, OrderDetail
from .serializers import ProductSerializer, OrderSerializer


class ProductList(generics.ListCreateAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer

	def get_queryset(self):
		queryset = Product.objects.all()
		sku = self.request.query_params.get('sku', None)
		name = self.request.query_params.get('name', None)
		price_min = self.request.query_params.get('price_min', None)
		price_max = self.request.query_params.get('price_max', None)

		if sku:
			queryset = queryset.filter(sku=sku)

		if name:
			queryset = queryset.filter(name__contains=name)

		if price_min:
			queryset = queryset.filter(price__gte=int(price_min))

		if price_max:
			queryset = queryset.filter(price__lte=int(price_max))

		return queryset


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