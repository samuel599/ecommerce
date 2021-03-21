from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *
import datetime
from .utils import cookieCart, cartData, guestOrder
# Create your views here.
def base(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cart = json.loads(request.COOKIES['cart'])
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0, 'shipping':False}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request, 'store/base.html', context)

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    product = Product.objects.all()
    context = {'product':product,'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('udpateItem')
    print(productId)
    print(action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0 :
        orderItem.delete()

    return JsonResponse('Item has been added',safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    if len(request.body) == 0:
        return JsonResponse('empty', safe=False)

    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete == True
        order.save()

        if order.shipping == True:
            Shipping.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],

            )

    else:
        customer, order = guestOrder(request.data)
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        Shipping.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )


    return JsonResponse('payment complete!', safe=False)
