# Sample Data Files

This directory contains sample data files you can use to test the LLM Data Visualizer.

## Files

### sales_data.csv
Monthly sales data with:
- Sales, Expenses, Profit by month
- Regional breakdown
- Great for line charts, bar charts

**Example prompts:**
- "Show me sales trends over the year"
- "Create a bar chart comparing profit by region"
- "Visualize the relationship between sales and expenses"

### products.json
Product inventory data with:
- Product names, categories, prices, stock levels
- Summary statistics
- Great for pie charts, category analysis

**Example prompts:**
- "Show the distribution of products by category"
- "Create a bar chart of stock levels"
- "Visualize price ranges across categories"

## How to Use

1. Start the Django server
2. Go to http://localhost:8000/
3. Upload one of these files
4. Try the example prompts above
5. Experiment with your own prompts!

## Creating Your Own Data

The visualizer supports:
- **CSV**: Tabular data with headers
- **JSON**: Objects or arrays of objects
- **YAML**: Similar to JSON
- **Excel**: .xlsx or .xls files
- **PDF**: Text extraction (experimental)

### Tips for Best Results

1. **Use clear column names** - helps the AI understand your data
2. **Include numeric data** - needed for most visualizations
3. **Keep it structured** - consistent format throughout
4. **Reasonable size** - start with < 1000 rows for best performance
5. **Multiple columns** - more interesting visualizations

### Sample Prompts That Work Well

- "Create a [chart type] showing [what to visualize]"
- "Compare [metric A] and [metric B]"
- "Show the distribution of [category]"
- "Visualize trends in [metric] over time"
- "Generate multiple charts to analyze this data"
