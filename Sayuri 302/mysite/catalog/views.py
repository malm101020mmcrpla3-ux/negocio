from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .models import Producto, Categoria, Perfil
from .forms import ProductoForm, CategoriaForm, RegistroForm, LoginForm,PerfilForm

# ==================== VISTAS BÁSICAS ====================
def hola_mundo(request):
    return HttpResponse("¡Hola Mundo desde Django!")

def inicio(request):
    return render(request, 'catalog/inicio.html')

# ==================== VISTAS DE PRODUCTOS (CRUD) ====================
def lista_productos(request):
    productos = Producto.objects.all()
    contexto = {'productos': productos, 'titulo': 'Lista de Productos'}
    return render(request, 'catalog/lista_productos.html', contexto)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    contexto = {'producto': producto}
    return render(request, 'catalog/detalle_producto.html', contexto)

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('catalog:lista_productos')
        else:
            form = ProductoForm()
            contexto = {'form': form, 'titulo': 'Crear Producto', 'accion': 'Crear'}
            return render(request, 'catalog/formulario_producto.html', contexto)

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('catalog:lista_productos')
        else:
            form = ProductoForm(instance=producto)
            contexto = {'form': form, 'titulo': 'Editar Producto', 'accion': 'Editar'}
            return render(request, 'catalog/formulario_producto.html', contexto)

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('catalog:lista_productos')
    contexto = {'producto': producto}
    return render(request, 'catalog/confirmar_eliminar.html', contexto)

# ==================== VISTAS DE CATEGORÍAS (CRUD) ====================
def lista_categorias(request):
    categorias = Categoria.objects.all()
    contexto = {'categorias': categorias, 'titulo': 'Lista de Categorías'
                }
    return render(request, 'catalog/lista_categorias.html', contexto)

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:lista_categorias')
    else:
        form = CategoriaForm()
    contexto = {'form': form, 'titulo': 'Crear Categoría', 'accion': 'Crear'}
    return render(request, 'catalog/formulario_categoria.html', contexto)

def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('catalog:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    contexto = {'form': form, 'titulo': 'Editar Categoría', 'accion': 'Editar'}
    return render(request, 'catalog/formulario_categoria.html', contexto)

def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('catalog:lista_categorias')
    contexto = {'categoria': categoria}
    return render(request, 'catalog/confirmar_eliminar_categoria.html', contexto)

# ==================== VISTAS DE AUTENTICACIÓN ====================
def registro(request):
    """Vista para registrar nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('catalog:inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada exitosamente.')
            return redirect('catalog:inicio')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()
    contexto = {'form': form, 'titulo': 'Registro de Usuario'}
    return render(request, 'catalog/registro.html', contexto)

def iniciar_sesion(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('catalog:inicio')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'catalog:inicio')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            form = LoginForm()
            contexto = {'form': form, 'titulo': 'Iniciar Sesión'}
            return render(request, 'catalog/login.html', contexto)

def cerrar_sesion(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('catalog:inicio')

@login_required
def perfil(request):
    """Vista para ver y editar el perfil del usuario"""
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('catalog:perfil')
        
        else:
            form = PerfilForm(instance=perfil)
            contexto = {'form': form, 'perfil': perfil, 'titulo': 'Mi Perfil'}
            return render(request, 'catalog/perfil.html', contexto)

@login_required
def lista_usuarios(request):
    """Vista para listar usuarios (solo para administradores)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('catalog:inicio')
    usuarios = User.objects.all().order_by('username')
    contexto = {'usuarios': usuarios, 'titulo': 'Lista de Usuarios'}
    return render(request, 'catalog/lista_usuarios.html', contexto)

@login_required
def crear_producto(request):
    """CREATE - Crea un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('catalog:lista_productos')
    else:
        form = ProductoForm()
    contexto = {'form': form, 'titulo': 'Crear Producto', 'accion': 'Crear'}
    return render(request, 'catalog/formulario_producto.html', contexto)

@login_required
def editar_producto(request, producto_id):
    """UPDATE - Edita un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('catalog:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    contexto = {'form': form, 'titulo': 'Editar Producto', 'accion': 'Editar'}
    return render(request, 'catalog/formulario_producto.html', contexto)

@login_required
def eliminar_producto(request, producto_id):
    """DELETE - Elimina un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('catalog:lista_productos')
    contexto = {'producto': producto}
    return render(request, 'catalog/confirmar_eliminar.html', contexto)