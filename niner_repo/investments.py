from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from db import get_db
from auth import login_required
from datetime import datetime, timedelta
import re
from gamification import on_investment_added

bp = Blueprint('investments', __name__, url_prefix='/investments')

@bp.route('/')
@login_required
def index():
    """View investment portfolio"""
    db = get_db()
    
    # Get all investments for the user
    investments = db.execute(
        '''SELECT i.*, it.icon, it.color, it.description
           FROM investments i
           LEFT JOIN investment_types it ON i.asset_type = it.name
           WHERE i.user_id = ?
           ORDER BY i.purchase_date DESC''',
        (g.user['id'],)
    ).fetchall()
    
    # Get investment types
    investment_types = db.execute(
        'SELECT * FROM investment_types ORDER BY name'
    ).fetchall()
    
    # Calculate portfolio statistics
    portfolio_stats = calculate_portfolio_stats(investments)
    
    # Get asset allocation (by type)
    asset_allocation = calculate_asset_allocation(investments)
    
    # Get top performers
    top_performers = get_top_performers(investments, limit=5)
    
    return render_template(
        'investments/index.html',
        investments=investments,
        investment_types=investment_types,
        portfolio_stats=portfolio_stats,
        asset_allocation=asset_allocation,
        top_performers=top_performers
    )

@bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new investment"""
    asset_name = request.form.get('asset_name', '').strip()
    asset_type = request.form.get('asset_type', '').strip()
    ticker_symbol = request.form.get('ticker_symbol', '').strip().upper()
    quantity = request.form.get('quantity', '').strip()
    purchase_price = request.form.get('purchase_price', '').strip()
    purchase_date = request.form.get('purchase_date', '').strip()
    current_price = request.form.get('current_price', '').strip()
    notes = request.form.get('notes', '').strip()
    
    # Validation
    errors = []
    
    if not asset_name:
        errors.append('Asset name is required.')
    elif len(asset_name) > 100:
        errors.append('Asset name must be 100 characters or less.')
    
    if not asset_type:
        errors.append('Asset type is required.')
    elif asset_type not in ['stock', 'bond', 'crypto', 'etf', 'mutual_fund', 'real_estate', 'commodity', 'other']:
        errors.append('Invalid asset type.')
    
    if not quantity:
        errors.append('Quantity is required.')
    else:
        try:
            quantity_float = float(quantity)
            if quantity_float <= 0:
                errors.append('Quantity must be greater than 0.')
        except ValueError:
            errors.append('Quantity must be a valid number.')
    
    if not purchase_price:
        errors.append('Purchase price is required.')
    else:
        try:
            purchase_price_float = float(purchase_price)
            if purchase_price_float <= 0:
                errors.append('Purchase price must be greater than 0.')
        except ValueError:
            errors.append('Purchase price must be a valid number.')
    
    if not purchase_date:
        errors.append('Purchase date is required.')
    else:
        try:
            datetime.fromisoformat(purchase_date)
            # Check if date is not in the future
            if datetime.fromisoformat(purchase_date) > datetime.now():
                errors.append('Purchase date cannot be in the future.')
        except ValueError:
            errors.append('Invalid purchase date format.')
    
    if current_price:
        try:
            current_price_float = float(current_price)
            if current_price_float < 0:
                errors.append('Current price cannot be negative.')
        except ValueError:
            errors.append('Current price must be a valid number.')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('investments.index'))
    
    # Insert investment
    db = get_db()
    db.execute(
        '''INSERT INTO investments 
           (user_id, asset_name, ticker_symbol, asset_type, quantity, 
            purchase_price, purchase_date, current_price, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (g.user['id'], asset_name, ticker_symbol, asset_type, quantity,
         purchase_price, purchase_date, purchase_price, notes)
    )
    db.commit()
    
    # GAMIFICATION: Award points for adding investment
    try:
        on_investment_added(g.user['id'])
    except Exception as e:
        print(f"Gamification error: {e}")
    
    flash('Investment added successfully!', 'success')
    return redirect(url_for('investments.index'))

@bp.route('/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    """Edit an existing investment"""
    db = get_db()
    
    # Get the investment and verify ownership
    investment = db.execute(
        'SELECT * FROM investments WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not investment:
        flash('Investment not found.', 'danger')
        return redirect(url_for('investments.index'))
    
    # Get form data
    asset_name = request.form.get('asset_name', '').strip()
    asset_type = request.form.get('asset_type', '').strip()
    ticker_symbol = request.form.get('ticker_symbol', '').strip().upper()
    quantity = request.form.get('quantity', '').strip()
    purchase_price = request.form.get('purchase_price', '').strip()
    purchase_date = request.form.get('purchase_date', '').strip()
    current_price = request.form.get('current_price', '').strip()
    notes = request.form.get('notes', '').strip()
    
    # Validation
    errors = []
    
    if not asset_name:
        errors.append('Asset name is required.')
    
    if not quantity:
        errors.append('Quantity is required.')
    else:
        try:
            quantity_float = float(quantity)
            if quantity_float <= 0:
                errors.append('Quantity must be greater than 0.')
        except ValueError:
            errors.append('Quantity must be a valid number.')
    
    if not purchase_price:
        errors.append('Purchase price is required.')
    else:
        try:
            purchase_price_float = float(purchase_price)
            if purchase_price_float <= 0:
                errors.append('Purchase price must be greater than 0.')
        except ValueError:
            errors.append('Purchase price must be a valid number.')
    
    if current_price:
        try:
            current_price_float = float(current_price)
            if current_price_float < 0:
                errors.append('Current price cannot be negative.')
        except ValueError:
            errors.append('Current price must be a valid number.')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('investments.index'))
    
    # Update investment
    db.execute(
        '''UPDATE investments 
           SET asset_name = ?, asset_type = ?, ticker_symbol = ?, 
               quantity = ?, purchase_price = ?, purchase_date = ?, 
               current_price = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ?''',
        (asset_name, asset_type, ticker_symbol or None, float(quantity), 
         float(purchase_price), purchase_date, 
         float(current_price) if current_price else None, notes or None,
         id, g.user['id'])
    )
    db.commit()
    
    flash(f'✅ Investment "{asset_name}" updated successfully!', 'success')
    return redirect(url_for('investments.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an investment"""
    db = get_db()
    
    # Get the investment and verify ownership
    investment = db.execute(
        'SELECT asset_name FROM investments WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not investment:
        flash('Investment not found.', 'danger')
        return redirect(url_for('investments.index'))
    
    # Delete the investment
    db.execute('DELETE FROM investments WHERE id = ? AND user_id = ?', (id, g.user['id']))
    db.commit()
    
    flash(f'Investment "{investment["asset_name"]}" deleted successfully.', 'info')
    return redirect(url_for('investments.index'))

@bp.route('/<int:id>/update-price', methods=['POST'])
@login_required
def update_price(id):
    """Update current price for an investment"""
    db = get_db()
    
    investment = db.execute(
        'SELECT * FROM investments WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not investment:
        return jsonify({'success': False, 'error': 'Investment not found'}), 404
    
    current_price = request.json.get('current_price')
    
    if not current_price:
        return jsonify({'success': False, 'error': 'Current price is required'}), 400
    
    try:
        current_price_float = float(current_price)
        if current_price_float < 0:
            return jsonify({'success': False, 'error': 'Price cannot be negative'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid price format'}), 400
    
    db.execute(
        'UPDATE investments SET current_price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
        (current_price_float, id, g.user['id'])
    )
    db.commit()
    
    # Calculate new gain/loss
    quantity = investment['quantity']
    purchase_price = investment['purchase_price']
    total_cost = quantity * purchase_price
    current_value = quantity * current_price_float
    gain_loss = current_value - total_cost
    gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return jsonify({
        'success': True,
        'current_price': current_price_float,
        'current_value': current_value,
        'gain_loss': gain_loss,
        'gain_loss_pct': gain_loss_pct
    })

# Helper functions
def calculate_portfolio_stats(investments):
    """Calculate portfolio statistics"""
    if not investments:
        return {
            'total_invested': 0,
            'current_value': 0,
            'total_gain_loss': 0,
            'total_gain_loss_pct': 0,
            'num_investments': 0
        }
    
    total_invested = 0
    current_value = 0
    
    for inv in investments:
        total_cost = inv['quantity'] * inv['purchase_price']
        total_invested += total_cost
        
        if inv['current_price']:
            current_value += inv['quantity'] * inv['current_price']
        else:
            current_value += total_cost  # Use purchase price if current price not set
    
    total_gain_loss = current_value - total_invested
    total_gain_loss_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
    
    return {
        'total_invested': round(total_invested, 2),
        'current_value': round(current_value, 2),
        'total_gain_loss': round(total_gain_loss, 2),
        'total_gain_loss_pct': round(total_gain_loss_pct, 2),
        'num_investments': len(investments)
    }

def calculate_asset_allocation(investments):
    """Calculate asset allocation by type"""
    allocation = {}
    total_value = 0
    
    for inv in investments:
        asset_type = inv['asset_type']
        value = inv['quantity'] * (inv['current_price'] or inv['purchase_price'])
        
        if asset_type not in allocation:
            allocation[asset_type] = {
                'value': 0,
                'count': 0,
                'icon': inv.get('icon', 'fa-circle'),
                'color': inv.get('color', '#95a5a6')
            }
        
        allocation[asset_type]['value'] += value
        allocation[asset_type]['count'] += 1
        total_value += value
    
    # Calculate percentages
    for asset_type in allocation:
        allocation[asset_type]['percentage'] = round(
            (allocation[asset_type]['value'] / total_value * 100) if total_value > 0 else 0, 2
        )
        allocation[asset_type]['value'] = round(allocation[asset_type]['value'], 2)
    
    return allocation

def get_top_performers(investments, limit=5):
    """Get top performing investments"""
    performers = []
    
    for inv in investments:
        if inv['current_price']:
            total_cost = inv['quantity'] * inv['purchase_price']
            current_value = inv['quantity'] * inv['current_price']
            gain_loss = current_value - total_cost
            gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            performers.append({
                'id': inv['id'],
                'asset_name': inv['asset_name'],
                'ticker_symbol': inv['ticker_symbol'],
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct,
                'current_value': current_value,
                'icon': inv.get('icon'),
                'color': inv.get('color')
            })
    
    # Sort by percentage gain/loss
    performers.sort(key=lambda x: x['gain_loss_pct'], reverse=True)
    
    return performers[:limit]