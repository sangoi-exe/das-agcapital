from django.contrib.auth.models import AbstractUser


class DefaultAccount(AbstractUser):
    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super(DefaultAccount, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
