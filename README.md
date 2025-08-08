# Crypto Hedge Fund Analytics Dashboard

A comprehensive real-time analytics dashboard for crypto hedge fund operations, demonstrating data accuracy, portfolio performance analysis, and risk management capabilities.

## 🎯 Project Overview

This POC showcases advanced data & analytics capabilities for crypto hedge fund operations, including:

- **Data Oversight & Accuracy**: Real-time data validation, multi-source reconciliation, and anomaly detection
- **Portfolio Performance & Risk Analysis**: P&L tracking, performance attribution, risk metrics, and stress testing
- **Optimization & Research**: Portfolio optimization, capital efficiency analysis, and rebalancing recommendations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Processing    │    │   Dashboard     │
│                 │    │                 │    │                 │
│ • Binance API   │───▶│ • Data Validation│───▶│ • Streamlit UI  │
│ • Coinbase API  │    │ • Risk Calc     │    │ • Real-time     │
│ • CoinGecko API │    │ • Performance   │    │ • Multi-page    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Storage       │
                       │                 │
                       │ • PostgreSQL    │
                       │ • Redis         │
                       │ • Azure Storage │
                       └─────────────────┘
```

## 🚀 Features

### Data Oversight & Accuracy
- ✅ Real-time data validation and quality checks
- ✅ Multi-source data reconciliation
- ✅ Automated anomaly detection
- ✅ Data lineage tracking
- ✅ Position reconciliation dashboard

### Portfolio Performance & Risk Analysis
- ✅ Real-time P&L tracking
- ✅ Performance attribution analysis
- ✅ Risk metrics (VaR, Sharpe ratio, drawdown)
- ✅ Factor exposure analysis
- ✅ Stress testing scenarios

### Optimization & Research
- ✅ Portfolio optimization suggestions
- ✅ Capital efficiency analysis
- ✅ Return driver decomposition
- ✅ Rebalancing recommendations

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Azure Account (for production deployment)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/danielchancfa/crypto-dashboard.git
cd cryptoDashboard
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Run the application**
```bash
streamlit run app/main.py
```

### Docker Deployment

```bash
docker-compose up -d
```

## 🚀 Production Deployment

### Azure Deployment (Recommended)

For production deployment to Azure with enterprise-grade infrastructure:

1. **Quick Deployment**
```bash
# Copy configuration
cp deployment/azure/terraform.tfvars.example deployment/azure/terraform.tfvars

# Edit configuration with your values
nano deployment/azure/terraform.tfvars

# Run automated deployment
./deployment/azure/deploy.sh
```

2. **Detailed Guide**
   - 📖 [Azure Deployment Guide](AZURE_DEPLOYMENT.md)
   - 📋 [Deployment Checklist](deployment/azure/CHECKLIST.md)
   - 🔧 [Manual Deployment Steps](deployment/azure/README.md)

### AWS Deployment

For AWS deployment (legacy):

```bash
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

## 📊 Dashboard Pages

1. **Real-Time Monitor**: Live price feeds, P&L tracking, and market overview
2. **Portfolio Analytics**: Performance attribution, return analysis, and optimization
3. **Risk Management**: VaR calculations, stress testing, and risk metrics
4. **Data Quality**: Data validation, reconciliation, and anomaly detection

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
COINBASE_API_KEY=your_coinbase_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_dashboard
REDIS_URL=redis://localhost:6379

# Azure Configuration (for production)
AZURE_STORAGE_ACCOUNT=your_storage_account
AZURE_STORAGE_KEY=your_storage_key
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_data_validators.py
```

## 🚀 Deployment Options

### Azure (Production-Ready)
- ✅ Enterprise-grade infrastructure
- ✅ Financial industry compliance
- ✅ Auto-scaling and high availability
- ✅ Comprehensive monitoring and alerting
- ✅ Cost optimization and management

### AWS (Legacy)
- ✅ Cloud-native architecture
- ✅ Scalable infrastructure
- ✅ Managed services integration

### Local Development
- ✅ Quick setup and testing
- ✅ Docker containerization
- ✅ Development-friendly environment

## 📈 Key Metrics Tracked

- **Portfolio Metrics**: NAV, P&L, Sharpe Ratio, Maximum Drawdown
- **Risk Metrics**: VaR (95%, 99%), Expected Shortfall, Beta
- **Performance Metrics**: Alpha, Information Ratio, Tracking Error
- **Data Quality Metrics**: Data freshness, accuracy, completeness

## 🔒 Security Features

- API key encryption and secure storage
- Data validation and sanitization
- Rate limiting and API quota management
- Audit logging for all data operations
- Network security groups and firewalls
- Encrypted storage and communications

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or support, please open an issue in the repository.

## 🎯 Success Metrics

This project demonstrates:

- ✅ **Technical Excellence**: Enterprise-grade infrastructure and architecture
- ✅ **Data Accuracy**: Multi-source validation and reconciliation
- ✅ **Real-time Capabilities**: Live streaming and monitoring
- ✅ **Risk Management**: Comprehensive risk analysis and metrics
- ✅ **Scalability**: Auto-scaling and performance optimization
- ✅ **Security**: Financial-grade security measures
- ✅ **Compliance**: Industry-standard compliance and audit trails

Perfect for showcasing your capabilities as a **Data and Analytics Manager** for crypto hedge fund operations!
