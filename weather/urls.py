from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='docs'), name='docs-ui'),
    path('docs/', SpectacularAPIView.as_view(), name='docs'),
    path('account/create/', views.RegistrationView.as_view(), name='register'),
    path('account/delete/', views.DeleteAccount.as_view(), name='delete_account'),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('subscriptions/', views.UserSubscriptionsView.as_view(), name='subscriptions_list'),
    path('subscriptions/<int:id>/', views.SubscriptionActionsView.as_view(), name='subscription_action'),
    path('subscriptions/create/', views.NewSubscriptionView.as_view(), name='new_subscription'),
]
