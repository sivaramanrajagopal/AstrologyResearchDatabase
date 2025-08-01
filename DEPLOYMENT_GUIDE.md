# 🚀 Deployment Guide

## 📋 Pre-deployment Checklist

### ✅ Code Status
- [x] **Git Repository**: Code is committed and pushed to GitHub
- [x] **Requirements**: All dependencies listed in `requirements.txt`
- [x] **Environment Variables**: Configuration ready
- [x] **Database**: Supabase schema deployed
- [x] **API Keys**: Google Maps API key configured

### 🔧 Required Environment Variables
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
SECRET_KEY=your_flask_secret_key
```

## 🌟 Recommended: Render Deployment

### Why Render?
- **✅ Flask Support**: Native Python/Flask support
- **✅ Database Integration**: Easy Supabase integration
- **✅ Environment Variables**: Simple configuration
- **✅ Auto-deploy**: Automatic deployment on git push
- **✅ Free Tier**: Generous free tier available

### Deployment Steps

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `sivaramanrajagopal/AstrologyResearchDatabase`

3. **Configure Service**
   ```
   Name: astrology-research-database
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app_global:app
   ```

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add all required environment variables:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `GOOGLE_MAPS_API_KEY`
     - `SECRET_KEY`

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy

### Render Configuration File
The `render.yaml` file is already configured for automatic deployment.

## ⚡ Alternative: Vercel Deployment

### Why Vercel?
- **✅ Fast Deployment**: Very quick deployment times
- **✅ Edge Network**: Global CDN
- **✅ Git Integration**: Automatic deployments
- **✅ Free Tier**: Generous free tier

### Deployment Steps

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app_global.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app_global.py"
       }
     ]
   }
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables**
   - Go to Vercel dashboard
   - Navigate to your project
   - Go to "Settings" → "Environment Variables"
   - Add all required variables

## 🔍 Post-Deployment Checklist

### ✅ Application Health
- [ ] **Homepage loads**: Check main page accessibility
- [ ] **Database connection**: Verify Supabase connectivity
- [ ] **API functionality**: Test location autocomplete
- [ ] **Form submissions**: Test adding new birth charts
- [ ] **Chart calculations**: Verify planetary calculations

### ✅ Performance Testing
- [ ] **Page load times**: Under 3 seconds
- [ ] **Database queries**: Efficient Supabase queries
- [ ] **API responses**: Google Maps API working
- [ ] **Mobile responsiveness**: Test on mobile devices

### ✅ Security Checklist
- [ ] **Environment variables**: All secrets properly configured
- [ ] **API keys**: Restricted to necessary domains
- [ ] **HTTPS**: SSL certificate active
- [ ] **Input validation**: Forms properly validated

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check requirements.txt
   pip install -r requirements.txt
   
   # Verify Python version
   python --version
   ```

2. **Environment Variables**
   - Ensure all variables are set in deployment platform
   - Check variable names match exactly
   - Verify API keys are valid

3. **Database Connection**
   - Verify Supabase URL and key
   - Check database schema is deployed
   - Test connection manually

4. **API Issues**
   - Verify Google Maps API key
   - Check API quotas and billing
   - Test API endpoints manually

## 📊 Monitoring

### Render Monitoring
- **Logs**: Available in Render dashboard
- **Metrics**: Built-in performance monitoring
- **Alerts**: Configure for downtime

### Vercel Monitoring
- **Analytics**: Built-in analytics
- **Functions**: Serverless function monitoring
- **Performance**: Core Web Vitals tracking

## 🔄 Continuous Deployment

### Automatic Deployments
- **Render**: Automatic on git push to main branch
- **Vercel**: Automatic on git push to main branch

### Manual Deployments
```bash
# Render (via dashboard)
# Vercel
vercel --prod
```

## 📞 Support

### Render Support
- [Documentation](https://render.com/docs)
- [Community](https://community.render.com)

### Vercel Support
- [Documentation](https://vercel.com/docs)
- [Community](https://github.com/vercel/vercel/discussions)

---

**🎉 Your Global Astrology Research Database is ready for deployment!** 