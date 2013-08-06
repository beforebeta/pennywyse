import datetime
from django.contrib.auth.models import User
from django.db import models

class Visitor(models.Model):
    user                = models.ForeignKey(User, db_index=True)
    session_key         = models.CharField(max_length=40, db_index=True)
    acquisition_source  = models.CharField(max_length=255, default="organic", db_index=True)

    email               = models.CharField(max_length=75, db_index=True)
    date_added          = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user:
            self.email = self.user.email
        super(Visitor, self).save(*args, **kwargs)

