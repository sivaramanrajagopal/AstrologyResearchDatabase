#!/usr/bin/env python3
"""
Global Astrology Database with Supabase Integration
Features:
- Global timezone handling
- Google Geocoding integration
- Checkbox-based categorization
- Supabase database storage
- Swiss Ephemeris planetary calculations
"""

# Import environment configuration first
import environment_config

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from datetime import datetime, timezone
import os
import json
import csv
import io
import requests
from typing import Dict, Optional

# Career prediction API (FastAPI) base URL
CAREER_API_URL = os.environ.get('CAREER_API_URL', 'http://127.0.0.1:8000')

# Import our modules
from supabase_config import supabase_manager
from utils.geocoding import get_location_details
from swiss_ephemeris_utils import calculate_planetary_positions_global
from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions, extract_enhanced_planetary_data
from category_definitions import get_category_options, validate_categories, PRIMARY_CATEGORIES, SUB_CATEGORIES, SPECIFIC_CONDITIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Check if Supabase is configured
if not supabase_manager:
    print("Warning: Supabase not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")

@app.route('/')
def index():
    """Home page with statistics"""
    try:
        if supabase_manager:
            stats = supabase_manager.get_statistics()
            total_charts = stats['total_charts']
            category_counts = stats['category_counts']
        else:
            total_charts = 0
            category_counts = {}
        
        return render_template('index_global.html', 
                             total_charts=total_charts,
                             category_counts=category_counts)
    except Exception as e:
        print(f"Error in index: {e}")
        return render_template('index_global.html', 
                             total_charts=0,
                             category_counts={})

@app.route('/add', methods=['GET', 'POST'])
def add_birth_chart():
    """Add new birth chart with global timezone support"""
    if request.method == 'POST':
        try:
            # Parse form data
            name = request.form['name'].strip()
            gender = request.form['gender']
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            # Handle time parsing with both HH:MM and HH:MM:SS formats
            time_str = request.form['time_of_birth']
            try:
                # Try HH:MM format first
                time_of_birth = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                try:
                    # Try HH:MM:SS format
                    time_of_birth = datetime.strptime(time_str, '%H:%M:%S').time()
                except ValueError:
                    flash('Invalid time format. Please use HH:MM or HH:MM:SS format.', 'error')
                    return redirect(url_for('add_birth_chart'))
            
            place_of_birth = request.form['place_of_birth'].strip()
            
            # Get location details using Google Geocoding
            location_details = get_location_details(place_of_birth)
            
            if not location_details:
                flash('Could not find location details. Please check the place name.', 'error')
                return redirect(url_for('add_birth_chart'))
            
            # Parse categories from radio buttons
            primary_category = request.form.get('primary_category')
            sub_category = request.form.get('sub_category')
            specific_condition = request.form.get('specific_condition')
            
            # Validate categories
            is_valid, message = validate_categories(primary_category, sub_category, specific_condition)
            if not is_valid:
                flash(f'Category validation error: {message}', 'error')
                return redirect(url_for('add_birth_chart'))
            
            # Additional fields
            description = request.form.get('description', '').strip()
            outcome = request.form.get('outcome', 'unknown')
            severity = request.form.get('severity', 'unknown')
            timing = request.form.get('timing', 'unknown')
            researcher_id = request.form.get('researcher_id', '').strip()
            consent_given = 'consent_given' in request.form
            anonymize = 'anonymize' in request.form
            
            # Travel-specific fields
            travel_country = request.form.get('travel_country', '').strip()
            travel_city = request.form.get('travel_city', '').strip()
            travel_purpose = request.form.get('travel_purpose', '').strip()
            travel_outcome = request.form.get('travel_outcome', '').strip()
            
            # Calculate enhanced planetary positions with global timezone
            planetary_positions = calculate_enhanced_planetary_positions(
                date_of_birth=date_of_birth,
                time_of_birth=time_of_birth,
                latitude=location_details['latitude'],
                longitude=location_details['longitude'],
                timezone_name=location_details.get('timezone_id')  # Use timezone_id from geocoding
            )
            
            if not planetary_positions:
                flash('Error calculating planetary positions. Please try again.', 'error')
                return redirect(url_for('add_birth_chart'))
            
            # Prepare data for Supabase
            chart_data = {
                # Personal Information
                'name': name,
                'gender': gender,
                'date_of_birth': date_of_birth.isoformat(),
                'time_of_birth': time_of_birth.isoformat(),
                'place_of_birth': place_of_birth,
                'latitude': location_details['latitude'],
                'longitude': location_details['longitude'],
                'timezone_name': location_details.get('timezone_id', 'UTC'),
                
                # Categories
                'primary_category': primary_category,
                'sub_category': sub_category,
                'specific_condition': specific_condition,
                
                # Additional Details
                'description': description,
                'outcome': outcome,
                'severity': severity,
                'timing': timing,
                
                # Travel Specific
                'travel_country': travel_country,
                'travel_city': travel_city,
                'travel_purpose': travel_purpose,
                'travel_outcome': travel_outcome,
                
                # Research Details
                'researcher_id': researcher_id,
                'consent_given': consent_given,
                'anonymize': anonymize,
                'created_by': 'system'
            }
            
            # Add enhanced planetary positions
            chart_data.update(extract_enhanced_planetary_data(planetary_positions))
            
            # Insert into Supabase
            if supabase_manager:
                result = supabase_manager.insert_birth_chart(chart_data)
                if result:
                    flash('Birth chart added successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Error saving to database. Please try again.', 'error')
            else:
                flash('Database not configured. Please check Supabase settings.', 'error')
            
        except Exception as e:
            print(f"Error adding birth chart: {e}")
            flash('Error processing birth chart. Please try again.', 'error')
    
    # Get category options for the form
    category_options = get_category_options()
    return render_template('add_birth_chart_global.html', 
                         category_options=category_options)

@app.route('/export/today')
def export_today_csv():
    """Download CSV of all birth charts added today (UTC date)."""
    if not supabase_manager:
        flash('Database not configured.', 'error')
        return redirect(url_for('index'))
    today = datetime.now(timezone.utc).date()
    charts = supabase_manager.get_charts_created_on_date(today)
    basic = ['id', 'name', 'gender', 'date_of_birth', 'time_of_birth', 'place_of_birth',
             'latitude', 'longitude', 'timezone_name', 'description', 'primary_category', 'sub_category',
             'outcome', 'severity', 'timing', 'created_at', 'updated_at']
    planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
    planet_cols = []
    for p in planets:
        planet_cols.extend([f'{p}_longitude', f'{p}_rasi', f'{p}_rasi_lord', f'{p}_nakshatra', f'{p}_nakshatra_lord', f'{p}_pada', f'{p}_degrees_in_rasi', f'{p}_retrograde'])
    asc_cols = ['ascendant_longitude', 'ascendant_rasi', 'ascendant_rasi_lord', 'ascendant_nakshatra', 'ascendant_nakshatra_lord', 'ascendant_pada', 'ascendant_degrees_in_rasi']
    house_cols = []
    for i in range(1, 13):
        house_cols.extend([f'house_{i}_longitude', f'house_{i}_rasi', f'house_{i}_degrees'])
    all_cols = basic + planet_cols + asc_cols + house_cols

    def safe(v):
        if v is None:
            return ''
        if isinstance(v, bool):
            return 'Y' if v else 'N'
        if isinstance(v, (dict, list)):
            return str(v)[:500]
        return str(v)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(all_cols)
    for row in charts:
        w.writerow([safe(row.get(c)) for c in all_cols])
    buf.seek(0)
    filename = f'charts_added_{today.isoformat()}.csv'
    return Response(buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'})

@app.route('/view')
def view_charts():
    """View all birth charts"""
    try:
        if supabase_manager:
            charts = supabase_manager.get_all_charts(limit=100)
        else:
            charts = []
        
        return render_template('view_charts_global.html', charts=charts, career_api_url=CAREER_API_URL.rstrip('/'))
    except Exception as e:
        print(f"Error viewing charts: {e}")
        return render_template('view_charts_global.html', charts=[], career_api_url=CAREER_API_URL.rstrip('/'))

@app.route('/chart/<int:chart_id>')
def view_chart_details(chart_id):
    """View detailed birth chart with tabbed interface (Chart Details / Dasha / Career)"""
    try:
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)
            if chart:
                # Parse JSON fields if they exist
                if chart.get('yogas'):
                    try:
                        chart['yogas'] = json.loads(chart['yogas'])
                    except:
                        chart['yogas'] = []

                if chart.get('shadbala'):
                    try:
                        chart['shadbala'] = json.loads(chart['shadbala'])
                    except:
                        chart['shadbala'] = {}

                if chart.get('aspects'):
                    try:
                        chart['aspects'] = json.loads(chart['aspects'])
                    except:
                        chart['aspects'] = []

                return render_template('chart_details_tabbed.html', chart=chart)
            else:
                flash('Birth chart not found.', 'error')
        else:
            flash('Database not configured.', 'error')
    except Exception as e:
        print(f"Error viewing chart details: {e}")
        flash('Error loading chart details.', 'error')

    return redirect(url_for('view_charts'))

@app.route('/edit/<int:chart_id>', methods=['GET', 'POST'])
def edit_birth_chart(chart_id):
    """Edit birth chart"""
    try:
        if request.method == 'GET':
            # Get chart details for editing
            if supabase_manager:
                chart = supabase_manager.get_birth_chart(chart_id)
                if chart:
                    return render_template('edit_birth_chart_global.html', 
                                         chart=chart,
                                         category_options=get_category_options())
                else:
                    flash('Birth chart not found.', 'error')
                    return redirect(url_for('view_charts'))
            else:
                flash('Database not configured.', 'error')
                return redirect(url_for('view_charts'))
        
        elif request.method == 'POST':
            # Handle form submission for editing
            try:
                # Parse form data
                name = request.form['name'].strip()
                gender = request.form['gender']
                date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
                
                # Handle time parsing with both HH:MM and HH:MM:SS formats
                time_str = request.form['time_of_birth']
                try:
                    # Try HH:MM format first
                    time_of_birth = datetime.strptime(time_str, '%H:%M').time()
                except ValueError:
                    try:
                        # Try HH:MM:SS format
                        time_of_birth = datetime.strptime(time_str, '%H:%M:%S').time()
                    except ValueError:
                        flash('Invalid time format. Please use HH:MM or HH:MM:SS format.', 'error')
                        return redirect(url_for('edit_birth_chart', chart_id=chart_id))
                
                place_of_birth = request.form['place_of_birth'].strip()
                
                # Get location details using Google Geocoding
                location_details = get_location_details(place_of_birth)
                
                if not location_details:
                    flash('Could not find location details. Please check the place name.', 'error')
                    return redirect(url_for('edit_birth_chart', chart_id=chart_id))
                
                # Parse categories from dropdowns
                primary_category = request.form.get('primary_category')
                sub_category = request.form.get('sub_category')
                specific_condition = request.form.get('specific_condition')
                
                # Validate categories
                is_valid, message = validate_categories(primary_category, sub_category, specific_condition)
                if not is_valid:
                    flash(f'Category validation error: {message}', 'error')
                    return redirect(url_for('edit_birth_chart', chart_id=chart_id))
                
                # Additional fields
                description = request.form.get('description', '').strip()
                outcome = request.form.get('outcome', 'unknown')
                severity = request.form.get('severity', 'unknown')
                timing = request.form.get('timing', 'unknown')
                researcher_id = request.form.get('researcher_id', '').strip()
                consent_given = 'consent_given' in request.form
                anonymize = 'anonymize' in request.form
                
                # Travel-specific fields
                travel_country = request.form.get('travel_country', '').strip()
                travel_city = request.form.get('travel_city', '').strip()
                travel_purpose = request.form.get('travel_purpose', '').strip()
                travel_outcome = request.form.get('travel_outcome', '').strip()
                
                # Calculate enhanced planetary positions with global timezone
                planetary_positions = calculate_enhanced_planetary_positions(
                    date_of_birth=date_of_birth,
                    time_of_birth=time_of_birth,
                    latitude=location_details['latitude'],
                    longitude=location_details['longitude'],
                    timezone_name=location_details['timezone_id']
                )
                
                # Extract enhanced planetary data for Supabase
                planetary_data = extract_enhanced_planetary_data(planetary_positions)
                
                # Prepare data for update
                chart_data = {
                    'name': name,
                    'gender': gender,
                    'date_of_birth': date_of_birth.isoformat(),
                    'time_of_birth': time_of_birth.strftime('%H:%M'),
                    'place_of_birth': place_of_birth,
                    'latitude': location_details['latitude'],
                    'longitude': location_details['longitude'],
                    'timezone_name': location_details['timezone_id'],
                    'primary_category': primary_category,
                    'sub_category': sub_category,
                    'specific_condition': specific_condition,
                    'description': description,
                    'outcome': outcome,
                    'severity': severity,
                    'timing': timing,
                    'researcher_id': researcher_id,
                    'consent_given': consent_given,
                    'anonymize': anonymize,
                    'travel_country': travel_country,
                    'travel_city': travel_city,
                    'travel_purpose': travel_purpose,
                    'travel_outcome': travel_outcome,
                    **planetary_data
                }
                
                # Update in Supabase
                if supabase_manager:
                    success = supabase_manager.update_birth_chart(chart_id, chart_data)
                    if success:
                        flash('Birth chart updated successfully! Note: Planetary positions have been recalculated based on the new data.', 'success')
                    else:
                        flash('Error updating birth chart.', 'error')
                else:
                    flash('Database not configured.', 'error')
                
            except Exception as e:
                print(f"Error updating birth chart: {e}")
                flash('Error updating birth chart. Please try again.', 'error')
            
            return redirect(url_for('view_charts'))
            
    except Exception as e:
        print(f"Error in edit_birth_chart: {e}")
        flash('Error loading chart for editing.', 'error')
        return redirect(url_for('view_charts'))

@app.route('/delete/<int:chart_id>', methods=['POST'])
def delete_birth_chart(chart_id):
    """Delete birth chart"""
    try:
        if supabase_manager:
            success = supabase_manager.delete_birth_chart(chart_id)
            if success:
                flash('Birth chart deleted successfully!', 'success')
            else:
                flash('Error deleting birth chart.', 'error')
        else:
            flash('Database not configured.', 'error')
    except Exception as e:
        print(f"Error deleting chart: {e}")
        flash('Error deleting birth chart.', 'error')
    
    return redirect(url_for('view_charts'))

@app.route('/api/location')
def get_location_api():
    """API endpoint for location autocomplete"""
    place_name = request.args.get('place', '')
    if not place_name:
        return jsonify({'error': 'Place name required'}), 400
    
    try:
        location_details = get_location_details(place_name)
        if location_details:
            return jsonify(location_details)
        else:
            return jsonify({'error': 'Location not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories_api():
    """API endpoint for category options"""
    try:
        return jsonify(get_category_options())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict')
def predict_choose():
    """Choose a chart to run career prediction (Vedic D1/D10 rules)."""
    try:
        if supabase_manager:
            charts = supabase_manager.get_all_charts(limit=500)
        else:
            charts = []
        return render_template('predict_choose.html', charts=charts)
    except Exception as e:
        print(f"Error in predict_choose: {e}")
        return render_template('predict_choose.html', charts=[])


@app.route('/predict/<int:chart_id>')
def predict_career(chart_id):
    """Run career prediction for a chart and show result (calls FastAPI)."""
    try:
        resp = requests.post(
            f'{CAREER_API_URL.rstrip("/")}/career/predict',
            json={'chart_id': chart_id},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)
        # Interpret factors and scores
        from services.factor_interpreter import get_factor_summary

        factor_summary = get_factor_summary(
            data.get('factors', []),
            data.get('scores', {})
        )

        return render_template(
            'predict_result.html',
            chart_id=chart_id,
            chart=chart,
            career_strength=data.get('career_strength'),
            factors=data.get('factors', []),
            scores=data.get('scores', {}),
            factor_summary=factor_summary,
            applied_rules=data.get('applied_rules', []),
            profession_probabilities=data.get('profession_probabilities'),
            dasha_current=data.get('dasha_current'),
            career_api_url=CAREER_API_URL.rstrip('/'),
            error=None,
        )
    except requests.exceptions.RequestException as e:
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                err_msg = e.response.json().get('detail', err_msg)
            except Exception:
                err_msg = e.response.text or err_msg
        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)
        return render_template(
            'predict_result.html',
            chart_id=chart_id,
            chart=chart,
            career_strength=None,
            factors=[],
            scores={},
            applied_rules=[],
            dasha_current=None,
            career_api_url=CAREER_API_URL.rstrip('/'),
            error=err_msg,
        ), (e.response.status_code if hasattr(e, 'response') and e.response is not None else 502)


@app.route('/dasha/<int:chart_id>')
def view_dasha(chart_id):
    """View Vimshottari Dasha calculations for a chart"""
    try:
        # Get chart data
        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)

        if not chart:
            flash('Birth chart not found.', 'error')
            return redirect(url_for('view_charts'))

        # Import Dasha calculator
        from services.dasha_calculator import generate_dasa_table, get_current_dasa_bhukti, generate_dasa_bhukti_table
        from datetime import datetime
        import swisseph as swe

        # Set sidereal mode
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # Parse birth data
        dob_str = chart.get('date_of_birth')
        tob_str = chart.get('time_of_birth')

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        try:
            tob = datetime.strptime(tob_str, '%H:%M').time()
        except:
            tob = datetime.strptime(tob_str, '%H:%M:%S').time()

        # Calculate Julian Day
        dt = datetime.combine(dob, tob)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

        # Get Moon longitude
        moon_lon = chart.get('moon_longitude')
        if not moon_lon:
            flash('Moon longitude not available for Dasha calculation.', 'error')
            return redirect(url_for('view_chart_details', chart_id=chart_id))

        # Calculate Dasha periods
        birth_nakshatra, birth_pada, dasa_table = generate_dasa_table(jd, moon_lon, total_years=120)

        # Get current Dasha/Bhukti
        current_info = get_current_dasa_bhukti(jd, moon_lon)

        # Calculate Bhukti table
        _, _, bhukti_table = generate_dasa_bhukti_table(jd, moon_lon)

        # Filter for current mahadasha bhuktis
        current_dasa_bhuktis = [b for b in bhukti_table if b['maha_dasa'] == current_info['current_dasa']]

        return render_template(
            'dasha_view.html',
            chart=chart,
            birth_nakshatra=birth_nakshatra,
            birth_pada=birth_pada,
            current_info=current_info,
            dasa_table=dasa_table[:20],  # First 20 periods
            current_dasa_bhuktis=current_dasa_bhuktis,
        )

    except Exception as e:
        print(f"Error calculating Dasha: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error calculating Dasha: {str(e)}', 'error')
        return redirect(url_for('view_chart_details', chart_id=chart_id))


@app.route('/dasha/<int:chart_id>/content')
def view_dasha_content(chart_id):
    """Return only Dasha content for AJAX loading (no header/footer)"""
    try:
        # Get chart data
        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)

        if not chart:
            return '<div class="alert alert-danger">Birth chart not found.</div>', 404

        # Import Dasha calculator
        from services.dasha_calculator import generate_dasa_table, get_current_dasa_bhukti, generate_dasa_bhukti_table
        from datetime import datetime
        import swisseph as swe

        # Set sidereal mode
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # Parse birth data
        dob_str = chart.get('date_of_birth')
        tob_str = chart.get('time_of_birth')

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        try:
            tob = datetime.strptime(tob_str, '%H:%M').time()
        except:
            tob = datetime.strptime(tob_str, '%H:%M:%S').time()

        # Calculate Julian Day
        dt = datetime.combine(dob, tob)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

        # Get Moon longitude
        moon_lon = chart.get('moon_longitude')
        if not moon_lon:
            return '<div class="alert alert-danger">Moon longitude not available for Dasha calculation.</div>', 400

        # Calculate Dasha periods
        birth_nakshatra, birth_pada, dasa_table = generate_dasa_table(jd, moon_lon, total_years=120)

        # Get current Dasha/Bhukti
        current_info = get_current_dasa_bhukti(jd, moon_lon)

        # Calculate Bhukti table
        _, _, bhukti_table = generate_dasa_bhukti_table(jd, moon_lon)

        # Filter for current mahadasha bhuktis
        current_dasa_bhuktis = [b for b in bhukti_table if b['maha_dasa'] == current_info['current_dasa']]

        return render_template(
            'partials/_dasha_content.html',
            chart=chart,
            birth_nakshatra=birth_nakshatra,
            birth_pada=birth_pada,
            current_info=current_info,
            dasa_table=dasa_table[:20],  # First 20 periods
            current_dasa_bhuktis=current_dasa_bhuktis,
        )

    except Exception as e:
        print(f"Error calculating Dasha content: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading Dasha data: {str(e)}</div>', 500


@app.route('/predict/<int:chart_id>/content')
def predict_career_content(chart_id):
    """Return only career prediction content for AJAX loading (no header/footer)"""
    try:
        resp = requests.post(
            f'{CAREER_API_URL.rstrip("/")}/career/predict',
            json={'chart_id': chart_id},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)

        # Interpret factors and scores for better display
        from services.factor_interpreter import get_factor_summary

        factor_summary = get_factor_summary(
            data.get('factors', []),
            data.get('scores', {})
        )

        # Return just the career content section
        return render_template(
            'partials/_career_content.html',
            chart_id=chart_id,
            chart=chart,
            career_strength=data.get('career_strength'),
            factors=data.get('factors', []),
            scores=data.get('scores', {}),
            factor_summary=factor_summary,
            applied_rules=data.get('applied_rules', []),
            profession_probabilities=data.get('profession_probabilities'),
            dasha_current=data.get('dasha_current'),
            career_api_url=CAREER_API_URL.rstrip('/'),
            error=None,
        )

    except Exception as e:
        print(f"Error getting career prediction content: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading career prediction: {str(e)}</div>', 500


@app.route('/ashtakavarga/<int:chart_id>/content')
def view_ashtakavarga_content(chart_id):
    """Return Ashtakavarga (BAV/SAV) content for AJAX loading"""
    try:
        # Get chart data from Supabase
        chart = None
        if supabase_manager:
            chart = supabase_manager.get_birth_chart(chart_id)

        if not chart:
            return '<div class="alert alert-danger">Birth chart not found.</div>', 404

        # Calculate planetary positions using enhanced Swiss Ephemeris
        from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions
        from datetime import datetime

        dob_str = chart.get('date_of_birth')
        tob_str = chart.get('time_of_birth')
        lat = chart.get('latitude')
        lon = chart.get('longitude')

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        try:
            tob = datetime.strptime(tob_str, '%H:%M').time()
        except:
            tob = datetime.strptime(tob_str, '%H:%M:%S').time()

        # Get timezone name from chart or default to IST
        timezone_name = chart.get('timezone', 'Asia/Kolkata')

        # Calculate enhanced planetary positions
        d1_positions = calculate_enhanced_planetary_positions(
            date_of_birth=dob,
            time_of_birth=tob,
            latitude=lat,
            longitude=lon,
            timezone_name=timezone_name
        )

        # Calculate Ashtakavarga
        from services.ashtakavarga_service import calculate_ashtakavarga_full

        ashtakavarga_data = calculate_ashtakavarga_full(d1_positions)

        if not ashtakavarga_data:
            return '<div class="alert alert-warning">Unable to calculate Ashtakavarga. Planetary positions may be incomplete.</div>', 400

        # Extract BAV and SAV data for template
        bav_data = ashtakavarga_data.get('bav', {})
        sav_data = ashtakavarga_data.get('sav', {})

        return render_template(
            'partials/_ashtakavarga_content.html',
            chart=chart,
            bav_data=bav_data,
            sav_data=sav_data,
        )

    except Exception as e:
        print(f"Error calculating Ashtakavarga content: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading Ashtakavarga data: {str(e)}</div>', 500


def extract_planetary_data(planetary_positions: Dict) -> Dict:
    """
    Extract planetary data from Swiss Ephemeris results for Supabase storage
    """
    extracted_data = {}
    
    # Define planets to extract
    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Ascendant']
    
    for planet in planets:
        if planet in planetary_positions:
            planet_data = planetary_positions[planet]
            prefix = planet.lower()
            
            extracted_data[f'{prefix}_longitude'] = planet_data.get('longitude', 0)
            extracted_data[f'{prefix}_rasi'] = planet_data.get('rasi', '')
            extracted_data[f'{prefix}_rasi_lord'] = get_rasi_lord(planet_data.get('rasi', ''))
            extracted_data[f'{prefix}_nakshatra'] = planet_data.get('nakshatra', '')
            extracted_data[f'{prefix}_nakshatra_lord'] = planet_data.get('nakshatra_lord', '')
            extracted_data[f'{prefix}_pada'] = planet_data.get('pada', 0)
            extracted_data[f'{prefix}_retrograde'] = planet_data.get('retrograde', False)
            extracted_data[f'{prefix}_degrees_in_rasi'] = planet_data.get('longitude', 0) % 30
    
    return extracted_data

def get_rasi_lord(rasi: str) -> str:
    """
    Get the lord of a rasi (sign)
    """
    rasi_lords = {
        'Mesha': 'Mars',
        'Rishaba': 'Venus', 
        'Mithuna': 'Mercury',
        'Kataka': 'Moon',
        'Simha': 'Sun',
        'Kanni': 'Mercury',
        'Thula': 'Venus',
        'Vrischika': 'Mars',
        'Dhanus': 'Jupiter',
        'Makara': 'Saturn',
        'Kumbha': 'Saturn',
        'Meena': 'Jupiter'
    }
    return rasi_lords.get(rasi, '')

if __name__ == '__main__':
    print("🌍 Starting Global Astrology Database")
    print("=" * 50)
    
    if supabase_manager:
        print("✅ Supabase configured")
    else:
        print("⚠️  Supabase not configured - using demo mode")
    
    app.run(debug=True, host='0.0.0.0', port=8081) 