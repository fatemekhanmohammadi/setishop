from django.shortcuts import render
from .serializers import CategorySerializer,ProductListSerializer,ProductDetailSerializer,FavoriteProductSerializer,ProductRatingSerializer
from rest_framework import generics, permissions
from .models import Category,Product,FavoriteProduct, ProductRating
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework import filters
from .filters import ProductFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cart import Cart
from .models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample


from django.contrib.auth import get_user_model

User=get_user_model()

#========================================================================================================

#لیست دسته بندی ها
@extend_schema(tags=['Products'])


class CategoryListView(generics.ListAPIView):
    queryset=Category.objects.all().order_by('id')
    serializer_class=CategorySerializer
    permission_classes=[permissions.AllowAny]


#========================================================================================================

#لیست محصولات
@extend_schema(tags=['Products'])

class ProductListView(generics.ListAPIView):
    queryset =Product.objects.filter(is_active=True).order_by('id')
    serializer_class=ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter  
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']



#==========================================================================================================

#جزییات یک محصول
@extend_schema(tags=['Products'])

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'       #«یک Product فعال را پیدا کن، ولی برای پیدا کردنش از slug استفاده کن.»


#==========================================================================================================
@extend_schema(tags=['Products'])

class ProductRatingView(APIView):
    def get(self, request, product_id):
        ratings=ProductRating.objects.filter(product_id=product_id)
        serializer=ProductRatingSerializer(ratings,many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        if ProductRating.objects.filter(user=request.user, product_id=product_id).exists():
            return Response({'error':'شما قبلا نظر و امتیاز ثبت کردین !'},status=status.HTTP_400_BAD_REQUEST )
        
        score=request.data.get('score')
        comment=request.data.get('comment','')
        ProductRating.objects.create(user=request.user, product_id=product_id, score=score,comment=comment)
        return Response({'messag':'نظر و امتیاز شا ثبت شد با تشکر '}, status=status.HTTP_201_CREATED) 



#===========================================================================================================

@extend_schema(tags=['Products'])

class CartDetailView(APIView):
    def get(self, request):
        cart = Cart(request)
        items, total = cart.get_items()

        data = []
        for item in items:
            data.append({
                'product': ProductListSerializer(item['product'], context={'request': request}).data,
                'quantity': item['quantity'],# تعداد اون محصولا
                'item_total': item['item_total'],# قیمت محصول
            })

        return Response({
            'items': data,
            'total': total,
        })

#=================================================================================================================
@extend_schema(tags=['Products'])

class CartAddView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return Response({'error': 'محصول پیدا نشد'}, status=status.HTTP_404_NOT_FOUND)

        cart = Cart(request)
        cart.add(product, quantity)
        return Response({'message': 'محصول اضافه شد'}, status=status.HTTP_201_CREATED)
#================================================================================================================ 
@extend_schema(tags=['Products'])

class CartUpdateView(APIView):
    def patch(self, request, product_id):
        quantity = int(request.data.get('quantity'))
        cart = Cart(request)
        cart.update(product_id, quantity)
        return Response({'message': 'تعداد بروزرسانی شد'})

#=================================================================================================================
@extend_schema(tags=['Products'])

class CartRemoveView(APIView):
    def delete(self, request, product_id):
        cart = Cart(request)
        cart.remove(product_id)
        return Response({'message': 'محصول حذف شد'}, status=status.HTTP_204_NO_CONTENT)


#================================================================================================================

@extend_schema(tags=['Products'])


class AdminProductCreateView(generics.CreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductDetailSerializer
    permission_classes=[permissions.IsAdminUser]



@extend_schema(tags=['Products'])


class AdminProductUpdateView(generics.UpdateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductDetailSerializer
    permission_classes=[permissions.IsAdminUser]




@extend_schema(tags=['Products'])

class AdminProductDeleteView(generics.DestroyAPIView):
    queryset=Product.objects.all()
    permission_classes=[permissions.IsAdminUser]


#===================================================================================================================

@extend_schema(tags=['Products'])
class FavoriteProductView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id=None):
        if product_id:
            favorites = FavoriteProduct.objects.filter(user=request.user, product_id=product_id)
        else:
        
            favorites = FavoriteProduct.objects.filter(user=request.user)
        serializer = FavoriteProductSerializer(favorites, many=True)
        return Response(serializer.data)

 
    def post(self, request, product_id):
        if FavoriteProduct.objects.filter(user=request.user, product_id=product_id).exists():
            return Response({'error': 'این محصول قبلا به لیست شما اضافه شده'}, status=status.HTTP_400_BAD_REQUEST)
        FavoriteProduct.objects.create(user=request.user, product_id=product_id)
        return Response({'message': 'به علاقه مندی ها اضافه شد'}, status=status.HTTP_201_CREATED)

   
    def delete(self, request, product_id):
        favorite = FavoriteProduct.objects.filter(user=request.user, product_id=product_id).first()
        if not favorite:
            return Response({'error': 'محصول یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        
        favorite.delete()
        return Response({'message': 'محصول حذف شد'}, status=status.HTTP_200_OK)