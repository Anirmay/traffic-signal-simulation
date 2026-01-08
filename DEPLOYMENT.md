# 🚀 Deployment & Configuration Guide

## Quick Links
- **Local Demo**: Run `streamlit run app.py` → http://localhost:8501
- **Test Suite**: Run `python demo.py` (validates all logic)
- **Streamlit Cloud**: https://streamlit.io/cloud

---

## OPTION 1: Run Locally (Recommended for Development)

### One-Command Setup
```bash
cd "Adaptive Traffic Signal Simulation"
pip install -r requirements.txt
streamlit run app.py
```

**Browser Opens Automatically** to `http://localhost:8501`

### Using Command Line on Windows
```cmd
# Navigate to project
cd C:\Users\HP\Desktop\Programming\"Adaptive Traffic Signal Simulation"

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Using PowerShell
```powershell
cd "C:\Users\HP\Desktop\Programming\Adaptive Traffic Signal Simulation"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

---

## OPTION 2: Deploy to Streamlit Cloud (Free, Public URL)

### Prerequisites
- GitHub account (free)
- Streamlit.io account (free)

### Step-by-Step Deployment

#### 1️⃣ Create GitHub Repository

```bash
# Inside project directory
git init
git add .
git commit -m "Initial commit: AI-Based Adaptive Traffic Signal Simulation"
```

Then on GitHub.com:
1. Create new repository: `traffic-signal-sim`
2. Run these commands:
```bash
git remote add origin https://github.com/YOUR_USERNAME/traffic-signal-sim.git
git branch -M main
git push -u origin main
```

#### 2️⃣ Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click **"New app"** button
3. Fill in:
   - **GitHub account**: Select your account
   - **Repository**: `traffic-signal-sim`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Deploy**

Streamlit will:
- ✓ Read `requirements.txt`
- ✓ Install dependencies
- ✓ Start your app
- ✓ Provide public URL

#### 3️⃣ Share Your Live App

```
Your app is now live at:
https://traffic-signal-sim.streamlit.app
```

**Share this URL with**:
- Hackathon judges
- Project stakeholders
- Demo audiences

---

## OPTION 3: Deploy to AWS (More Powerful)

### Using AWS Lightsail

```bash
# 1. Create Lightsail instance (Ubuntu 20.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip

# 4. Clone repository
git clone https://github.com/YOUR_USERNAME/traffic-signal-sim.git
cd traffic-signal-sim

# 5. Install Python packages
pip3 install -r requirements.txt

# 6. Run with Streamlit
streamlit run app.py --server.port 80 --server.headless true
```

---

## OPTION 4: Deploy to Heroku

### Setup

```bash
# 1. Install Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create traffic-signal-sim

# 4. Add buildpacks
heroku buildpacks:set heroku/python

# 5. Create Procfile
echo "web: streamlit run app.py --logger.level=error --server.port \$PORT" > Procfile

# 6. Deploy
git push heroku main
```

---

## Configuration Options

### Modify Signal Timing

Edit `logic.py`:

```python
# Change these values in TrafficSignalController.__init__()

self.min_green_time = 10      # Minimum green light (seconds)
self.max_green_time = 60      # Maximum green light (seconds)
self.base_green_time = 20     # Base cycle time (seconds)
```

**Example**: For slower traffic (highways)
```python
self.min_green_time = 15
self.max_green_time = 90
self.base_green_time = 30
```

### Change Update Frequency

Edit `app.py` (around line 380):

```python
# Current: 3 seconds between signal changes
time.sleep(3)  # Change this value

# For faster simulation (1 second)
time.sleep(1)

# For slower simulation (5 seconds)
time.sleep(5)
```

### Adjust Vehicle Input Range

Edit `app.py` (around line 125):

```python
# Current: 0-100 vehicles with 5-step increments
count = st.sidebar.slider(..., max_value=100, step=5)

# For 0-200 vehicles with 10-step increments
count = st.sidebar.slider(..., max_value=200, step=10)
```

### Customize Colors

Edit `app.py` color mapping section:

```python
color_mapping = {
    'RED': '#ff6b6b',      # Red
    'GREEN': '#51cf66',    # Green
    'YELLOW': '#ffd43b'    # Yellow
}

# Change to custom colors:
color_mapping = {
    'RED': '#FF0000',      # Pure red
    'GREEN': '#00FF00',    # Pure green
    'YELLOW': '#FFFF00'    # Pure yellow
}
```

---

## Environment Variables (Optional)

For production, create `.env` file:

```env
# .env (create in project root)
LOG_LEVEL=WARNING
DEBUG_MODE=false
AUTO_RELOAD=false
```

Then access in code:
```python
import os
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

---

## Performance Tuning

### For High Traffic Simulation

```python
# In app.py, increase update interval
time.sleep(5)  # Slower updates = less CPU

# Reduce chart refresh frequency
if st.session_state.update_counter % 2 == 0:
    st.pyplot(fig)  # Update every 2 cycles
```

### For Real-Time Operations

```python
# Decrease sleep time
time.sleep(0.5)  # Faster updates = more responsive

# Use Streamlit's caching
@st.cache_data
def expensive_calculation():
    return controller.get_statistics()
```

---

## Security Considerations

### For Production Deployment

1. **Hide sensitive data**:
   ```python
   # Use environment variables, not hardcoded values
   API_KEY = os.getenv('API_KEY')
   ```

2. **Enable HTTPS**:
   - Streamlit Cloud does this automatically ✓
   - AWS/Heroku: Configure SSL certificates

3. **Add authentication** (if needed):
   ```python
   import streamlit_authenticator as stauth
   # Add login mechanism
   ```

4. **Rate limiting**:
   ```python
   # Prevent abuse of simulation controls
   time.sleep(1)  # Add delay between updates
   ```

---

## Monitoring & Logging

### Local Development Logging

```python
# Add to app.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Current state: {signal_state}")
logger.info(f"Simulation cycle: {cycle_counter}")
```

### Streamlit Cloud Logs

View logs in Streamlit Cloud dashboard:
1. Go to app settings
2. Click "Manage app"
3. View "Logs" tab

---

## Troubleshooting Deployment

### Problem: "requirements.txt not found"
```bash
# Ensure file is in root directory
ls requirements.txt  # Should exist

# If not, create it
pip freeze > requirements.txt
```

### Problem: "ModuleNotFoundError"
```bash
# Check all imports are in requirements.txt
# Add missing packages:
pip install <package_name>
pip freeze > requirements.txt
```

### Problem: "App takes too long to start"
```bash
# Reduce startup time:
# 1. Remove unnecessary imports
# 2. Use streamlit caching
# 3. Lazy load heavy libraries

@st.cache_resource
def load_model():
    return YourModel()
```

### Problem: "Session state not persisting"
```python
# Always initialize in session_state
if 'controller' not in st.session_state:
    st.session_state.controller = TrafficSignalController()
```

---

## Scaling the Application

### For Multiple Intersections

```python
# Create multiple controllers
intersections = {
    'Junction_1': TrafficSignalController(),
    'Junction_2': TrafficSignalController(),
    'Junction_3': TrafficSignalController(),
}

# Coordinate them
for junction, controller in intersections.items():
    state = controller.get_signal_state()
    # Display or process
```

### For Database Integration

```python
# Add to requirements.txt
# sqlite3 (built-in)
# or: sqlalchemy, psycopg2, firebase-admin

# Store simulation data
import sqlite3
conn = sqlite3.connect('traffic_data.db')
# Save signal states and statistics
```

---

## Performance Benchmarks

| Configuration | Load Time | Memory | Suitable For |
|---|---|---|---|
| Local (Laptop) | <1s | 50MB | Development, Demo |
| Streamlit Cloud | 5-10s | 512MB | Public sharing |
| AWS t2.micro | 2-3s | 1GB | Production |
| Heroku Free | 30s | 512MB | Budget deployment |

---

## Maintenance Checklist

- [ ] Update Streamlit monthly: `pip install --upgrade streamlit`
- [ ] Monitor Streamlit Cloud usage (free tier: 3 concurrent users)
- [ ] Backup repository on GitHub
- [ ] Test locally before pushing changes
- [ ] Document any customizations made
- [ ] Update requirements.txt after adding packages

---

## Support Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **GitHub**: https://github.com/streamlit/streamlit
- **Issues**: Create GitHub issues for bugs/features
- **Community**: https://discuss.streamlit.io

---

## Summary

| Method | Setup Time | Cost | Best For |
|--------|-----------|------|----------|
| **Local** | 2 min | Free | Development |
| **Streamlit Cloud** | 5 min | Free | Quick demos |
| **AWS** | 15 min | ~$5/month | Production |
| **Heroku** | 10 min | Free/Paid | Side projects |

**Recommended**: Start with **Streamlit Cloud** for hackathon evaluation!

---

*Last Updated: January 8, 2026*
*Version: 1.0*
