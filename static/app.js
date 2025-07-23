class EcommerceAIAgent {
    constructor() {
        this.chatContainer = document.getElementById('chat-messages');
        this.questionForm = document.getElementById('question-form');
        this.questionInput = document.getElementById('question-input');
        this.submitBtn = document.getElementById('submit-btn');
        this.loading = document.getElementById('loading');
        this.loadingText = document.getElementById('loading-text');
        
        this.init();
    }
    
    init() {
        // Form submission
        this.questionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.askQuestion();
        });
        
        // Example question buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.questionInput.value = question;
                this.askQuestion();
            });
        });
        
        // Auto-focus input
        this.questionInput.focus();
    }
    
    async askQuestion() {
        const question = this.questionInput.value.trim();
        if (!question) return;
        
        // Add user message
        this.addMessage(question, 'user');
        
        // Clear input and disable form
        this.questionInput.value = '';
        this.setLoading(true);
        
        try {
            // Create assistant message placeholder
            const assistantMessage = this.addMessage('', 'assistant', true);
            const messageContent = assistantMessage.querySelector('.message-content');
            
            // Use fetch with Server-Sent Events (EventSource doesn't support POST)
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            // Read the stream
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (let line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonData = line.substring(6);
                            if (jsonData.trim()) {
                                const data = JSON.parse(jsonData);
                                
                                if (data.error) {
                                    messageContent.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>${data.error}`;
                                    this.setLoading(false);
                                    return;
                                } else if (data.status) {
                                    this.loadingText.textContent = data.status;
                                } else if (data.partial_response) {
                                    messageContent.innerHTML = `<i class="bi bi-robot me-2"></i>${data.partial_response}`;
                                    this.scrollToBottom();
                                } else if (data.final_response) {
                                    this.handleFinalResponse(data.final_response, messageContent);
                                    this.setLoading(false);
                                    return;
                                }
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, an error occurred while processing your question.', 'assistant');
            this.setLoading(false);
        }
    }
    
    handleFinalResponse(response, messageContent) {
        let content = `<i class="bi bi-robot me-2"></i>${response.response}`;
        
        // Add chart if available
        if (response.chart) {
            content += '<div class="chart-container"><div id="chart-' + Date.now() + '"></div></div>';
        }
        
        // Add data table if results available
        if (response.query_result && response.query_result.length > 0) {
            content += this.createDataTable(response.query_result);
        }
        
        // Add SQL query (collapsible)
        if (response.sql_query) {
            content += `
                <div class="mt-3">
                    <button class="btn btn-outline-secondary btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#sql-${Date.now()}" aria-expanded="false">
                        <i class="bi bi-code"></i> View SQL Query
                    </button>
                    <div class="collapse" id="sql-${Date.now()}">
                        <div class="sql-query mt-2">
                            <code>${response.sql_query}</code>
                        </div>
                    </div>
                </div>
            `;
        }
        
        messageContent.innerHTML = content;
        
        // Render chart if available
        if (response.chart) {
            const chartId = messageContent.querySelector('[id^="chart-"]').id;
            Plotly.newPlot(chartId, response.chart.data, response.chart.layout, {responsive: true});
        }
        
        this.scrollToBottom();
    }
    
    createDataTable(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        let table = '<div class="data-table"><table class="table table-sm table-striped"><thead><tr>';
        
        headers.forEach(header => {
            table += `<th>${header}</th>`;
        });
        
        table += '</tr></thead><tbody>';
        
        data.slice(0, 10).forEach(row => { // Limit to first 10 rows
            table += '<tr>';
            headers.forEach(header => {
                const value = row[header];
                const displayValue = typeof value === 'number' ? value.toLocaleString() : value;
                table += `<td>${displayValue || '-'}</td>`;
            });
            table += '</tr>';
        });
        
        table += '</tbody></table>';
        
        if (data.length > 10) {
            table += `<small class="text-muted">Showing first 10 of ${data.length} results</small>`;
        }
        
        table += '</div>';
        return table;
    }
    
    addMessage(content, type, isPlaceholder = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (isPlaceholder) {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <span class="typing-indicator"></span>
                    <span class="typing-indicator"></span>
                    <span class="typing-indicator"></span>
                </div>
            `;
        } else {
            const icon = type === 'user' ? 'bi-person' : 'bi-robot';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <i class="bi ${icon} me-2"></i>${content}
                </div>
            `;
        }
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    setLoading(isLoading) {
        if (isLoading) {
            this.loading.style.display = 'block';
            this.submitBtn.disabled = true;
            this.questionInput.disabled = true;
        } else {
            this.loading.style.display = 'none';
            this.submitBtn.disabled = false;
            this.questionInput.disabled = false;
            this.questionInput.focus();
        }
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EcommerceAIAgent();
});
