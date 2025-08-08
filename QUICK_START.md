# 🚀 Quick Start Guide - Crypto Hedge Fund Dashboard

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+**
- **Docker & Docker Compose**
- **Git**
- **AWS CLI** (for deployment)
- **Terraform** (for deployment)

## 🏃‍♂️ Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd cryptoDashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
# Add your API keys and database settings
```

### 3. Run with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:8501
```

### 4. Run Locally (Alternative)

```bash
# Start Redis and PostgreSQL manually, then:
streamlit run app/main.py
```

## ☁️ AWS Deployment

### 1. AWS Setup

```bash
# Configure AWS CLI
aws configure

# Set your AWS credentials and region
```

### 2. Deploy Infrastructure

```bash
# Make deployment script executable
chmod +x deployment/scripts/deploy.sh

# Deploy to AWS
./deployment/scripts/deploy.sh deploy
```

### 3. Access Your Dashboard

After successful deployment, you'll get a URL like:
```
http://your-alb-dns-name.us-east-1.elb.amazonaws.com
```

## 📊 Dashboard Features

### **Main Dashboard**
- Real-time portfolio NAV and P&L
- Key risk metrics (VaR, Sharpe ratio)
- Asset allocation visualization
- Market overview and alerts

### **Real-Time Monitor**
- Live price feeds from multiple exchanges
- Portfolio position tracking
- Data quality indicators
- Performance metrics

### **Portfolio Analytics**
- Performance attribution analysis
- Return decomposition
- Asset correlation analysis
- Historical performance trends

### **Risk Management**
- VaR calculations (parametric, historical, Monte Carlo)
- Stress testing scenarios
- Risk metrics dashboard
- Position-level risk assessment

### **Data Quality**
- Multi-source data validation
- Anomaly detection
- Data freshness monitoring
- Quality scoring and reporting

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BINANCE_API_KEY` | Binance API key | - |
| `BINANCE_SECRET_KEY` | Binance secret key | - |
| `COINGECKO_API_KEY` | CoinGecko API key | - |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///crypto_dashboard.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `DEBUG` | Enable debug mode | `False` |
| `UPDATE_INTERVAL` | Data update frequency (seconds) | `60` |

### Risk Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `VAR_CONFIDENCE_LEVEL` | VaR confidence level | `0.95` |
| `VAR_TIME_HORIZON` | VaR time horizon (days) | `1` |
| `PRICE_DEVIATION_THRESHOLD` | Price validation threshold | `0.05` |
| `DATA_FRESHNESS_THRESHOLD` | Data staleness threshold (seconds) | `300` |

## 🛠️ Development

### Project Structure

```
cryptoDashboard/
├── app/                    # Main application code
│   ├── main.py            # Streamlit entry point
│   ├── components/        # UI components
│   ├── data/              # Data processing modules
│   └── utils/             # Utility functions
├── deployment/            # Deployment configuration
│   ├── terraform/         # Infrastructure as code
│   └── scripts/           # Deployment scripts
├── data/                  # Data storage
├── tests/                 # Unit tests
└── requirements.txt       # Python dependencies
```

### Adding New Features

1. **New Data Source**: Add to `app/data/data_collectors.py`
2. **New Risk Metric**: Extend `app/data/risk_calculators.py`
3. **New Dashboard Page**: Create in `app/main.py`
4. **New Validation Rule**: Add to `app/data/data_validators.py`

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_data_validators.py
```

## 📈 Monitoring & Alerts

### Local Monitoring

```bash
# View logs
docker-compose logs -f crypto-dashboard

# Monitor resources
docker stats
```

### AWS Monitoring

- **CloudWatch**: Application metrics and logs
- **ECS**: Container health and performance
- **RDS**: Database performance monitoring
- **ElastiCache**: Redis performance metrics

### Health Checks

The application includes health check endpoints:
- `/_stcore/health` - Streamlit health check
- `/health` - Application health check

## 🔒 Security Considerations

### Local Development
- Use environment variables for sensitive data
- Don't commit API keys to version control
- Use strong passwords for local databases

### AWS Deployment
- IAM roles with minimal required permissions
- Security groups restricting access
- Encrypted data at rest and in transit
- Regular security updates

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

2. **Database connection failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   ```

3. **API rate limits**
   ```bash
   # Check API usage in logs
   docker-compose logs crypto-dashboard | grep "rate limit"
   ```

4. **Memory issues**
   ```bash
   # Increase Docker memory limit
   # Or optimize data processing
   ```

### Getting Help

1. Check the logs: `docker-compose logs crypto-dashboard`
2. Review configuration in `.env`
3. Verify API keys and permissions
4. Check network connectivity

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform Documentation](https://www.terraform.io/docs/)
- [Python Binance API](https://python-binance.readthedocs.io/)

## 🎯 Next Steps

1. **Customize the dashboard** for your specific needs
2. **Add real API keys** for live data feeds
3. **Implement user authentication** for production use
4. **Add more risk models** and analytics features
5. **Set up automated monitoring** and alerting

---

**Happy Trading! 📈** 