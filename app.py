from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import csv
import io
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///birthcharts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import Swiss Ephemeris utilities
from swiss_ephemeris_utils import calculate_planetary_positions, format_planetary_positions, get_planet_summary

# Database Model
class BirthChart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    time_of_birth = db.Column(db.Time, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    research_category = db.Column(db.String(100), nullable=False)
    researcher_id = db.Column(db.String(50), nullable=False)
    additional_notes = db.Column(db.Text)
    planetary_positions = db.Column(db.Text)  # JSON string of planetary positions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Research categories
RESEARCH_CATEGORIES = [
    'Business Success',
    'Medical Conditions (Autism)',
    'Medical Conditions (ADHD)',
    'Medical Conditions (Other)',
    'IT/Technology Careers',
    'Creative Arts',
    'Sports/Athletics',
    'Education/Academia',
    'Relationships/Marriage',
    'Health/Wellness',
    'Spiritual/Religious',
    'Other'
]

@app.route('/')
def index():
    total_charts = BirthChart.query.count()
    category_counts = db.session.query(
        BirthChart.research_category,
        db.func.count(BirthChart.id)
    ).group_by(BirthChart.research_category).all()
    
    return render_template('index.html', 
                         total_charts=total_charts,
                         category_counts=category_counts,
                         categories=RESEARCH_CATEGORIES)

@app.route('/add', methods=['GET', 'POST'])
def add_birth_chart():
    if request.method == 'POST':
        try:
            # Parse form data
            name = request.form['name'].strip()
            gender = request.form['gender']
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            time_of_birth = datetime.strptime(request.form['time_of_birth'], '%H:%M').time()
            city = request.form['city'].strip()
            country = request.form['country'].strip()
            research_category = request.form['research_category']
            researcher_id = request.form['researcher_id'].strip()
            additional_notes = request.form['additional_notes'].strip()
            
            # Basic validation
            if not all([name, city, country, research_category, researcher_id]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('add_birth_chart'))
            
            # Calculate planetary positions using Swiss Ephemeris
            planetary_positions = {}
            try:
                # Get latitude and longitude from form
                lat = float(request.form.get('latitude', 0))
                lon = float(request.form.get('longitude', 0))
                
                # If coordinates not provided, use defaults
                if lat == 0 and lon == 0:
                    print("Using default coordinates for planetary calculations")
                
                # Calculate planetary positions with IST timezone
                planetary_positions = calculate_planetary_positions(
                    date_of_birth, time_of_birth, lat, lon, 5.5
                )
                
                # Convert to JSON string for storage
                planetary_positions_json = json.dumps(planetary_positions)
                
            except Exception as e:
                print(f"Error calculating planetary positions: {e}")
                planetary_positions_json = "{}"
            
            # Create new birth chart entry
            birth_chart = BirthChart(
                name=name,
                gender=gender,
                date_of_birth=date_of_birth,
                time_of_birth=time_of_birth,
                city=city,
                country=country,
                research_category=research_category,
                researcher_id=researcher_id,
                additional_notes=additional_notes,
                planetary_positions=planetary_positions_json
            )
            
            db.session.add(birth_chart)
            db.session.commit()
            
            flash('Birth chart data added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error adding birth chart: {str(e)}', 'error')
            return redirect(url_for('add_birth_chart'))
    
    return render_template('add_birth_chart.html', categories=RESEARCH_CATEGORIES)

@app.route('/view')
def view_charts():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    category_filter = request.args.get('category', '')
    
    query = BirthChart.query
    if category_filter:
        query = query.filter(BirthChart.research_category == category_filter)
    
    charts = query.order_by(BirthChart.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('view_charts.html', 
                         charts=charts,
                         categories=RESEARCH_CATEGORIES,
                         current_category=category_filter)

@app.route('/export')
def export_data():
    format_type = request.args.get('format', 'csv')
    category_filter = request.args.get('category', '')
    
    query = BirthChart.query
    if category_filter:
        query = query.filter(BirthChart.research_category == category_filter)
    
    charts = query.all()
    
    if format_type == 'csv':
        return export_csv(charts, category_filter)
    else:
        return export_json(charts, category_filter)

def export_csv(charts, category_filter):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Name', 'Gender', 'Date of Birth', 'Time of Birth',
        'City', 'Country', 'Research Category', 'Researcher ID',
        'Additional Notes', 'Created At'
    ])
    
    # Write data
    for chart in charts:
        writer.writerow([
            chart.id, chart.name, chart.gender,
            chart.date_of_birth.strftime('%Y-%m-%d'),
            chart.time_of_birth.strftime('%H:%M'),
            chart.city, chart.country, chart.research_category,
            chart.researcher_id, chart.additional_notes,
            chart.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    filename = f"birthcharts_{category_filter.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

def export_json(charts, category_filter):
    data = []
    for chart in charts:
        data.append({
            'id': chart.id,
            'name': chart.name,
            'gender': chart.gender,
            'date_of_birth': chart.date_of_birth.strftime('%Y-%m-%d'),
            'time_of_birth': chart.time_of_birth.strftime('%H:%M'),
            'city': chart.city,
            'country': chart.country,
            'research_category': chart.research_category,
            'researcher_id': chart.researcher_id,
            'additional_notes': chart.additional_notes,
            'created_at': chart.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    filename = f"birthcharts_{category_filter.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
    
    return jsonify(data), 200, {
        'Content-Disposition': f'attachment; filename={filename}'
    }

@app.route('/chart/<int:chart_id>')
def view_chart_details(chart_id):
    """View detailed planetary positions for a specific birth chart"""
    chart = BirthChart.query.get_or_404(chart_id)
    
    # Parse planetary positions from JSON
    planetary_positions = {}
    if chart.planetary_positions:
        try:
            planetary_positions = json.loads(chart.planetary_positions)
        except:
            planetary_positions = {}
    
    # Format positions for display
    formatted_positions = format_planetary_positions(planetary_positions)
    
    return render_template('chart_details.html',
                         chart=chart,
                         planetary_positions=formatted_positions,
                         raw_positions=planetary_positions)

@app.route('/edit/<int:chart_id>', methods=['GET', 'POST'])
def edit_birth_chart(chart_id):
    """Edit an existing birth chart"""
    chart = BirthChart.query.get_or_404(chart_id)
    
    if request.method == 'POST':
        try:
            # Parse form data
            chart.name = request.form['name'].strip()
            chart.gender = request.form['gender']
            chart.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            chart.time_of_birth = datetime.strptime(request.form['time_of_birth'], '%H:%M').time()
            chart.city = request.form['city'].strip()
            chart.country = request.form['country'].strip()
            chart.research_category = request.form['research_category']
            chart.researcher_id = request.form['researcher_id'].strip()
            chart.additional_notes = request.form['additional_notes'].strip()
            
            # Update coordinates
            chart.latitude = float(request.form.get('latitude', 0))
            chart.longitude = float(request.form.get('longitude', 0))
            
            # Basic validation
            if not all([chart.name, chart.city, chart.country, chart.research_category, chart.researcher_id]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('edit_birth_chart', chart_id=chart_id))
            
            # Recalculate planetary positions with new data
            planetary_positions = {}
            try:
                # Calculate planetary positions with IST timezone
                planetary_positions = calculate_planetary_positions(
                    chart.date_of_birth, chart.time_of_birth, chart.latitude, chart.longitude, 5.5
                )
                
                # Convert to JSON string for storage
                planetary_positions_json = json.dumps(planetary_positions)
                chart.planetary_positions = planetary_positions_json
                
            except Exception as e:
                print(f"Error calculating planetary positions: {e}")
                flash('Warning: Could not recalculate planetary positions.', 'warning')
            
            # Save changes
            db.session.commit()
            
            flash('Birth chart updated successfully!', 'success')
            return redirect(url_for('view_chart_details', chart_id=chart_id))
            
        except Exception as e:
            flash(f'Error updating birth chart: {str(e)}', 'error')
            return redirect(url_for('edit_birth_chart', chart_id=chart_id))
    
    return render_template('edit_birth_chart.html', 
                         chart=chart, 
                         categories=RESEARCH_CATEGORIES)

@app.route('/delete/<int:chart_id>', methods=['POST'])
def delete_birth_chart(chart_id):
    """Delete a birth chart"""
    chart = BirthChart.query.get_or_404(chart_id)
    
    try:
        db.session.delete(chart)
        db.session.commit()
        flash('Birth chart deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting birth chart: {str(e)}', 'error')
    
    return redirect(url_for('view_charts'))

@app.route('/stats')
def statistics():
    total_charts = BirthChart.query.count()
    
    # Category statistics
    category_stats = db.session.query(
        BirthChart.research_category,
        db.func.count(BirthChart.id).label('count')
    ).group_by(BirthChart.research_category).all()
    
    # Gender distribution
    gender_stats = db.session.query(
        BirthChart.gender,
        db.func.count(BirthChart.id).label('count')
    ).group_by(BirthChart.gender).all()
    
    # Researcher contributions
    researcher_stats = db.session.query(
        BirthChart.researcher_id,
        db.func.count(BirthChart.id).label('count')
    ).group_by(BirthChart.researcher_id).order_by(db.func.count(BirthChart.id).desc()).limit(10).all()
    
    return render_template('statistics.html',
                         total_charts=total_charts,
                         category_stats=category_stats,
                         gender_stats=gender_stats,
                         researcher_stats=researcher_stats)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    # os.makedirs('data', exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=8080) 