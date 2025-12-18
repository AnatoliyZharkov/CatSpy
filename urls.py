from django.urls import path
from . import views

urlpatterns = [
    # Cats
    path("cats/", views.list_cats),
    path("cats/create/", views.create_cat),
    path("cats/<int:cat_id>/", views.update_cat_salary),
    path("cats/<int:cat_id>/delete/", views.delete_cat),

    # Missions
    path("missions/create/", views.create_mission),
    path("missions/<int:mission_id>/delete/", views.delete_mission),
    path(
        "missions/<int:mission_id>/assign/<int:cat_id>/",
        views.assign_cat_to_mission
    ),

    # Targets
    path("targets/<int:target_id>/", views.update_target),
]
