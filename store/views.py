import json

from django.shortcuts import render
from . import models
from django.http import JsonResponse
import datetime


def store(request):
    products = models.Product.objects.all()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    else:
        order = {
            'get_cart_total': 0,
            'get_cart_items': 0,
        }

    context = {
        'products': products,
        'order': order,
    }
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
    else:
        order = {
            'get_cart_total': 0,
            'get_cart_items': 0,
        }
    context = {
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
    else:
        order = {
            'get_cart_total': 0,
            'get_cart_items': 0,
        }
    context = {
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    product = models.Product.objects.get(pk=productId)
    orderitem, created = models.OrderItem.objects.get_or_create(product=product, order=order)

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()
    return JsonResponse('Item was updated', safe=False)


def processOrder(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        total = int(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            models.ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                phone_number=data['shipping']['number'],
            )
    else:
        print("User didn't logg in")

    return JsonResponse('Payment is complete..', safe=False)