from sales.models import Product, Order, OrderDetail
from rest_framework import serializers
from django.db.models import Sum


def product_not_be_used(product: Product, quantity: int) -> bool:
	if product.stock - quantity <= 0:
		return True
	
	if product.stock - quantity <= product.stock_min:
		return True

	return False


def reduce_stock(sku: str, quantity: int) -> Product:
	try:
		product = Product.objects.get(sku=sku)
		product.stock = product.stock - quantity
		product.save()

		return product
	except Product.DoesNotExist:
		raise serializers.ValidationError('Product not available')


def calculate_order_detail(order_detail: OrderDetail) -> OrderDetail:
	order_detail.sub_total = order_detail.product.price * order_detail.quantity
	order_detail.save()
	return order_detail


def calculate_order(order: Order) -> Order:
	total = order.order_details.aggregate(total_price=Sum('sub_total'))
	
	if order.paid < total.get('total_price'):
		order.delete()
		raise serializers.ValidationError('Paid should not be less than total.')
	else:
		order.total = total.get('total_price')
		order.change = order.paid - order.total
		order.save()

	return order






