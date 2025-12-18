from django.db import models
from django.core.exceptions import ValidationError


class Cat(models.Model):
    name = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    breed = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Mission(models.Model):
    cat = models.OneToOneField(
        Cat,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mission"
    )
    is_completed = models.BooleanField(default=False)

    def clean(self):
        if self.cat and hasattr(self.cat, "mission") and self.cat.mission != self:
            raise ValidationError("Cat already has a mission")

    def update_completion_status(self):
        if all(target.is_completed for target in self.targets.all()):
            self.is_completed = True
            self.save()

    def __str__(self):
        return f"Mission {self.id}"


class Target(models.Model):
    mission = models.ForeignKey(
        Mission,
        related_name="targets",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def clean(self):
        if self.is_completed and self.pk:
            old = Target.objects.get(pk=self.pk)
            if old.notes != self.notes:
                raise ValidationError("Cannot update notes of completed target")

        if self.mission.is_completed:
            raise ValidationError("Cannot modify target of completed mission")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.mission.update_completion_status()

    def __str__(self):
        return f"{self.name} ({self.country})"
