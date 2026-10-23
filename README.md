# 🛒 Superstore Sales Dashboard

## Project Overview
An interactive data visualization dashboard built with Plotly Dash to analyze
the sales performance of a retail superstore across multiple regions in the US.

---

## Dataset
- **Name:** Sample Superstore Dataset
- **Source:** https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
- **File:** Sample - Superstore.csv
- **Size:** 9,994 rows × 21 columns
- **Key Columns:** Sales, Profit, Discount, Category, Region, Segment, Ship Mode, Order Date

---

## Dashboard Features
The dashboard includes 13 interactive charts across 4 tabs:

### 📊 Comparison Tab
- Column Chart: Total Sales by Category
- Bar Chart: Total Profit by Sub-Category
- Stacked Column Chart: Sales by Region and Category
- Stacked Bar Chart: Orders by Segment and Ship Mode
- Clustered Column Chart: Sales vs Profit by Category
- Clustered Bar Chart: Sales vs Profit by Region

### 🔗 Relationship Tab
- Scatter Chart: Discount vs Profit
- Bubble Chart: Sales vs Profit vs Quantity

### 📈 Distribution Tab
- Histogram: Distribution of Sales
- Box Chart: Profit Distribution by Category
- Violin Chart: Sales Distribution by Region

### 📅 Time-Series Tab
- Line Chart: Monthly Sales Trend
- Area Chart: Monthly Profit Trend

---

## Interactive Elements
- **Region Filter:** Filter data by region (All / East / West / Central / South)
- **Category Filter:** Filter data by category (All / Furniture / Technology / Office Supplies)
- **Year Range Slider:** Filter data by year range (2014 - 2017)

---

## Project Structure
```
Superstore_Dashboard/
├── app.py                        # Main Dash application
├── data/
│   ├── raw_data.csv              # Original dataset
│   └── cleaned_data.csv         # Processed dataset
├── notebooks/
│   └── preprocessing.ipynb      # Data cleaning notebook
├── assets/
│   └── style.css                # Custom CSS
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies
```

---

## How to Run
1. Clone or download the project
2. Open terminal in the project folder
3. Inspip install plotly pandas numpy jupyter openpyxltall dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the dashboard:
   ```
   python app_edit.py
   
   ```
5. Open your browser and go to: **http://127.0.0.1:8050/**
```

