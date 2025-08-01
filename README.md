# 🌍 Global Astrology Research Database

A comprehensive Flask-based web application for astrological research with global timezone support, accurate planetary calculations, and advanced Vedic astrology features.

## ✨ Features

- **🌍 Global Timezone Support**: Automatic timezone detection for any location worldwide
- **🪐 Accurate Planetary Calculations**: Swiss Ephemeris-based calculations with Lahiri Ayanamsa
- **🧘 Advanced Astrology Features**: Yogas, Shadbala, Planetary Aspects, House Positions
- **📊 Research Database**: Structured categorization for astrological research
- **🔍 Enhanced Chart Analysis**: Detailed planetary positions, Nakshatras, and Rasis
- **⚡ Real-time Calculations**: Dynamic planetary position calculations
- **🌐 Supabase Integration**: Scalable PostgreSQL database backend

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Supabase account
- Google Maps API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sivaramanrajagopal/AstrologyResearchDatabase.git
   cd AstrologyResearchDatabase
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your credentials
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   SECRET_KEY=your_secret_key
   ```

4. **Run the application**
   ```bash
   python app_global.py
   ```

5. **Access the application**
   - Open http://localhost:8080
   - Start adding birth charts with global timezone support

## 🏗️ Architecture

### Core Components
- **`app_global.py`**: Main Flask application with global features
- **`enhanced_swiss_ephemeris.py`**: Advanced Vedic astrology calculations
- **`supabase_config.py`**: Database integration layer
- **`utils/geocoding.py`**: Google Maps integration for location services
- **`category_definitions.py`**: Research categorization system

### Database Schema
- **Personal Information**: Name, gender, birth details
- **Location Data**: Coordinates, timezone, place of birth
- **Planetary Positions**: All 9 planets + Ascendant with detailed calculations
- **Research Categories**: Primary, sub, and specific conditions
- **Enhanced Features**: Houses, Yogas, Shadbala, Aspects

## 🌟 Key Features

### Planetary Calculations
- **Accurate Swiss Ephemeris**: Using Lahiri Ayanamsa
- **Global Timezone Support**: Automatic timezone detection
- **Enhanced Data**: Houses, Yogas, Shadbala, Planetary Aspects
- **Nakshatra Analysis**: Complete Nakshatra and Pada calculations

### Research Database
- **Structured Categories**: Primary, sub, and specific conditions
- **Outcome Tracking**: Success, failure, ongoing status
- **Severity Levels**: Mild, moderate, severe classifications
- **Timing Analysis**: Immediate, short-term, long-term tracking

### User Interface
- **Responsive Design**: Works on desktop and mobile
- **Real-time Validation**: Form validation and error handling
- **Enhanced Charts**: Detailed planetary position displays
- **Edit Functionality**: Full CRUD operations

## 🚀 Deployment

### Render (Recommended)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy automatically on git push

### Vercel
1. Install Vercel CLI
2. Configure for Python/Flask
3. Set environment variables
4. Deploy with `vercel --prod`

## 🔧 Configuration

### Environment Variables
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
SECRET_KEY=your_flask_secret_key
```

### Database Setup
1. Create Supabase project
2. Run the enhanced schema migration
3. Update environment variables
4. Test database connection

## 📊 API Endpoints

- `GET /`: Home page with statistics
- `GET /add`: Add new birth chart form
- `POST /add`: Submit new birth chart
- `GET /view`: View all birth charts
- `GET /chart/<id>`: View specific chart details
- `GET /edit/<id>`: Edit birth chart form
- `POST /edit/<id>`: Update birth chart
- `POST /delete/<id>`: Delete birth chart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Swiss Ephemeris for accurate astronomical calculations
- Supabase for scalable database infrastructure
- Google Maps API for location services
- Vedic astrology community for insights and feedback

---

**Built with ❤️ for astrological research and global accessibility** 