from django.db.models import Sum

from rest_framework import serializers
from rest_framework.reverse import reverse
from sales.models import Product, Order, OrderDetail

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
	product_href = serializers.SerializerMethodField()

	def get_product_href(self, obj):
		request = self.context['request']
		return request.build_absolute_uri(obj.product.get_absolute_url())

	class Meta:
		model = OrderDetail
		fields = ('id', 
				  'product', 
				  'quantity', 
				  'price', 
				  'sub_total',
				  'product_href',)


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
		items = data.get('order_details')
		sub_totals = []

		for item in items:
			try:
				product = Product.objects.get(sku=item.get('product'))
				current_stock = product.stock - item.get('quantity') 
				sub_totals.append(product.price * item.get('quantity'))

				# Validasi jika stock produk - quantity menyebabkan nilai 0 itu
				# data invalid !
				if current_stock <= 0:
					raise serializers.ValidationError(f"product {product.sku} dont't be add to order")

				# Validasi jika stock product - quantity tidak boleh kurang dari stock minimum 
				# dari sebuah product
				if current_stock < product.stock_min:
					raise serializers.ValidationError(f"product {product.sku} dont't be add to order")

			except Product.DoesNotExist:
				raise serializers.ValidationError(f'Product {item.get("sku")} does not exist !')

			except Exception:
				raise serializers.ValidationError(f'Just something wrong !')

		# uang bayar tidak boleh lebih kecil dari total yang harus di bayar.
		if data.get('paid') < sum(sub_totals):
			raise serializers.ValidationError(f"paid not less than to total !")

		# Validasi tidak boleh ada nomer order yang sama ! (discuss)
		order = Order.objects.filter(order_number=data.get('order_number'))
		if order:
			raise serializers.ValidationError(f"Order {order.order_number} is available !")

		# TODO: add validation order details not multiple product same.
		return data

	def create(self, validated_data):
		order_details_data = validated_data.pop('order_details')
		order = Order.objects.create(**validated_data)

		for item in order_details_data:
			product = Product.objects.get(sku=item.pop('product'))
			product.stok = product.stock - item.get('quantity')
			product.save()
			
			item['sub_total'] = item.get('quantity') * product.price
			item['price'] = product.price

			order_detail = OrderDetail.objects.create(
				order=order, 
				product=product, 
				**item)

		total = order.order_details.aggregate(total_price=Sum('sub_total'))
		order.total = total.get('total_price')
		order.change = order.paid - total.get('total_price')
		order.save()

		return order


		# TODO: need to check again from create order with oder details 
		# using Postman.

class ReportStockMinimumSerializer(serializers.BaseSerializer):
	def to_representation(self, obj):
		return {
			'sku': obj.sku,
			'name': obj.name,
			'base_price': obj.base_price,
			'price': obj.price,
			'stock': obj.stock,
			'stock_min': obj.stock_min
		}


class ReportSaleSerializer(serializers.BaseSerializer):

	def to_representation(self, obj):
		url = self.context['request'].build_absolute_uri
		href = url(reverse('salesapi:order_detail', kwargs={'order_number': obj.order_number}))
		return {
			"order_number": obj.order_number,
			"total_orders": obj.total,
			"href": href,
			"items": obj.order_details.count(),
			# TODO: add link for retrieve order details !	
		}

	class Meta:
		model = Order

