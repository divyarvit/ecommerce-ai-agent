import json
import logging
import time
import re
from flask import render_template, request, Response, jsonify
from sqlalchemy import text
from app import app, db
from ai_service import generate_sql_query, generate_natural_response
import plotly.graph_objs as go
import plotly.utils

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return Response(f"data: {json.dumps({'error': 'Please provide a question'})}\n\n",
                        mimetype='text/event-stream')

    def generate_response():
        with app.app_context():
            try:
                yield f"data: {json.dumps({'status': 'Processing your question...'})}\n\n"
                time.sleep(0.5)

                yield f"data: {json.dumps({'status': 'Generating SQL query...'})}\n\n"
                time.sleep(0.5)

                sql_result = generate_sql_query(question)

                if not sql_result.get('query'):
                    yield f"data: {json.dumps({'error': sql_result.get('explanation', 'Could not generate SQL query')})}\n\n"
                    return

                raw_query = sql_result['query']
                logging.debug(f"Raw SQL: {raw_query}")

                query = patch_division_by_zero(raw_query)
                logging.debug(f"Patched SQL: {query}")

                visualization_type = sql_result.get('visualization_type', 'none')

                yield f"data: {json.dumps({'status': 'Executing database query...'})}\n\n"
                time.sleep(0.5)

                try:
                    result = db.session.execute(text(query))
                    rows = result.fetchall()
                    columns = result.keys()

                    query_result = []
                    for row in rows:
                        row_dict = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            if hasattr(value, '__float__'):
                                value = float(value)
                            elif hasattr(value, 'isoformat'):
                                value = value.isoformat()
                            row_dict[column] = value
                        query_result.append(row_dict)

                except Exception as e:
                    logging.error(f"SQL execution error: {e}")
                    yield f"data: {json.dumps({'error': f'Database query failed: {str(e)}'})}\n\n"
                    return

                yield f"data: {json.dumps({'status': 'Generating response...'})}\n\n"
                time.sleep(0.5)

                natural_response = generate_natural_response(query_result, question, query)

                chart_json = None
                if visualization_type != 'none' and query_result:
                    try:
                        chart_json = generate_chart(query_result, visualization_type, question)
                    except Exception as e:
                        logging.error(f"Chart generation error: {e}")

                words = natural_response.split()
                response_data = {
                    'response': '',
                    'query_result': query_result,
                    'chart': chart_json,
                    'sql_query': query
                }

                for word in words:
                    response_data['response'] += word + ' '
                    yield f"data: {json.dumps({'partial_response': response_data['response']})}\n\n"
                    time.sleep(0.05)

                yield f"data: {json.dumps({'final_response': response_data})}\n\n"

            except Exception as e:
                logging.error(f"Error in ask_question: {e}")
                yield f"data: {json.dumps({'error': f'An error occurred: {str(e)}'})}\n\n"

    return Response(generate_response(), mimetype='text/event-stream')

def patch_division_by_zero(sql: str) -> str:
    """
    Patch SQL to avoid division-by-zero errors.
    Ensures all divisions are rewritten as A / NULLIF(B, 0)
    Avoids re-patching already wrapped divisions and preserves aggregate functions.
    """
    def replacer(match):
        numerator = match.group(1)
        denominator = match.group(2)
        logging.debug(f"Division found: {numerator} / {denominator}")

        # Skip if denominator is already wrapped in NULLIF or is an aggregate function
        if 'NULLIF' in denominator or denominator.strip().upper().startswith(('COUNT(', 'SUM(', 'AVG(')):
            logging.debug(f"Skipping patch for denominator: {denominator}")
            return match.group(0)

        return f"{numerator} / NULLIF({denominator}, 0)"

    # Clean malformed LLM-generated patterns like: NULLIF(NULLIF, 0)(SUM(x), 0)
    sql = re.sub(r'NULLIF\(NULLIF,\s*0\)\(([^()]+?),\s*0\)', r'NULLIF(\1, 0)', sql)
    logging.debug(f"After cleaning malformed NULLIF: {sql}")

    # Fix double-nested NULLIFs like: NULLIF(NULLIF(expr, 0), 0)
    sql = re.sub(r'NULLIF\(NULLIF\(([^()]+?),\s*0\),\s*0\)', r'NULLIF(\1, 0)', sql)
    logging.debug(f"After cleaning double-nested NULLIF: {sql}")

    # Patch raw A / B to A / NULLIF(B, 0), excluding aggregate functions
    div_pattern = r'([\w\.\(\)\s*]+)\s*/\s*([\w\.\(\)\s*]+)(?!\s*\))'
    sql = re.sub(div_pattern, replacer, sql)
    logging.debug(f"Final patched SQL: {sql}")

    return sql

def generate_chart(data, chart_type, title):
    """Generate chart data for visualization"""
    if not data or len(data) == 0:
        return None

    try:
        columns = list(data[0].keys())
        if len(columns) < 2 and chart_type != "number":
            return None

        if chart_type == "number":
            value = data[0][columns[0]]
            fig = go.Figure(data=[go.Indicator(mode="number", value=value)])
        else:
            x_values = [row[columns[0]] for row in data]
            y_values = [row[columns[1]] for row in data]
            if chart_type == 'bar':
                fig = go.Figure(data=[go.Bar(x=x_values, y=y_values)])
            elif chart_type == 'line':
                fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='lines+markers')])
            elif chart_type == 'pie':
                fig = go.Figure(data=[go.Pie(labels=x_values, values=y_values)])
            else:
                fig = go.Figure(data=[go.Bar(x=x_values, y=y_values)])

        fig.update_layout(title=title, template='plotly_dark', height=400)
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))

    except Exception as e:
        logging.error(f"Chart generation error: {e}")
        return None

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'database': 'connected'})