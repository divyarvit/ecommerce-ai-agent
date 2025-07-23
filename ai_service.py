import os
import json
import logging
import requests
from typing import Dict, Any

logging.basicConfig(level=logging.DEBUG)

class LocalLLMService:
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3")
        self.timeout = 300

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            logging.debug(f"Ollama availability check response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Ollama availability check failed: {e}")
            return False

def clean_sql_response(response: str) -> str:
    response = response.strip()
    if "SELECT" in response.upper():
        lines = response.split('\n')
        sql_lines = []
        in_sql = False
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                in_sql = True
            if in_sql:
                sql_lines.append(line)
                if line.endswith(';'):
                    break
        if sql_lines:
            return ' '.join(sql_lines)
    return response

def determine_visualization_type(sql_query: str, question: str) -> str:
    sql_lower = sql_query.lower()
    question_lower = question.lower()
    if any(word in sql_lower for word in ['date', 'time', 'month', 'day']):
        return "line"
    if any(word in sql_lower for word in ['group by', 'order by']) and 'count' in sql_lower:
        return "bar"
    if any(word in question_lower for word in ['distribution', 'breakdown', 'percentage']):
        return "pie"
    if any(word in question_lower for word in ['correlation', 'relationship', 'vs']):
        return "scatter"
    if "conversion rate" in question_lower:
        return "bar"
    if any(word in question_lower for word in ['total sales', 'total revenue']):
        return "number"
    if "cpc" in question_lower:
        return "bar"
    return "pie"

def fallback_query_generation(question: str) -> Dict[str, Any]:
    question_lower = question.lower()
    fallback_map = {
        "total sales": {
            "query": "SELECT SUM(total_sales) AS total_sales FROM total_sales_metrics;",
            "visualization_type": "number"
        },
        "roas": {
            "query": "SELECT item_id, SUM(ad_sales) / NULLIF(SUM(ad_spend), 0) AS roas FROM ad_sales_metrics GROUP BY item_id ORDER BY roas DESC;",
            "visualization_type": "bar"
        },
        "cpc": {
            "query": "SELECT item_id, SUM(ad_spend) / NULLIF(SUM(clicks), 0) AS cpc FROM ad_sales_metrics GROUP BY item_id ORDER BY cpc DESC LIMIT 1;",
            "visualization_type": "bar"
        },
        "eligible": {
            "query": """
                SELECT 
                    COUNT(DISTINCT CASE WHEN eligibility = true THEN item_id END) AS eligible_products,
                    COUNT(DISTINCT item_id) AS total_products,
                    (COUNT(DISTINCT CASE WHEN eligibility = true THEN item_id END) * 1.0) / NULLIF(COUNT(DISTINCT item_id), 0) * 100 AS percentage_eligible
                FROM product_eligibility;
            """,
            "visualization_type": "pie"
        },
        "conversion rate": {
            "query": """
                SELECT item_id, 
                       SUM(units_sold) / NULLIF(SUM(clicks), 0) AS conversion_rate 
                FROM ad_sales_metrics 
                GROUP BY item_id 
                ORDER BY conversion_rate DESC 
                LIMIT 10;
            """,
            "visualization_type": "bar"
        }
    }
    for key, val in fallback_map.items():
        if key in question_lower:
            return {**val, "model_used": "fallback"}
    return {
        "query": "SELECT 'Please rephrase your question' as message;",
        "visualization_type": "none",
        "model_used": "fallback"
    }

def generate_sql_query(question: str) -> Dict[str, Any]:
    logging.info(f"Generating SQL for question: {question}")
    service = LocalLLMService()
    if not service.is_available():
        logging.error("Ollama service unavailable at %s", service.base_url)
        raise Exception("Local LLM (Ollama) not available. Please install and start Ollama with a model.")

    max_retries = 2
    system_prompt = os.environ.get("OLLAMA_SQL_PROMPT", "You are an expert SQL analyst for e-commerce data...")
    payload = {
        "model": service.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "stream": False
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{service.base_url}/api/chat",
                json=payload,
                timeout=service.timeout,
                stream=True
            )
            if response.status_code == 200:
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        logging.debug(f"Ollama response chunk: {chunk}")
                        if chunk.get("message", {}).get("content"):
                            full_content += chunk["message"]["content"]
                        if chunk.get("done", False):
                            break
                sql_query = clean_sql_response(full_content.strip())
                if "SELECT" not in sql_query.upper() or "Please rephrase" in sql_query:
                    logging.warning(f"Invalid SQL generated on attempt {attempt + 1}: {sql_query}")
                    continue
                viz_type = determine_visualization_type(sql_query, question)
                return {
                    "query": sql_query,
                    "visualization_type": viz_type,
                    "model_used": f"local_{service.model}"
                }
            else:
                logging.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            logging.error(f"Local LLM error on attempt {attempt + 1}: {e}")
            continue

    return fallback_query_generation(question)
