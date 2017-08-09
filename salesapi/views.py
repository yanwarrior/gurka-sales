from django.db.models import F
from django.db.models import Sum

from rest_framework import generics
from rest_framework.response import Response

from sales.models import Product, Order, OrderDetail
from .serializers import (
	ProductSerializer, 
	OrderSerializer, 
	ReportStockMinimumSerializer,
	ReportSaleSerializer)

from rest_framework.pagination import PageNumberPagination
from .helpers import tweak_report_omzet_list
from .core.pagination import LinkHeaderPagination


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


class OrderList(generics.ListCreateAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer


class OrderDetail(generics.RetrieveAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	lookup_field = 'order_number'


class ReportProductStockMin(generics.ListAPIView):
	queryset = Product.objects.filter(stock__lte=F('stock_min'))
	serializer_class = ReportStockMinimumSerializer


class ReportOmzet(generics.ListAPIView):
	queryset = Order.objects.all()
	serializer_class = ReportSaleSerializer
	pagination_class = LinkHeaderPagination

	def filter_queryset(self, queryset):
		start_date = self.request.query_params.get('start_date')
		end_date = self.request.query_params.get('end_date')
		queryset = Order.objects.all()

		if start_date and end_date:
			queryset = Order.objects.filter(
				order_date__range=(start_date, end_date))
		
		return queryset

	@tweak_report_omzet_list
	def list(self, request, *args, **kwargs):
		return super(ReportOmzet, self).list(request, *args, **kwargs)