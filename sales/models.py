from django.db import models
import random


class Product(models.Model):
	sku = models.CharField(max_length=30, unique=True, primary_key=True)
	name = models.CharField(max_length=30)
	base_price = models.PositiveIntegerField()
	price = models.PositiveIntegerField()
	stock = models.PositiveIntegerField()
	stock_min = models.PositiveIntegerField()

	def __str__(self):
		return self.sku

	class Meta:
		db_table = 'product'


class Order(models.Model):
	order_number = models.CharField(max_length=30, unique=True, primary_key=True)
	order_date = models.DateTimeField(auto_now_add=True)
	total = models.PositiveIntegerField()
	paid = models.PositiveIntegerField()
	change = models.PositiveIntegerField()

	def __str__(self):
		return self.order_number

	class Meta:
		db_table = 'order'


class OrderDetail(models.Model):
	order = models.ForeignKey(Order, related_name='order_details')
	product = models.ForeignKey(Product, related_name='product_detail')
	quantity = models.PositiveIntegerField()
	price = models.PositiveIntegerField()
	sub_total = models.PositiveIntegerField()

	def __str__(self):
		return self.order.order_number + " " + self.product.sku

	class Meta:
		db_table = 'orderdetail'


