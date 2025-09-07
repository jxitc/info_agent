/**
 * Info Agent - Main Application JavaScript
 * 
 * This file contains the core client-side functionality for the Info Agent web interface.
 */

class InfoAgent {
    constructor() {
        this.apiBaseUrl = this.getApiBaseUrl();
        this.currentPage = 'memories';
        this.memories = [];
        this.searchQuery = '';
        this.isLoading = false;
        this.searchStats = null; // Store search filtering statistics
        this.chatHistory = []; // Store chat messages
        this.ragResults = []; // Store RAG search results for chat context
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadInitialData();
        
        console.log('Info Agent initialized');
    }
    
    /**
     * Get API base URL, using same host and port as current page
     */
    getApiBaseUrl() {
        const protocol = window.location.protocol;
        const host = window.location.host; // includes port
        
        return `${protocol}//${host}/api/v1`;
    }
    
    /**
     * Setup event listeners for UI interactions
     */
    setupEventListeners() {
        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobile-menu-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (mobileToggle && sidebar) {
            mobileToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }
        
        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                if (page) {
                    this.navigateTo(page);
                }
            });
        });
        
        // Search functionality
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        
        if (searchInput) {
            // Search when Enter is pressed
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
            });
        }
        
        if (searchButton) {
            // Search when button is clicked
            searchButton.addEventListener('click', () => {
                const query = searchInput ? searchInput.value : '';
                this.performSearch(query);
            });
        }
        
        // Add memory form
        const addForm = document.getElementById('add-memory-form');
        if (addForm) {
            addForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddMemory(e);
            });
        }
    }
    
    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Focus search with '/' or Ctrl+K
            if (e.key === '/' || (e.ctrlKey && e.key === 'k')) {
                e.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Clear search with Escape
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('search-input');
                if (searchInput && document.activeElement === searchInput) {
                    searchInput.value = '';
                    searchInput.blur();
                    this.loadMemories();
                }
            }
            
            // Navigation shortcuts
            if (e.ctrlKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateTo('memories');
                        break;
                    case 'n':
                        e.preventDefault();
                        this.navigateTo('add');
                        break;
                }
            }
        });
    }
    
    /**
     * Load initial data when app starts
     */
    async loadInitialData() {
        await this.loadMemories();
        this.updateUI();
        
        // Clear RAG panel on startup
        this.clearRagPanelOnStartup();
    }
    
    /**
     * Navigate to different pages/views
     */
    navigateTo(page) {
        // Update navigation active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-page="${page}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
        
        this.currentPage = page;
        this.updateUI();
        
        // Close mobile menu
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
    
    /**
     * Update UI based on current page and state
     */
    updateUI() {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;
        
        switch(this.currentPage) {
            case 'memories':
                this.renderMemoriesView();
                break;
            case 'add':
                this.renderAddMemoryView();
                break;
            case 'chat':
                this.renderChatView();
                // Clear RAG panel when first entering chat view
                setTimeout(() => this.clearRagPanelOnStartup(), 100);
                break;
            case 'status':
                this.renderStatusView();
                break;
            case 'detail':
                this.renderMemoryDetailView();
                break;
            default:
                this.renderMemoriesView();
        }
    }
    
    /**
     * Render memories list view
     */
    renderMemoriesView() {
        const content = `
            <div class="search-container">
                <input 
                    type="text" 
                    id="search-input" 
                    class="search-bar" 
                    placeholder="Search for memory... (Press Enter or click search)"
                    value="${this.searchQuery}"
                >
                <button id="search-button" class="search-button" type="button" title="Search">
                    <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </button>
            </div>
            
            <div id="memories-container">
                ${this.isLoading ? this.renderLoading() : this.renderMemories()}
            </div>
        `;
        
        document.getElementById('main-content').innerHTML = content;
        this.setupEventListeners(); // Re-setup event listeners for new elements
    }
    
    /**
     * Render chat view with split layout
     */
    renderChatView() {
        const content = `
            <div class="chat-container">
                <div class="chat-layout">
                    <!-- Left side: ChatGPT-style chat interface -->
                    <div class="chat-panel">
                        <div class="chat-header">
                            <h2>💬 Chat with Info Agent</h2>
                            <div class="chat-status">
                                <span class="status-indicator online"></span>
                                Memory Agent Ready
                            </div>
                        </div>
                        
                        <div class="chat-messages" id="chat-messages">
                            <div class="message ai-message">
                                <div class="message-avatar">🤖</div>
                                <div class="message-content">
                                    <div class="message-text">Hi there! I'm your personal memory agent. I can help you search through your memories, find relevant information, and answer questions about what you've stored. What would you like to know?</div>
                                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="chat-input-container">
                            <div class="chat-input-wrapper">
                                <textarea 
                                    id="chat-input" 
                                    class="chat-input" 
                                    placeholder="Ask about your memories... (Press Enter to send)"
                                    rows="1"
                                ></textarea>
                                <button id="chat-send-button" class="chat-send-button" type="button">
                                    <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Right side: RAG search results panel -->
                    <div class="rag-panel">
                        <div class="rag-header">
                            <h3>📚 Relevant Memories</h3>
                            <div class="rag-info">
                                <span id="rag-count">Welcome</span>
                            </div>
                        </div>
                        
                        <div class="rag-results" id="rag-results">
                            <!-- RAG results will be dynamically populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('main-content').innerHTML = content;
        this.setupChatEventListeners();
    }
    
    /**
     * Setup event listeners for chat interface
     */
    setupChatEventListeners() {
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send-button');
        
        if (chatInput) {
            // Auto-resize textarea
            chatInput.addEventListener('input', () => {
                chatInput.style.height = 'auto';
                chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
            });
            
            // Send on Enter (but Shift+Enter for new line)
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
        }
        
        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.sendChatMessage();
            });
        }
    }
    
    /**
     * Send chat message to memory agent
     */
    async sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addChatMessage(message, 'user');
        
        // Clear input and reset height
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Clear RAG results from previous query
        this.clearRagResults();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Call the memory agent API
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: {} // TODO: Add conversation context in future
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add AI response to chat
                this.addChatMessage(data.data.response, 'ai');
                
                // Update RAG results panel with real search results
                this.updateRagResults(data.data.rag_results, data.data.metadata);
                
                console.log('Chat response received:', {
                    iterations: data.data.metadata.iterations,
                    operation_type: data.data.metadata.operation_type,
                    total_results: data.data.metadata.total_results
                });
                
            } else {
                // Handle API error
                this.hideTypingIndicator();
                const errorMsg = data.error?.message || 'Failed to process your message';
                this.addChatMessage(`Sorry, I encountered an error: ${errorMsg}`, 'ai');
                console.error('Chat API error:', data.error);
            }
            
        } catch (error) {
            // Handle network/parsing errors
            this.hideTypingIndicator();
            this.addChatMessage('Sorry, I\'m having trouble connecting to the memory agent. Please try again.', 'ai');
            console.error('Chat request failed:', error);
        }
    }
    
    /**
     * Add message to chat (placeholder implementation)
     */
    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const time = new Date().toLocaleTimeString();
        
        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingElement = document.createElement('div');
        typingElement.className = 'message ai-message typing-indicator';
        typingElement.id = 'typing-indicator';
        
        typingElement.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Clear RAG panel on startup with welcome message
     */
    clearRagPanelOnStartup() {
        const ragCount = document.getElementById('rag-count');
        const ragResultsContainer = document.getElementById('rag-results');
        
        if (ragCount) {
            ragCount.textContent = 'Start chatting to see relevant memories';
        }
        
        if (ragResultsContainer) {
            ragResultsContainer.innerHTML = `
                <div class="rag-welcome">
                    <div class="rag-welcome-icon">💬</div>
                    <h4>Welcome to Info Agent</h4>
                    <p>Start a conversation to see relevant memories appear here as the agent searches through your personal knowledge base.</p>
                    <div class="rag-features">
                        <div class="feature-item">🔍 Smart search results</div>
                        <div class="feature-item">📊 Relevance scoring</div>
                        <div class="feature-item">🧠 AI-powered matching</div>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Clear RAG results panel during search
     */
    clearRagResults() {
        const ragCount = document.getElementById('rag-count');
        const ragResultsContainer = document.getElementById('rag-results');
        
        if (ragCount) {
            ragCount.textContent = 'Searching memories...';
        }
        
        if (ragResultsContainer) {
            ragResultsContainer.innerHTML = `
                <div class="rag-loading">
                    <div class="spinner"></div>
                    <p>Searching through your memories...</p>
                </div>
            `;
        }
    }
    
    /**
     * Update RAG results with real agent search results
     */
    updateRagResults(ragResults, metadata) {
        const ragCount = document.getElementById('rag-count');
        const ragResultsContainer = document.getElementById('rag-results');
        
        if (ragCount) {
            const count = ragResults?.length || 0;
            const query = metadata?.query || '';
            ragCount.textContent = `${count} ${count === 1 ? 'memory' : 'memories'} found${query ? ` for "${query}"` : ''}`;
        }
        
        if (ragResultsContainer) {
            if (!ragResults || ragResults.length === 0) {
                ragResultsContainer.innerHTML = `
                    <div class="rag-empty">
                        <p>No relevant memories found for this query.</p>
                    </div>
                `;
                return;
            }
            
            // Render real RAG results
            const resultsHtml = ragResults.map(result => this.renderRagMemory(result)).join('');
            ragResultsContainer.innerHTML = resultsHtml;
        }
    }
    
    /**
     * Render individual RAG memory result
     */
    renderRagMemory(result) {
        const score = result.relevance_score || 0;
        const scoreText = score.toFixed(2);
        const scoreClass = score >= 0.8 ? 'high' : score >= 0.5 ? 'medium' : 'low';
        
        const date = result.metadata?.date ? 
            new Date(result.metadata.date).toLocaleDateString() : '';
        const category = result.metadata?.category || '';
        const wordCount = result.metadata?.word_count || '';
        
        return `
            <div class="rag-memory" data-memory-id="${result.memory_id}">
                <div class="rag-memory-header">
                    <span class="rag-memory-id">#${result.memory_id}</span>
                    <span class="rag-memory-score score-${scoreClass}">Score: ${scoreText}</span>
                </div>
                <h4 class="rag-memory-title">${this.escapeHtml(result.title)}</h4>
                <p class="rag-memory-snippet">${this.escapeHtml(result.snippet)}</p>
                <div class="rag-memory-meta">
                    ${date ? `<span class="rag-memory-date">📅 ${date}</span>` : ''}
                    ${category ? `<span class="rag-memory-category">${this.escapeHtml(category)}</span>` : ''}
                    ${wordCount ? `<span class="rag-memory-words">${wordCount} words</span>` : ''}
                    <span class="rag-memory-source">📊 ${result.source}</span>
                </div>
            </div>
        `;
    }

    /**
     * Render add memory view
     */
    renderAddMemoryView() {
        const content = `
            <div class="add-memory-container">
                <h1>Add New Memory</h1>
                
                <form id="add-memory-form" class="add-memory-form">
                    <div class="form-group">
                        <label for="memory-content">Memory Content</label>
                        <textarea 
                            id="memory-content" 
                            class="form-control" 
                            rows="6" 
                            placeholder="Enter your memory content here..."
                            required
                        ></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="memory-title">Title (optional)</label>
                        <input 
                            type="text" 
                            id="memory-title" 
                            class="form-control" 
                            placeholder="Custom title (will be auto-generated if empty)"
                        >
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary" ${this.isLoading ? 'disabled' : ''}>
                            ${this.isLoading ? '<div class="spinner"></div>' : ''} Add Memory
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="app.navigateTo('memories')">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.getElementById('main-content').innerHTML = content;
        this.setupEventListeners();
    }
    
    
    /**
     * Render system status view
     */
    async renderStatusView() {
        const content = `
            <div class="status-container">
                <h1>System Status</h1>
                <div id="status-content">
                    ${this.renderLoading()}
                </div>
            </div>
        `;
        
        document.getElementById('main-content').innerHTML = content;
        
        try {
            const status = await this.fetchSystemStatus();
            document.getElementById('status-content').innerHTML = this.renderSystemStatus(status);
        } catch (error) {
            document.getElementById('status-content').innerHTML = this.renderError('Failed to load system status');
        }
    }
    
    /**
     * Render memory detail view
     */
    async renderMemoryDetailView() {
        if (!this.currentMemoryId) {
            this.navigateTo('memories');
            return;
        }
        
        const content = `
            <div class="memory-detail-container">
                <div class="memory-detail-header">
                    <button class="btn btn-secondary" onclick="app.navigateTo('memories')">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                        </svg>
                        Back to Memories
                    </button>
                    <h1>Memory Details</h1>
                </div>
                
                <div id="memory-detail-content">
                    ${this.renderLoading()}
                </div>
            </div>
        `;
        
        document.getElementById('main-content').innerHTML = content;
        
        try {
            const memory = await this.fetchMemoryDetails(this.currentMemoryId);
            document.getElementById('memory-detail-content').innerHTML = this.renderMemoryDetail(memory);
        } catch (error) {
            console.error('Error loading memory details:', error);
            document.getElementById('memory-detail-content').innerHTML = this.renderError(`Failed to load memory details: ${error.message}`);
        }
    }
    
    /**
     * Render memories grid
     */
    renderMemories() {
        if (!this.memories || this.memories.length === 0) {
            return this.renderEmptyState();
        }
        
        const memoriesHtml = this.memories.map(memory => this.renderMemoryCard(memory)).join('');
        const searchInfoHtml = this.renderSearchInfo();
        
        return `
            ${searchInfoHtml}
            <div class="memory-grid">${memoriesHtml}</div>
        `;
    }
    
    /**
     * Render search info message
     */
    renderSearchInfo() {
        if (!this.searchStats) {
            return ''; // No search performed, don't show anything
        }
        
        const { totalResults, filteredResults, query } = this.searchStats;
        
        if (totalResults === filteredResults) {
            // No filtering occurred
            return `
                <div class="search-info">
                    <svg class="search-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    Found <strong>${filteredResults}</strong> ${filteredResults === 1 ? 'result' : 'results'} for "<em>${this.escapeHtml(query)}</em>"
                </div>
            `;
        } else {
            // Filtering occurred
            const filtered = totalResults - filteredResults;
            return `
                <div class="search-info">
                    <svg class="search-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    Found <strong>${filteredResults}</strong> relevant ${filteredResults === 1 ? 'result' : 'results'} for "<em>${this.escapeHtml(query)}</em>"
                    <span class="filter-info">— filtered out ${filtered} ${filtered === 1 ? 'result' : 'results'} with relevance &lt; 0.3</span>
                </div>
            `;
        }
    }
    
    /**
     * Render individual memory card
     */
    renderMemoryCard(memory) {
        const createdDate = new Date(memory.created_at).toLocaleDateString();
        const categories = memory.dynamic_fields?.categories || memory.dynamic_fields?.category ? 
            [memory.dynamic_fields.category] : [];
        
        // Show ranking explanation if this is a search result and explanation exists
        const showRankingInfo = this.searchQuery && memory.ranking_explanation;
        
        return `
            <div class="memory-card" onclick="app.viewMemoryDetails(${memory.id})">
                <div class="memory-header">
                    <h3 class="memory-title">${this.escapeHtml(memory.title)}</h3>
                    <div class="memory-header-right">
                        <span class="memory-id">#${memory.id}</span>
                        ${showRankingInfo && memory.relevance_score ? `
                            <span class="memory-score" title="Relevance Score">
                                ${(memory.relevance_score * 100).toFixed(0)}%
                            </span>
                        ` : ''}
                    </div>
                </div>
                
                <div class="memory-content">
                    ${this.escapeHtml(memory.content)}
                </div>
                
                ${showRankingInfo ? `
                    <div class="memory-ranking-info">
                        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span class="ranking-explanation">${this.escapeHtml(memory.ranking_explanation)}</span>
                    </div>
                ` : ''}
                
                <div class="memory-meta">
                    <span class="memory-date">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
                        </svg>
                        ${createdDate}
                    </span>
                    
                    <div class="memory-stats">
                        <span>${memory.word_count} words</span>
                        ${showRankingInfo && memory.match_type ? `
                            <span class="match-type" title="Search Method">${memory.match_type}</span>
                        ` : ''}
                    </div>
                </div>
                
                ${categories.length > 0 ? `
                    <div class="memory-tags">
                        ${categories.map(cat => `<span class="memory-tag">${this.escapeHtml(cat)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Render loading state
     */
    renderLoading() {
        return `
            <div class="loading">
                <div class="spinner"></div>
                Loading...
            </div>
        `;
    }
    
    /**
     * Render empty state
     */
    renderEmptyState() {
        return `
            <div class="empty-state">
                <svg class="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <p>No memories found</p>
                <p class="text-muted">Add your first memory to get started</p>
                <button class="btn btn-primary" onclick="app.navigateTo('add')" style="margin-top: 1rem;">
                    Add Memory
                </button>
            </div>
        `;
    }
    
    /**
     * Render error state
     */
    renderError(message) {
        return `
            <div class="empty-state">
                <svg class="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="location.reload()" style="margin-top: 1rem;">
                    Retry
                </button>
            </div>
        `;
    }
    
    /**
     * API Methods
     */
    
    /**
     * Load memories from API
     */
    async loadMemories(limit = 20) {
        this.isLoading = true;
        this.searchStats = null; // Clear search stats when loading all memories
        this.updateUI();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/memories?limit=${limit}`);
            const data = await response.json();
            
            if (data.success) {
                this.memories = data.data.memories;
            } else {
                throw new Error(data.error?.message || 'Failed to load memories');
            }
        } catch (error) {
            console.error('Error loading memories:', error);
            this.memories = [];
            this.showError('Failed to load memories. Please check if the API server is running.');
        } finally {
            this.isLoading = false;
            this.updateUI();
        }
    }
    
    /**
     * Search memories
     */
    async searchMemories(query, limit = 20) {
        if (!query.trim()) {
            return this.loadMemories(limit);
        }
        
        this.isLoading = true;
        this.searchQuery = query;
        this.updateUI();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
            const data = await response.json();
            
            if (data.success) {
                // Filter results by relevance score > 0.3, then convert to memory format
                const filteredResults = data.data.results.filter(result => {
                    const hasScore = result.relevance_score !== null && result.relevance_score !== undefined;
                    return hasScore && result.relevance_score > 0.3;
                });
                
                // Store search statistics for UI display
                this.searchStats = {
                    totalResults: data.data.results.length,
                    filteredResults: filteredResults.length,
                    query: query
                };
                
                this.memories = filteredResults.map(result => ({
                    id: result.memory_id,
                    title: result.title,
                    content: result.snippet,
                    created_at: new Date().toISOString(), // Placeholder
                    word_count: result.snippet.split(' ').length,
                    dynamic_fields: {},
                    relevance_score: result.relevance_score, // Keep relevance score for debugging
                    match_type: result.match_type || 'hybrid',
                    ranking_explanation: result.ranking_explanation || ''
                }));
                
                console.log(`Search for "${query}": ${data.data.results.length} total, ${filteredResults.length} relevant (score > 0.3)`);
            } else {
                throw new Error(data.error?.message || 'Search failed');
            }
        } catch (error) {
            console.error('Error searching memories:', error);
            this.memories = [];
            this.showError('Search failed. Please try again.');
        } finally {
            this.isLoading = false;
            this.updateUI();
        }
    }
    
    /**
     * Add new memory
     */
    async addMemory(content, title = null) {
        this.isLoading = true;
        this.updateUI();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/memories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    title: title || undefined
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Memory added successfully!');
                this.navigateTo('memories');
                await this.loadMemories(); // Refresh memories list
            } else {
                throw new Error(data.error?.message || 'Failed to add memory');
            }
        } catch (error) {
            console.error('Error adding memory:', error);
            this.showError('Failed to add memory. Please try again.');
        } finally {
            this.isLoading = false;
            this.updateUI();
        }
    }
    
    /**
     * Fetch system status
     */
    async fetchSystemStatus() {
        const response = await fetch(`${this.apiBaseUrl}/status`);
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            throw new Error(data.error?.message || 'Failed to fetch status');
        }
    }
    
    /**
     * Fetch individual memory details
     */
    async fetchMemoryDetails(memoryId) {
        const response = await fetch(`${this.apiBaseUrl}/memories/${memoryId}`);
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            throw new Error(data.error?.message || 'Failed to fetch memory details');
        }
    }
    
    /**
     * Event Handlers
     */
    
    // Removed handleSearch method - now only search on Enter key press
    
    performSearch(query) {
        this.searchMemories(query);
    }
    
    async handleAddMemory(event) {
        const formData = new FormData(event.target);
        const content = formData.get('content') || document.getElementById('memory-content').value;
        const title = formData.get('title') || document.getElementById('memory-title').value;
        
        if (!content.trim()) {
            this.showError('Please enter memory content');
            return;
        }
        
        await this.addMemory(content.trim(), title.trim() || null);
    }
    
    /**
     * View memory details
     */
    async viewMemoryDetails(memoryId) {
        console.log('View memory details:', memoryId);
        this.currentMemoryId = memoryId;
        this.navigateTo('detail');
    }
    
    /**
     * Utility Methods
     */
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system (can be enhanced)
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem;
            border-radius: 8px;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        `;
        
        // Set colors based on type
        switch(type) {
            case 'error':
                notification.style.background = '#ef4444';
                notification.style.color = 'white';
                break;
            case 'success':
                notification.style.background = '#10b981';
                notification.style.color = 'white';
                break;
            default:
                notification.style.background = '#3b82f6';
                notification.style.color = 'white';
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    renderSystemStatus(status) {
        return `
            <div class="status-grid">
                <div class="status-card">
                    <h3>System Info</h3>
                    <p>Version: ${status.version}</p>
                    <p>Python: ${status.python_version}</p>
                    <p>Platform: ${status.platform}</p>
                    <p>Status: ${status.overall_status}</p>
                </div>
                
                <div class="status-card">
                    <h3>Database</h3>
                    <p>Status: ${status.services?.database?.status || 'Unknown'}</p>
                    <p>Memories: ${status.services?.database?.total_memories || 0}</p>
                </div>
                
                <div class="status-card">
                    <h3>Vector Store</h3>
                    <p>Status: ${status.services?.vector_store?.status || 'Unknown'}</p>
                    <p>Documents: ${status.services?.vector_store?.document_count || 0}</p>
                </div>
                
                <div class="status-card">
                    <h3>AI Services</h3>
                    <p>Status: ${status.services?.ai_services?.status || 'Unknown'}</p>
                    <p>Model: ${status.services?.ai_services?.model || 'N/A'}</p>
                </div>
            </div>
        `;
    }
    
    /**
     * Render detailed memory information
     */
    renderMemoryDetail(memory) {
        const createdDate = new Date(memory.created_at).toLocaleString();
        const updatedDate = new Date(memory.updated_at).toLocaleString();
        
        // Extract dynamic fields for better display
        const dynamicFields = memory.dynamic_fields || {};
        const {
            ai_processed,
            ai_model,
            ai_tokens_used,
            categories,
            category,
            people,
            places,
            dates_times,
            description,
            summary,
            tags,
            priority,
            status,
            ...otherFields
        } = dynamicFields;
        
        return `
            <div class="memory-detail">
                <!-- Main Memory Info -->
                <div class="detail-section main-info">
                    <div class="detail-header">
                        <div class="memory-title-large">${this.escapeHtml(memory.title)}</div>
                        <div class="memory-id-large">#${memory.id}</div>
                    </div>
                </div>
                
                <!-- Content Section -->
                <div class="detail-section">
                    <h3>📝 Content</h3>
                    <div class="content-display">
                        ${this.escapeHtml(memory.content).replace(/\n/g, '<br>')}
                    </div>
                </div>
                
                <!-- Metadata Section -->
                <div class="detail-section">
                    <h3>📊 Metadata</h3>
                    <div class="metadata-grid">
                        <div class="metadata-item">
                            <label>Memory ID:</label>
                            <span>${memory.id}</span>
                        </div>
                        <div class="metadata-item">
                            <label>Word Count:</label>
                            <span>${memory.word_count} words</span>
                        </div>
                        <div class="metadata-item">
                            <label>Content Hash:</label>
                            <span class="hash">${memory.content_hash || 'N/A'}</span>
                        </div>
                        <div class="metadata-item">
                            <label>Version:</label>
                            <span>${memory.version || 1}</span>
                        </div>
                        <div class="metadata-item">
                            <label>Created:</label>
                            <span>${createdDate}</span>
                        </div>
                        <div class="metadata-item">
                            <label>Updated:</label>
                            <span>${updatedDate}</span>
                        </div>
                    </div>
                </div>
                
                ${ai_processed ? `
                <!-- AI Processing Info -->
                <div class="detail-section">
                    <h3>🤖 AI Processing</h3>
                    <div class="ai-info-grid">
                        <div class="ai-info-item">
                            <label>AI Processed:</label>
                            <span class="status-badge success">✅ Yes</span>
                        </div>
                        ${ai_model ? `
                        <div class="ai-info-item">
                            <label>Model Used:</label>
                            <span>${ai_model}</span>
                        </div>
                        ` : ''}
                        ${ai_tokens_used ? `
                        <div class="ai-info-item">
                            <label>Tokens Used:</label>
                            <span>${ai_tokens_used}</span>
                        </div>
                        ` : ''}
                        ${description ? `
                        <div class="ai-info-item">
                            <label>AI Description:</label>
                            <span>${this.escapeHtml(description)}</span>
                        </div>
                        ` : ''}
                        ${summary ? `
                        <div class="ai-info-item">
                            <label>AI Summary:</label>
                            <span>${this.escapeHtml(summary)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : `
                <!-- No AI Processing -->
                <div class="detail-section">
                    <h3>🤖 AI Processing</h3>
                    <div class="ai-info-item">
                        <span class="status-badge neutral">⚪ Not AI processed</span>
                        <p class="text-muted">This memory was created in basic mode without AI analysis.</p>
                    </div>
                </div>
                `}
                
                ${(categories && categories.length) || category || (people && people.length) || (places && places.length) || (tags && tags.length) ? `
                <!-- Extracted Information -->
                <div class="detail-section">
                    <h3>🏷️ Extracted Information</h3>
                    <div class="extracted-info">
                        ${(categories && categories.length) || category ? `
                        <div class="info-group">
                            <label>Categories:</label>
                            <div class="tag-list">
                                ${categories ? categories.map(cat => `<span class="tag category">${this.escapeHtml(cat)}</span>`).join('') : 
                                  category ? `<span class="tag category">${this.escapeHtml(category)}</span>` : ''}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${people && people.length ? `
                        <div class="info-group">
                            <label>People:</label>
                            <div class="tag-list">
                                ${people.map(person => `<span class="tag person">👤 ${this.escapeHtml(person)}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${places && places.length ? `
                        <div class="info-group">
                            <label>Places:</label>
                            <div class="tag-list">
                                ${places.map(place => `<span class="tag place">📍 ${this.escapeHtml(place)}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${dates_times && dates_times.length ? `
                        <div class="info-group">
                            <label>Dates & Times:</label>
                            <div class="tag-list">
                                ${dates_times.map(dt => `<span class="tag datetime">📅 ${this.escapeHtml(dt)}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${tags && tags.length ? `
                        <div class="info-group">
                            <label>Tags:</label>
                            <div class="tag-list">
                                ${tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${priority ? `
                        <div class="info-group">
                            <label>Priority:</label>
                            <span class="priority-badge priority-${priority}">${priority.toUpperCase()}</span>
                        </div>
                        ` : ''}
                        
                        ${status ? `
                        <div class="info-group">
                            <label>Status:</label>
                            <span class="status-badge">${this.escapeHtml(status)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                ${Object.keys(otherFields).length > 0 ? `
                <!-- Additional Dynamic Fields -->
                <div class="detail-section">
                    <h3>🔧 Dynamic Fields</h3>
                    <div class="dynamic-fields">
                        ${Object.entries(otherFields).map(([key, value]) => `
                            <div class="dynamic-field">
                                <label>${this.escapeHtml(key)}:</label>
                                <span>${typeof value === 'object' ? JSON.stringify(value) : this.escapeHtml(String(value))}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Actions -->
                <div class="detail-actions">
                    <button class="btn btn-secondary" onclick="app.navigateTo('memories')">
                        Back to Memories
                    </button>
                    <button class="btn btn-primary" onclick="app.editMemory(${memory.id})">
                        Edit Memory
                    </button>
                    <button class="btn btn-danger" onclick="app.deleteMemory(${memory.id})">
                        Delete Memory
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Edit memory (placeholder)
     */
    editMemory(memoryId) {
        this.showInfo(`Edit memory ${memoryId} - Coming in future update!`);
    }
    
    /**
     * Delete memory
     */
    async deleteMemory(memoryId) {
        if (!confirm('Are you sure you want to delete this memory? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/memories/${memoryId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Memory deleted successfully!');
                this.navigateTo('memories');
                await this.loadMemories(); // Refresh the memories list
            } else {
                throw new Error(data.error?.message || 'Failed to delete memory');
            }
        } catch (error) {
            console.error('Error deleting memory:', error);
            this.showError(`Failed to delete memory: ${error.message}`);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new InfoAgent();
});