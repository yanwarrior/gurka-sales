from django.db.models import F
from django.db.models import Sum

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from sales.models import Product, Order, OrderDetail
from .serializers import (
	ProductSerializer, 
	OrderSerializer, 
	ReportStockMinimumSerializer,
	ReportSaleSerializer)

from rest_framework.pagination import PageNumberPagination


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


@api_view(['GET'])
def report_product_stock_min(request):
	# Please read: `How can I compare two fields of a model in a query?`
	# https://stackoverflow.com/a/7054290
	instance = Product.objects.filter(stock__lte=F('stock_min'))
	serializer = ReportStockMinimumSerializer(instance, many=True)
	return Response(serializer.data)





@api_view(['GET'])
def report_omzet(request):
	context = {'request': request}
	paginator = PageNumberPagination()
	paginator.page_size = 1

	start_date = request.query_params.get('start_date')
	end_date = request.query_params.get('end_date')
	if start_date and end_date:
		instance = Order.objects.filter(order_date__range=(start_date, end_date))
	else:
		instance = Order.objects.all()

	instance = paginator.paginate_queryset(instance, request)
	serializer_all = ReportSaleSerializer(instance, many=True)
	# serializer_one = CountTotalSerializer(instance)
	return Response(serializer_all.data)


class ReportProductStockMin(generics.ListAPIView):
	queryset = Order.objects.filter(stock__lte=F('stock_min'))
	serializer_class = ReportStockMinimumSerializer


class ReportOmzet(generics.ListAPIView):
	queryset = Order.objects.all()
	serializer_class = ReportSaleSerializer

	def filter_queryset(self, queryset):
		start_date = self.request.query_params.get('start_date')
		end_date = self.request.query_params.get('end_date')

		queryset = Order.objects.all()

		if start_date and end_date:
			queryset = Order.objects.filter(order_date__range=(start_date, end_date))
		
		return queryset

	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())
		data = queryset.aggregate(total=Sum('total'))

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			data.update({'orders': serializer.data})
			return self.get_paginated_response(data)

		serializer = self.get_serializer(queryset, many=True)
		data.update({'orders': serializer.data})
		return Response(data)