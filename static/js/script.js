// DOM Elements
const searchForm = document.getElementById('searchForm');
const hanInput = document.getElementById('hanInput');
const clearBtn = document.getElementById('clearBtn');
const searchBtn = document.getElementById('searchBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const resultCount = document.getElementById('resultCount');
const bestResult = document.getElementById('bestResult');
const bestMatch = document.getElementById('bestMatch');
const bestTranslation = document.getElementById('bestTranslation');
const allResults = document.getElementById('allResults');
const errorMessage = document.getElementById('errorMessage');

// State
let isSearching = false;

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupInputHandling();
    checkServerStatus();
});

async function checkServerStatus() {
    try {
        const response = await fetch('/api/health');
        if (response.ok) {
            console.log('Server is healthy');
            hideError();
        } else {
            console.warn('Server health check failed');
            showError('Máy chủ đang khởi động, vui lòng đợi...');
        }
    } catch (err) {
        console.warn('Server not ready yet:', err);
        showError('Máy chủ đang khởi động, vui lòng đợi...');
    }
}

function setupEventListeners() {
    // Form submission
    searchForm.addEventListener('submit', handleSearch);
    
    // Clear button
    clearBtn.addEventListener('click', clearInput);
    
    // Input changes
    hanInput.addEventListener('input', handleInputChange);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

function setupInputHandling() {
    // Auto-resize textarea
    hanInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
    
    // Show/hide clear button
    hanInput.addEventListener('input', function() {
        if (this.value.trim()) {
            clearBtn.classList.add('show');
        } else {
            clearBtn.classList.remove('show');
        }
    });
}

function handleInputChange() {
    // Hide previous results when user starts typing
    if (results.classList.contains('show')) {
        hideResults();
    }
}

function handleKeyboard(e) {
    // Ctrl/Cmd + Enter to search
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSearch(e);
    }
    
    // Escape to clear
    if (e.key === 'Escape') {
        clearInput();
    }
}

function clearInput() {
    hanInput.value = '';
    hanInput.style.height = 'auto';
    clearBtn.classList.remove('show');
    hanInput.focus();
}

async function handleSearch(e) {
    e.preventDefault();
    
    const query = hanInput.value.trim();
    
    if (!query) {
        showError('Vui lòng nhập câu tiếng Hán cần tìm kiếm.');
        return;
    }
    
    if (isSearching) {
        return;
    }
    
    isSearching = true;
    setSearchingState(true);
    hideResults();
    hideError();
    
    try {
        // Đầu tiên, khởi tạo model nếu cần
        console.log('Initializing model...');
        try {
            const initResponse = await fetch('/api/init-model');
            if (!initResponse.ok) {
                console.warn('Model init failed, continuing with search...');
            } else {
                const initData = await initResponse.json();
                console.log('Model init response:', initData);
            }
        } catch (initErr) {
            console.warn('Model init error, continuing with search:', initErr);
        }
        
        // Sau đó thực hiện search
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Có lỗi xảy ra khi tìm kiếm.');
        }
        
    } catch (err) {
        console.error('Search error:', err.message);
        if (err.message.includes('502') || err.message.includes('Bad Gateway')) {
            showError('Máy chủ đang khởi động, vui lòng thử lại sau 30 giây.');
        } else if (err.message.includes('Failed to fetch')) {
            showError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.');
        } else {
            showError('Có lỗi xảy ra: ' + err.message);
        }
    } finally {
        isSearching = false;
        setSearchingState(false);
    }
}

function setSearchingState(searching) {
    searchBtn.disabled = searching;
    
    if (searching) {
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Đang tìm...</span>';
        loading.classList.remove('hidden');
    } else {
        searchBtn.innerHTML = '<i class="fas fa-search"></i><span>Tìm kiếm</span>';
        loading.classList.add('hidden');
    }
}

function displayResults(data) {
    const { results: searchResults, best_result } = data;
    
    // Update result count
    resultCount.textContent = searchResults ? searchResults.length : 0;
    
    // Display best result
    if (best_result && searchResults && searchResults.length > 0) {
        displayBestResult(best_result);
    } else {
        console.error('No valid results found:', data);
        showError('Không tìm thấy kết quả phù hợp');
        return;
    }
    
    // Show results section
    results.classList.remove('hidden');
    
    // Smooth scroll to results
    setTimeout(() => {
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
    
    // Add fade-in animation
    addFadeInAnimation(results);
}

function displayBestResult(bestResultData) {
    if (bestResultData && bestResultData.score !== null && bestResultData.score !== undefined) {
        bestMatch.textContent = bestResultData.best_match || '';
        bestTranslation.textContent = bestResultData.translation || '';
        
        bestResult.classList.remove('hidden');
    } else {
        console.error('Invalid bestResultData:', bestResultData);
        showError('Dữ liệu kết quả không hợp lệ');
    }
}

function displayAllResults(searchResults) {
    allResults.innerHTML = '';
    
    searchResults.forEach((result, index) => {
        const resultCard = createResultCard(result, index + 1);
        allResults.appendChild(resultCard);
    });
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    // Validate result data
    if (!result || typeof result.score !== 'number') {
        console.error('Invalid result data:', result);
        card.innerHTML = `
            <div class="result-card-header">
                <div class="result-card-title">Kết quả ${index}</div>
                <div class="result-card-score" style="background: #e53e3e; color: white;">
                    Lỗi dữ liệu
                </div>
            </div>
            <div class="result-content">
                <p class="result-text">Dữ liệu kết quả không hợp lệ</p>
            </div>
        `;
        return card;
    }
    
    const scoreColor = getScoreColor(result.score);
    
    card.innerHTML = `
        <div class="result-card-header">
            <div class="result-card-title">Kết quả ${index}</div>
            <div class="result-card-score" style="background: ${scoreColor.background}; color: ${scoreColor.text};">
                ${result.score.toFixed(4)} (${result.model || 'unknown'})
            </div>
        </div>
        <div class="result-content">
            <div class="result-item">
                <label>Tiếng Hán gốc:</label>
                <p class="result-text">${escapeHtml(result.han_original || '')}</p>
            </div>
            <div class="result-item">
                <label>Tiếng Việt gốc:</label>
                <p class="result-text">${escapeHtml(result.best_match || '')}</p>
            </div>
            <div class="result-item">
                <label>Bản dịch:</label>
                <p class="result-text">${escapeHtml(result.translation || '')}</p>
            </div>
        </div>
    `;
    
    return card;
}

function getScoreColor(score) {
    if (score >= 0.9) {
        return { background: '#48bb78', text: 'white' };
    } else if (score >= 0.7) {
        return { background: '#ed8936', text: 'white' };
    } else if (score >= 0.5) {
        return { background: '#ecc94b', text: 'black' };
    } else {
        return { background: '#e53e3e', text: 'white' };
    }
}

function showError(message) {
    errorMessage.textContent = message;
    error.classList.remove('hidden');
    
    // Scroll to error
    setTimeout(() => {
        error.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function hideError() {
    error.classList.add('hidden');
}

function hideResults() {
    results.classList.add('hidden');
    bestResult.classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility function to format score
function formatScore(score) {
    return (score * 100).toFixed(1) + '%';
}

// Add some nice animations
function addFadeInAnimation(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        element.style.transition = 'all 0.5s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100);
}

// Initialize animations for results
document.addEventListener('DOMContentLoaded', function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    // Observe result cards for animation
    const resultCards = document.querySelectorAll('.result-card');
    resultCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
        observer.observe(card);
    });
}); 