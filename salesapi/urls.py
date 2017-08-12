from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^products/$', 
		views.ProductList.as_view(), 
		name='product_list'),

	url(r'^products/(?P<sku>[\w-]+)/$', 
		views.ProductDetail.as_view(), 
		name='product_detail'),

	url(r'^orders/$', 
		views.OrderList.as_view(), 
		name='order-list'),

	url(r'^orders/(?P<order_number>[\w-]+)/$', 
		views.OrderDetail.as_view(), 
		name='order_detail'),

	url(r'^report/products/stock-min/$', 
		views.ReportProductStockMin.as_view(), 
		name='report_product_stock_min'),
	
	url(r'^reports/omzet/$', 
		views.ReportOmzet.as_view(), 
		name='report_omzet'),
]