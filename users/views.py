from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from inventory.models import Store
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

def is_admin(user):
    """Check if user is an admin/superuser"""
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def assign_store(request, user_id):
    """Assign a store to a staff member (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get active stores for selection
    stores = Store.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        store_id = request.POST.get('store')
        
        if store_id and store_id.isdigit():
            # Assign user to selected store
            store = get_object_or_404(Store, id=store_id)
            user_profile.store = store
            user_profile.save()
            messages.success(request, f"{user.username} has been assigned to {store.name}")
        else:
            # Remove store assignment (global access)
            user_profile.store = None
            user_profile.save()
            messages.success(request, f"{user.username} now has global access (no store restriction)")
        
        return redirect('admin:auth_user_changelist')
    
    return render(request, 'users/assign_store.html', {
        'user': user,
        'user_profile': user_profile,
        'stores': stores,
    })

@login_required
def current_user_store(request):
    """Display the current user's store assignment"""
    if hasattr(request.user, 'profile') and request.user.profile.store:
        store = request.user.profile.store
        return render(request, 'users/user_store.html', {
            'store': store,
        })
    else:
        messages.info(request, "You don't have a store assignment. Please contact an administrator.")
        return redirect('dashboard:index')


@login_required
def staff_profile(request):
    """Staff profile page — view and update profile information"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            new_email = request.POST.get('email', request.user.email).strip()
            if new_email and new_email != request.user.email:
                if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                    messages.error(request, "That email address is already in use.")
                    return redirect('profile')
                request.user.email = new_email
            request.user.save()

            profile.phone = request.POST.get('phone', profile.phone)
            profile.position = request.POST.get('position', profile.position)
            profile.bio = request.POST.get('bio', profile.bio)
            profile.address = request.POST.get('address', profile.address)
            profile.city = request.POST.get('city', profile.city)
            profile.postal_code = request.POST.get('postal_code', profile.postal_code)

            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if avatar_file.content_type not in allowed_types:
                    messages.error(request, "Please upload a valid image file (JPEG, PNG, GIF, or WebP).")
                    return redirect('profile')
                if avatar_file.size > 5 * 1024 * 1024:
                    messages.error(request, "Image file size must be under 5 MB.")
                    return redirect('profile')
                if profile.avatar:
                    profile.avatar.delete(save=False)
                profile.avatar = avatar_file

            if request.POST.get('remove_avatar') == '1' and profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None

            profile.save()

            logger.info(f"Profile updated for user {request.user.username}")
            messages.success(request, "Your profile has been updated successfully.")

        elif action == 'change_password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_password):
                messages.error(request, "Your current password is incorrect.")
                return redirect('profile')

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect('profile')

            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect('profile')

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            logger.info(f"Password changed for user {request.user.username}")
            messages.success(request, "Your password has been changed successfully.")

        return redirect('profile')

    return render(request, 'profile.html', {
        'profile': profile,
    })


@login_required
def staff_settings(request):
    """Staff settings page — manage notification and display preferences"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.low_stock_alerts = request.POST.get('low_stock_alerts') == 'on'
        profile.rental_reminders = request.POST.get('rental_reminders') == 'on'
        profile.items_per_page = int(request.POST.get('items_per_page', 25))
        profile.save()

        logger.info(f"Settings updated for user {request.user.username}")
        messages.success(request, "Your settings have been saved successfully.")
        return redirect('settings')

    return render(request, 'settings.html', {
        'profile': profile,
    })