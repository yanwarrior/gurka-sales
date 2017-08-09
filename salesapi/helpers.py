from sales.models import Product, Order, OrderDetail
from rest_framework import serializers
from rest_framework.response import Response
from django.db.models import Sum, Count


def product_is_limited(product: Product, quantity: int) -> bool:
	if product.stock - quantity <= 0:
		return True
	
	if product.stock - quantity <= product.stock_min:
		return True

	return False


def calc_stock_product(sku: str, quantity: int) -> Product:
	try:
		product = Product.objects.get(sku=sku)
		product.stock = product.stock - quantity
		product.save()

		return product
	except Product.DoesNotExist:
		raise serializers.ValidationError('Product not available')


def calc_subtotal_orderdetail(order_detail: OrderDetail) -> OrderDetail:
	order_detail.sub_total = order_detail.product.price * order_detail.quantity
	order_detail.save()
	return order_detail


def order_paid_is_valid(order: Order) -> bool:
	total = order.order_details.aggregate(total_price=Sum('sub_total'))
	
	if order.paid < total.get('total_price'):
		order.delete()
		raise serializers.ValidationError(
			'Paid should not be less than total.')

	return True


def calc_total_change_order(order: Order) -> Order:
	if order_paid_is_valid(order):
		total = order.order_details.aggregate(total_price=Sum('sub_total'))
		order.total = total.get('total_price')
		order.change = order.paid - total.get('total_price')
		order.save()

	return order


def tweak_report_omzet_list(func):
	RESPONSE_ARGS = 1
	VIEW_ARGS = 0

	def wrap(*args, **kwargs):
		view = args[VIEW_ARGS]
		queryset = view.filter_queryset(view.get_queryset())
		total_orders = queryset.aggregate(total=Sum('total'), count=Count('order_number'))
		total_orders.update({'orders': func(*args, **kwargs).data})
		headers = {val[0]: val[1] for key, val in func(*args, **kwargs)._headers.items()}
		
		return Response(total_orders, headers=headers)

	wrap.__name__ = func.__name__
	wrap.__doc__ = func.__doc__
	return wrap
		

		