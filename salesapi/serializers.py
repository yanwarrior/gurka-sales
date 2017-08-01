from rest_framework import serializers
from sales.models import Product, Order, OrderDetail
from salesapi.helpers import (product_is_limited, 
	calc_stock_product, calc_subtotal_orderdetail, calc_total_change_order, order_paid_is_valid)

# TODO: Create tests.
# TODO: Add features for reporting data.

class ProductSerializer(serializers.ModelSerializer):

	class Meta:
		model = Product
		fields = ('sku', 
				  'name', 
				  'base_price', 
				  'price', 
				  'stock', 
				  'stock_min')


class OrderDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderDetail
		fields = ('id', 
				  'product', 
				  'quantity', 
				  'price', 
				  'sub_total')


class OrderSerializer(serializers.ModelSerializer):
	order_details = OrderDetailsSerializer(many=True)

	class Meta:
		model = Order
		fields = ('order_number', 
				  'order_date',
				  'total', 
				  'paid', 
				  'change', 
				  'order_details')

	def validate(self, data):
		order_details_data = data.get('order_details')
		for order_detail_data in order_details_data:
			sku = order_detail_data.get('product')
			product = Product.objects.get(sku=sku)

			if product_is_limited(product, order_detail_data.get('quantity')):
 				raise serializers.ValidationError(f"product {product.sku} dont't be add to order")

		return data

	def create(self, validated_data):
		order_details_data = validated_data.pop('order_details')
		order = Order.objects.create(**validated_data)

		for order_detail_data in order_details_data:
			product = calc_stock_product(order_detail_data.pop('product'), 
										 order_detail_data.pop('quantity'))
			order_detail = OrderDetail.objects.create(
				order=order, 
				product=product, 
				**order_detail_data)

			calc_subtotal_orderdetail(order_detail)

		order = calc_total_change_order(order)
		return order


		# TODO: need to check again from create order with oder details 
		# using Postman.


