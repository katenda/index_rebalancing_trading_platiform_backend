from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.db.models import Sum, Count
from decimal import Decimal
from .models import User, Transaction, Holding
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    TransactionSerializer, TransactionCreateSerializer,
    HoldingSerializer, HoldingCreateSerializer, PortfolioSummarySerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own profile unless they're staff
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        User registration endpoint
        POST /api/users/register/
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login endpoint
        POST /api/users/login/
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        User logout endpoint
        POST /api/users/logout/
        """
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Get current user profile
        GET /api/users/profile/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update current user profile
        PUT/PATCH /api/users/update_profile/
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction model
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own transactions unless they're staff
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get transactions filtered by type
        GET /api/transactions/by_type/?type=deposit
        """
        transaction_type = request.query_params.get('type')
        if transaction_type:
            queryset = self.get_queryset().filter(transaction_type=transaction_type)
        else:
            queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent transactions (last 10)
        GET /api/transactions/recent/
        """
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get transaction summary
        GET /api/transactions/summary/
        """
        queryset = self.get_queryset()
        
        total_debits = queryset.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        total_credits = queryset.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        transaction_count = queryset.count()
        
        return Response({
            'total_debits': total_debits,
            'total_credits': total_credits,
            'net_amount': total_credits - total_debits,
            'transaction_count': transaction_count,
            'current_balance': request.user.balance
        })


class HoldingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Holding model
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own holdings unless they're staff
        if self.request.user.is_staff:
            return Holding.objects.all()
        return Holding.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HoldingCreateSerializer
        return HoldingSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_stock(self, request):
        """
        Get holdings filtered by stock symbol
        GET /api/holdings/by_stock/?stock=AAPL
        """
        stock = request.query_params.get('stock')
        if stock:
            queryset = self.get_queryset().filter(stock__iexact=stock)
        else:
            queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def profitable(self, request):
        """
        Get only profitable holdings
        GET /api/holdings/profitable/
        """
        queryset = self.get_queryset().extra(
            where=["(quantity * current_price) > (quantity * buying_price)"]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def losing(self, request):
        """
        Get only losing holdings
        GET /api/holdings/losing/
        """
        queryset = self.get_queryset().extra(
            where=["(quantity * current_price) < (quantity * buying_price)"]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get holdings summary
        GET /api/holdings/summary/
        """
        queryset = self.get_queryset()
        
        total_invested = sum(holding.total_invested for holding in queryset)
        total_current_value = sum(holding.current_value for holding in queryset)
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_percentage = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        return Response({
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percentage': round(total_profit_loss_percentage, 2),
            'holdings_count': queryset.count()
        })


class PortfolioViewSet(viewsets.ViewSet):
    """
    ViewSet for portfolio-related operations
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get complete portfolio summary
        GET /api/portfolio/summary/
        """
        user = request.user
        holdings = Holding.objects.filter(user=user)
        transactions = Transaction.objects.filter(user=user)
        
        # Calculate holdings totals
        total_invested = sum(holding.total_invested for holding in holdings)
        total_current_value = sum(holding.current_value for holding in holdings)
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_percentage = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        data = {
            'total_balance': user.balance,
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percentage': round(total_profit_loss_percentage, 2),
            'holdings_count': holdings.count(),
            'transactions_count': transactions.count()
        }
        
        serializer = PortfolioSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Get portfolio performance metrics
        GET /api/portfolio/performance/
        """
        user = request.user
        holdings = Holding.objects.filter(user=user)
        
        if not holdings.exists():
            return Response({
                'message': 'No holdings found',
                'total_return': 0,
                'best_performer': None,
                'worst_performer': None
            })
        
        # Calculate performance metrics
        performance_data = []
        for holding in holdings:
            performance_data.append({
                'stock': holding.stock,
                'profit_loss': float(holding.profit_loss),
                'profit_loss_percentage': float(holding.profit_loss_percentage)
            })
        
        # Sort by performance
        performance_data.sort(key=lambda x: x['profit_loss_percentage'], reverse=True)
        
        total_return = sum(item['profit_loss'] for item in performance_data)
        
        return Response({
            'total_return': total_return,
            'best_performer': performance_data[0] if performance_data else None,
            'worst_performer': performance_data[-1] if performance_data else None,
            'all_performances': performance_data
        })