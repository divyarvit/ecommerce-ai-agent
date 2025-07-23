# 🤖 E-commerce AI Agent

An advanced AI-powered data intelligence platform that transforms natural language questions into actionable business insights. Built with Flask, PostgreSQL, and Google Gemini AI.

##  Features

###  Natural Language Processing
- Ask questions in plain English about your e-commerce data
- Advanced AI converts your questions to SQL automatically
- No technical knowledge required

###  Real-Time Analytics
- Instant data analysis with streaming responses
- Interactive visualizations generated automatically
- Advanced metrics: RoAS, CPC, CTR, conversion rates

###  Modern Interface
- Ultra-modern glass morphism UI design
- Real-time streaming responses with typing effects
- Animated backgrounds with floating particles
- Mobile-responsive design

###  Production-Ready
- PostgreSQL database with connection pooling
- Server-sent events for real-time communication
- Professional error handling and logging
- Scalable architecture

##  Your Data

The system comes loaded with your real e-commerce data:
- **8,779 total records** across three datasets
- **Product Eligibility**: 4,381 records tracking advertising eligibility
- **Ad Sales Metrics**: 3,696 records with advertising performance data
- **Total Sales**: 702 records with overall sales performance

##  Example Questions

Try asking these questions to see the AI in action:

### Revenue Analysis
- "What is my total revenue?"
- "Show me revenue by product"
- "What are my top performing products?"

### Advertising Performance
- "What's my Return on Ad Spend?"
- "Show me CPC by product"
- "Which products have the highest conversion rate?"

### Business Intelligence
- "What percentage of products are eligible for advertising?"
- "Show me trends over time"
- "Compare ad performance vs total sales"

## 🛠️ Quick Start

### Option 1: Local Development

1. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy psycopg2-binary google-genai pandas plotly gunicorn python-dotenv
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

3. **Run setup validation**
   ```bash
   python setup_local.py
   ```

4. **Start the application**
   ```bash
   python main.py
   ```



### Backend Stack
- **Flask**: Web framework with modular design
- **SQLAlchemy**: Database ORM with optimized queries
- **PostgreSQL**: Production database with connection pooling
- **Google Gemini AI**: Natural language to SQL conversion

### Frontend Stack
- **HTML5 + CSS3**: Modern semantic markup
- **JavaScript ES6+**: Real-time streaming interface
- **Bootstrap 5**: Responsive design framework
- **Plotly.js**: Interactive data visualizations

### AI Pipeline
1. **Question Processing**: Natural language input validation
2. **SQL Generation**: AI converts questions to optimized SQL
3. **Database Execution**: Safe query execution with error handling
4. **Response Generation**: AI formats results for user consumption
5. **Streaming Output**: Real-time delivery with typing effects

##  API Integration

### Make API Calls

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is my total revenue?"}'
```

### Response Format

The API returns Server-Sent Events with real-time streaming:

```
data: {"status": "Processing your question..."}
data: {"partial_response": "Your total revenue is "}
data: {"final_response": {"response": "Your total revenue is $1,004,904.56", "sql_query": "SELECT SUM(total_sales)..."}}
```

##  Performance

### Database Optimization
- Indexed columns for fast queries
- Connection pooling for high concurrency
- Optimized SQL generation by AI

### Real-Time Features
- Server-Sent Events for streaming responses
- Non-blocking query execution
- Progressive result loading

### Scalability
- Stateless application design
- Database connection pooling
- Optimized for horizontal scaling


```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
GEMINI_API_KEY=your_gemini_api_key
SESSION_SECRET=your_secret_key
```

##  Sample Insights

Based on your actual data, here are some insights the AI can provide:

### Revenue Metrics
- **Total Revenue**: $1,004,904.56 across all products
- **Average Order Value**: Calculated from units and sales data
- **Revenue Growth**: Trends over time periods

### Advertising Performance
- **Return on Ad Spend (RoAS)**: Revenue per dollar spent
- **Cost Per Click (CPC)**: Advertising efficiency metrics
- **Conversion Rates**: Sales performance by product

### Product Intelligence
- **Eligibility Analysis**: Which products can run ads
- **Top Performers**: Highest converting products
- **Optimization Opportunities**: Underperforming areas

