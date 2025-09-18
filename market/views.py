from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, CreditListing, Transaction
from .forms import ProjectForm, ListingForm, BuyerRegisterForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse

# Simple session-based cart (MVP)
CART_SESSION_KEY = 'cart'  # structure: { listing_id: credits_requested }

def index(request):
    featured = CreditListing.objects.filter(available=True).order_by('-created_at')[:6]
    return render(request, 'index.html', {'featured': featured})

def project_list(request):
    listings = CreditListing.objects.filter(available=True).order_by('-created_at')
    return render(request, 'project_list.html', {'listings': listings})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    listings = project.listings.filter(available=True)
    return render(request, 'project_detail.html', {'project': project, 'listings': listings})

@login_required
def project_onboard(request):
    if request.method == 'POST':
        p_form = ProjectForm(request.POST)
        l_form = ListingForm(request.POST)
        if p_form.is_valid() and l_form.is_valid():
            project = p_form.save(commit=False)
            project.owner = request.user
            project.save()
            listing = l_form.save(commit=False)
            listing.project = project
            listing.save()
            messages.success(request, "Project and listing created. It will appear after admin review.")
            return redirect('market:dashboard')
    else:
        p_form = ProjectForm()
        l_form = ListingForm()
    return render(request, 'project_onboard.html', {'p_form': p_form, 'l_form': l_form})

def buyer_register(request):
    if request.method == 'POST':
        form = BuyerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created and you're logged in.")
            return redirect('market:index')
    else:
        form = BuyerRegisterForm()
    return render(request, 'buyer_register.html', {'form': form})

def _get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})

def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for lid, qty in cart.items():
        try:
            listing = CreditListing.objects.get(pk=int(lid))
        except CreditListing.DoesNotExist:
            continue
        credits = int(qty)
        amount = credits * listing.price_per_credit
        items.append({'listing': listing, 'credits': credits, 'amount': amount})
        total += amount
    return render(request, 'cart.html', {'items': items, 'total': total})

def add_to_cart(request, listing_id=None):
    # Not wired to URL in this MVP; listing detail 'add' uses a form POST to /cart/ via JS in template
    pass

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = _get_cart(request)
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('market:project_list')
        # Create transactions for each listing (simple approach)
        transactions = []
        total_amount = Decimal('0.00')
        for lid, qty in cart.items():
            listing = get_object_or_404(CreditListing, pk=int(lid))
            qty = int(qty)
            amount = qty * listing.price_per_credit
            txn = Transaction.objects.create(
                buyer=request.user,
                listing=listing,
                credits_bought=qty,
                total_amount=amount,
                status='PENDING'
            )
            transactions.append(txn)
            total_amount += amount
        # Here you would integrate with M-Pesa / Flutterwave. For MVP we simulate redirect to success.
        # Clear cart
        request.session[CART_SESSION_KEY] = {}
        messages.info(request, f"Checkout created. Simulating payment for ${total_amount}.")
        # For demo: go to first transaction success
        return redirect('market:payment_success', txn_id=transactions[0].id)
    else:
        return redirect('market:cart')

@login_required
def payment_success(request, txn_id):
    txn = get_object_or_404(Transaction, pk=txn_id, buyer=request.user)
    # Simulate success
    txn.status = 'SUCCESS'
    txn.payment_reference = f"SIM-{txn.id}"
    txn.save()
    # TODO: decrement listing available_credits, mark listing unavailable if 0
    listing = txn.listing
    if txn.credits_bought <= listing.available_credits:
        listing.available_credits -= txn.credits_bought
        if listing.available_credits == 0:
            listing.available = False
        listing.save()
    messages.success(request, f"Payment successful. Transaction #{txn.id} confirmed.")
    return render(request, 'checkout.html', {'txn': txn})

@login_required
def dashboard(request):
    projects = request.user.projects.all()
    txns = request.user.transactions.all()
    return render(request, 'dashboard.html', {'projects': projects, 'txns': txns})

@login_required
def certificate_view(request, txn_id):
    txn = get_object_or_404(Transaction, pk=txn_id, buyer=request.user, status='SUCCESS')
    # Simple HTML certificate. For PDF generation, you can integrate ReportLab or xhtml2pdf.
    return render(request, 'certificate.html', {'txn': txn})
