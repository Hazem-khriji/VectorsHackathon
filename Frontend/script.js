// API Configuration
const API_URL = 'http://localhost:8000';  // Change this to your backend URL

// Get DOM elements
const form = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const spinner = document.getElementById('spinner');
const resultsDiv = document.getElementById('results');
const resultsContent = document.getElementById('resultsContent');
const errorDiv = document.getElementById('error');

// Image preview functionality
imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            imagePreview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <p>${file.name}</p>
            `;
        };
        
        reader.readAsDataURL(file);
    } else {
        imagePreview.innerHTML = '';
    }
});

// Form submission
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Clear previous results/errors
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    
    // Validate inputs
    const query = queryInput.value.trim();
    const imageFile = imageInput.files[0];
    
    if (!query && !imageFile) {
        showError('Please provide a search query or upload an image');
        return;
    }
    
    // Show loading state
    setLoading(true);
    
    try {
        // Prepare form data
        const formData = new FormData();
        
        if (query) {
            formData.append('query', query);
        }
        
        if (imageFile) {
            formData.append('image', imageFile);
        }
        
        // Make API request
        const response = await fetch(`${API_URL}/api/search`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResults(data.data);
        } else {
            showError(data.error || 'An error occurred');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to the server. Please try again.');
    } finally {
        setLoading(false);
    }
});

// Helper functions
function setLoading(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
    } else {
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

function showResults(data) {
    resultsContent.textContent = typeof data === 'string' 
        ? data 
        : JSON.stringify(data, null, 2);
    resultsDiv.classList.remove('hidden');
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}
