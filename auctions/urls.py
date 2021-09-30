from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="create_listing"),
    path('listing/<int:listing_id>', views.view_listing, name="listing"),
    path('listing/<int:listing_id>/bid', views.bid, name='bid'),
    path('listing/<int:listing_id>/addcomment', views.add_comment, name='add_comment'),
    path('listing/<int:listing_id>/addwatchlist', views.add_watchlist, name="add_watchlist"),
]
