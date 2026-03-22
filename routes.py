from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Expense

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    month = request.args.get('month')  # format: 2025-03
    
    query = Expense.query.filter_by(user_id=user_id)
    
    if month:
        query = query.filter(Expense.date.startswith(month))
    
    expenses = query.order_by(Expense.date.desc()).all()
    
    return jsonify([{
        'id': e.id,
        'amount': e.amount,
        'category': e.category,
        'note': e.note,
        'date': e.date
    } for e in expenses]), 200


@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('amount') or not data.get('category') or not data.get('date'):
        return jsonify({'error': 'Amount, category and date are required'}), 400

    expense = Expense(
        amount=float(data['amount']),
        category=data['category'],
        note=data.get('note', ''),
        date=data['date'],
        user_id=user_id
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({
        'id': expense.id,
        'amount': expense.amount,
        'category': expense.category,
        'note': expense.note,
        'date': expense.date
    }), 201


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()

    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted'}), 200


@expenses_bp.route('/expenses/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    month = request.args.get('month')  # format: 2025-03

    query = Expense.query.filter_by(user_id=user_id)

    if month:
        query = query.filter(Expense.date.startswith(month))

    expenses = query.all()

    total = sum(e.amount for e in expenses)

    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount

    return jsonify({
        'total': round(total, 2),
        'by_category': by_category,
        'count': len(expenses)
    }), 200