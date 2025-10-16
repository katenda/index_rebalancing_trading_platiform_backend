from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Transaction, Holding


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'userid', 'balance', 'is_active', 'date_joined', 'last_login', 'password', 'password_confirm']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'userid', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model
    """
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'user_name', 'user_email', 'transaction_type', 'debit', 'credit', 'description', 'date', 'balance_after']
        read_only_fields = ['id', 'date', 'balance_after']
    
    def create(self, validated_data):
        # Calculate balance_after based on user's current balance
        user = validated_data['user']
        current_balance = user.balance
        
        # Update user balance
        net_amount = validated_data['credit'] - validated_data['debit']
        user.balance += net_amount
        user.save()
        
        # Set balance_after
        validated_data['balance_after'] = user.balance
        
        return super().create(validated_data)


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating transactions (simplified)
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'debit', 'credit', 'description']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Calculate balance_after based on user's current balance
        current_balance = user.balance
        net_amount = validated_data['credit'] - validated_data['debit']
        user.balance += net_amount
        user.save()
        
        # Set balance_after
        validated_data['balance_after'] = user.balance
        
        return super().create(validated_data)


class HoldingSerializer(serializers.ModelSerializer):
    """
    Serializer for Holding model
    """
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    total_invested = serializers.ReadOnlyField()
    current_value = serializers.ReadOnlyField()
    profit_loss = serializers.ReadOnlyField()
    profit_loss_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Holding
        fields = ['id', 'user', 'user_name', 'user_email', 'stock', 'quantity', 'buying_price', 'current_price', 'date_purchased', 'total_invested', 'current_value', 'profit_loss', 'profit_loss_percentage']
        read_only_fields = ['id', 'date_purchased']


class HoldingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating holdings (simplified)
    """
    class Meta:
        model = Holding
        fields = ['stock', 'quantity', 'buying_price', 'current_price']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class PortfolioSummarySerializer(serializers.Serializer):
    """
    Serializer for portfolio summary
    """
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_invested = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_current_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit_loss = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit_loss_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    holdings_count = serializers.IntegerField()
    transactions_count = serializers.IntegerField()
