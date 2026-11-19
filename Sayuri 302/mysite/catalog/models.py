from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
class Categoria(models.Model):
     nombre = models.CharField(max_length=100)
     descripcion = models.TextField(blank=True, null=True)
     def __str__(self):
          return self.nombre
     class Meta:
          verbose_name = "Categoría"
          verbose_name_plural = "Categorías"
class Producto(models.Model):
     nombre = models.CharField(max_length=200)
     descripcion = models.TextField(blank=True, null=True)
     precio = models.DecimalField(max_digits=10, decimal_places=2)
     stock = models.IntegerField(default=0)
     categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
     fecha_creacion = models.DateTimeField(auto_now_add=True)
     activo = models.BooleanField(default=True)
     def __str__(self):
          return self.nombre
     class Meta:
          verbose_name = "Producto"
          verbose_name_plural = "Productos"
          ordering = ['nombre']  
class Perfil(models.Model):
     """Modelo para extender la información del usuario"""
     usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
     telefono = models.CharField(max_length=20, blank=True, null=True)
     direccion = models.TextField(blank=True, null=True)
     fecha_nacimiento = models.DateField(blank=True, null=True)
     foto = models.ImageField(upload_to='perfiles/', blank=True, null=True
)
     fecha_creacion = models.DateTimeField(auto_now_add=True)
     fecha_actualizacion = models.DateTimeField(auto_now=True)
     def __str__(self):
          return f'Perfil de {self.usuario.username}'
     class Meta:
          verbose_name = 'Perfil'
          verbose_name_plural = 'Perfiles'
# Señales para crear/actualizar el perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
     if created:
          Perfil.objects.create(usuario=instance)
@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
     instance.perfil.save()
