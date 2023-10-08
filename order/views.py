import stripe

from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render

from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Order, OrderItem
from . serializers import OrderSerializer, MyOrderSerializer

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string



@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        paid_amount = sum(item.get('quantity') * item.get('product').price for item in serializer.validated_data['items'])

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency='USD',
                description='Charge from Djackets',
                source=serializer.validated_data['stripe_token']
            )
            serializer.save(user=request.user, paid_amount=paid_amount)
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            user_email = request.data.get('email', '')
            phone = request.data.get('phone', '')
            place = request.data.get('place', '')
            zipcode = request.data.get('zipcode', '')
            template = render_to_string('order/email.html', {'first_name': first_name, 'last_name' : last_name,
                                                            "user_email" : user_email, "phone" : phone, "place" : place,
                                                            "zipcode" : zipcode})
            # print(first_name+last_name+user_email+place)
            try:
                email = EmailMultiAlternatives(
                subject="Thank you for purchasings",
                body='DSDDSDSDSD',
                from_email = settings.EMAIL_HOST_USER,
                to=[user_email],
                # ["bcc@example.com"],
                # reply_to=["another@example.com"],
                # headers={"Message-ID": "foo"},
                )
                email.send()
            except Exception as e:
                print(f"Error sending email: {str(e)}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrdersList(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = MyOrderSerializer(orders, many=True)
        return Response(serializer.data)

