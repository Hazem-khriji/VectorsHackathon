import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import type { Product, SearchResponse } from './types';

// Generate a unique session ID for behavior tracking
const getSessionId = () => {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
};

function App() {
    const [query, setQuery] = useState('');
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [initialLoading, setInitialLoading] = useState(true);

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [isSearchMode, setIsSearchMode] = useState(false);

    // AI Response state
    const [aiResponse, setAiResponse] = useState<string | null>(null);

    // Image Search state
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    // Financial context state
    const [budget, setBudget] = useState<string>('');
    const [showFilters, setShowFilters] = useState(false);

    // Session ID for tracking
    const sessionId = getSessionId();

    // Track user behavior
    const trackEvent = useCallback(async (eventType: string, data: object) => {
        try {
            await fetch('http://localhost:8000/api/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    event_type: eventType,
                    timestamp: new Date().toISOString(),
                    ...data
                })
            });
        } catch (e) {
            console.log('Tracking failed:', e);
        }
    }, [sessionId]);

    // Fetch products on page load
    useEffect(() => {
        fetchProducts(1);
    }, []);

    const fetchProducts = async (page: number) => {
        if (page === 1) {
            setInitialLoading(true);
        } else {
            setLoading(true);
        }
        setError(null);
        setAiResponse(null);

        try {
            // Pass session_id to enable personalized cumulative feed
            let url = `http://localhost:8000/api/products?page=${page}&limit=12&session_id=${sessionId}`;
            if (budget) {
                url += `&max_price=${budget}`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Failed to fetch products');
            }

            const data: SearchResponse = await response.json();
            if (data.success) {
                setProducts(data.data);
                setCurrentPage(data.current_page || 1);
                setTotalPages(data.total_pages || 1);
                setTotalCount(data.total_count || 0);
                setIsSearchMode(false);
            } else {
                throw new Error(data.error || 'An error occurred');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setInitialLoading(false);
            setLoading(false);
        }
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedImage(file);
            setImagePreview(URL.createObjectURL(file));
            // Reset query if just searching by image, or keep it to refine
        }
    };

    const clearImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
    };

    const handleSearch = async () => {
        if (!query.trim() && !selectedImage) {
            fetchProducts(1);
            return;
        }

        setLoading(true);
        setError(null);
        setIsSearchMode(true);
        setAiResponse(null);
        setProducts([]);

        // Track search event
        trackEvent('search', {
            query,
            budget: budget || null,
            has_image: !!selectedImage
        });

        try {
            const formData = new FormData();
            formData.append('query', query);
            if (budget) {
                formData.append('max_budget', budget);
            }
            if (selectedImage) {
                formData.append('image', selectedImage);
            }

            const response = await fetch('http://localhost:8000/api/search-products', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data: SearchResponse = await response.json();
            if (data.success) {
                setAiResponse(data.ai_response || null);
                setProducts(data.data);
                setTotalCount(data.count);

                // Refresh recommendations after search (preference updated)
                // setTimeout(fetchRecommendations, 1000);
            } else {
                throw new Error(data.error || 'An error occurred');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setQuery('');
        setBudget('');
        clearImage();
        setError(null);
        setIsSearchMode(false);
        setAiResponse(null);
        fetchProducts(1);
        fetchProducts(1);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    const handlePageChange = (page: number) => {
        if (page >= 1 && page <= totalPages && page !== currentPage) {
            fetchProducts(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const handleProductClick = (product: Product) => {
        trackEvent('product_click', {
            product_id: product.id,
            category: product.category,
            price: product.discounted_price
        });

        // Refresh recommendations after click (intent updated)
        // Intent will normally be reflected on next feed fetch
    };

    const handleAddToCart = (product: Product, e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        trackEvent('add_to_cart', {
            product_id: product.id,
            category: product.category,
            price: product.discounted_price
        });
        alert(`Added to cart: ${product.category}`);

        // Refresh recommendations after add to cart (strong intent)
        // Intent will normally be reflected on next feed fetch
    };

    const renderStars = (rating: number) => {
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;

        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars.push(<span key={i} className="star filled">★</span>);
            } else if (i === fullStars && hasHalfStar) {
                stars.push(<span key={i} className="star half">★</span>);
            } else {
                stars.push(<span key={i} className="star empty">★</span>);
            }
        }
        return stars;
    };

    const renderPagination = () => {
        if (totalPages <= 1 || isSearchMode) return null;

        const pages = [];
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        pages.push(
            <button
                key="prev"
                className="pagination-btn"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
            >
                ← Prev
            </button>
        );

        if (startPage > 1) {
            pages.push(
                <button key={1} className="pagination-btn" onClick={() => handlePageChange(1)}>1</button>
            );
            if (startPage > 2) {
                pages.push(<span key="dots1" className="pagination-dots">...</span>);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            pages.push(
                <button
                    key={i}
                    className={`pagination-btn ${currentPage === i ? 'active' : ''}`}
                    onClick={() => handlePageChange(i)}
                >
                    {i}
                </button>
            );
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                pages.push(<span key="dots2" className="pagination-dots">...</span>);
            }
            pages.push(
                <button key={totalPages} className="pagination-btn" onClick={() => handlePageChange(totalPages)}>
                    {totalPages}
                </button>
            );
        }

        pages.push(
            <button
                key="next"
                className="pagination-btn"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
            >
                Next →
            </button>
        );

        return (
            <div className="pagination">
                <div className="pagination-info">
                    Showing page {currentPage} of {totalPages} ({totalCount} total products)
                </div>
                <div className="pagination-controls">{pages}</div>
            </div>
        );
    };

    const renderProductCards = (productList: Product[]) => (
        <div className="products-grid">
            {productList.map((product) => (
                <div
                    key={product.id}
                    className="product-card"
                    onClick={() => handleProductClick(product)}
                >
                    <div className="product-image-container">
                        <img
                            src={product.image_url}
                            alt={product.category}
                            className="product-image"
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x300?text=No+Image';
                            }}
                        />
                        {(Number(product.actual_price) || 0) > (Number(product.discounted_price) || 0) && (
                            <span className="discount-badge">
                                {Math.round((1 - (Number(product.discounted_price) || 0) / (Number(product.actual_price) || 1)) * 100)}% OFF
                            </span>
                        )}
                    </div>

                    <div className="product-info">
                        <span className="product-category">{product.category}</span>

                        <div className="product-rating">
                            {renderStars(Number(product.rating) || 0)}
                            <span className="rating-value">({(Number(product.rating) || 0).toFixed(1)})</span>
                        </div>

                        <div className="product-pricing">
                            {(Number(product.actual_price) || 0) > (Number(product.discounted_price) || 0) && (
                                <span className="original-price">${(Number(product.actual_price) || 0).toFixed(2)}</span>
                            )}
                            <span className="current-price">${(Number(product.discounted_price) || 0).toFixed(2)}</span>
                        </div>

                        <div className="product-actions">
                            <a
                                href={product.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="view-product-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleProductClick(product);
                                }}
                            >
                                View →
                            </a>
                            <button
                                className="add-to-cart-btn"
                                onClick={(e) => handleAddToCart(product, e)}
                            >
                                🛒 Add
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <div className="app">
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <span className="logo-icon">🛍️</span>
                        <h1>FinCommerce Search</h1>
                    </div>
                    <p className="tagline">AI-powered product discovery with financial context</p>
                </div>
            </header>

            {/* Search Section */}
            <section className="search-section">
                <div className="search-container">
                    {/* Image Preview */}
                    {imagePreview && (
                        <div className="image-preview-container">
                            <span className="preview-label">Search by image:</span>
                            <div className="preview-wrapper">
                                <img src={imagePreview} alt="Search Preview" className="image-preview" />
                                <button className="remove-image-btn" onClick={clearImage}>×</button>
                            </div>
                        </div>
                    )}

                    <div className="search-input-wrapper">
                        <span className="search-icon">🔍</span>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Search for products or upload an image..."
                            className="search-input"
                        />

                        {/* Hidden File Input */}
                        <input
                            type="file"
                            id="image-upload"
                            accept="image/*"
                            style={{ display: 'none' }}
                            onChange={handleImageChange}
                        />

                        {/* Camera Icon Trigger */}
                        <label htmlFor="image-upload" className="camera-btn" title="Search by Image">
                            📷
                        </label>
                    </div>

                    {/* Financial Filters Toggle */}
                    <button
                        className="filter-toggle-btn"
                        onClick={() => setShowFilters(!showFilters)}
                    >
                        💰 {showFilters ? 'Hide' : 'Show'} Budget Filter
                    </button>

                    {/* Financial Context Filters */}
                    {showFilters && (
                        <div className="financial-filters">
                            <div className="filter-group">
                                <label htmlFor="budget">💵 Max Budget ($)</label>
                                <input
                                    type="number"
                                    id="budget"
                                    value={budget}
                                    onChange={(e) => setBudget(e.target.value)}
                                    placeholder="e.g., 500"
                                    className="budget-input"
                                    min="0"
                                />
                            </div>
                        </div>
                    )}

                    <div className="search-buttons">
                        <button onClick={handleSearch} disabled={loading || initialLoading} className="search-btn">
                            {loading ? <span className="spinner"></span> : '🔍 Search'}
                        </button>
                        <button onClick={handleReset} className="reset-btn" disabled={loading || initialLoading}>
                            ↺ Reset
                        </button>
                    </div>
                </div>
            </section>

            {/* Error Message */}
            {error && (
                <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    {error}
                </div>
            )}

            {/* Loading State */}
            {(loading || initialLoading) && (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>{initialLoading ? 'Loading products...' : 'AI is analyzing your search...'}</p>
                </div>
            )}



            {/* Search Results (AI Response + Product Cards) */}
            {!loading && !initialLoading && isSearchMode && (
                <section className="search-results-section">
                    {aiResponse && (
                        <div className="ai-response-section">
                            <div className="ai-response-header">
                                <span className="ai-icon">🤖</span>
                                <h2>AI Recommendations</h2>
                            </div>
                            <div className="ai-response-content">
                                <ReactMarkdown>{aiResponse}</ReactMarkdown>
                            </div>
                        </div>
                    )}

                    {products.length > 0 && (
                        <div className="search-products-section">
                            <div className="results-header">
                                <h2>
                                    <span className="results-icon">📦</span>
                                    {`Found ${products.length} Matching Products`}
                                    {budget && ` (Under $${budget})`}
                                </h2>
                            </div>
                            {renderProductCards(products)}
                        </div>
                    )}

                    <div className="back-to-products">
                        <button onClick={handleReset} className="back-btn">
                            ← Back to All Products
                        </button>
                    </div>
                </section>
            )}

            {/* Products Grid Section (Browse Mode) */}
            {!loading && !initialLoading && !isSearchMode && (
                <section className="results-section">
                    <div className="results-header">
                        <h2>
                            <span className="results-icon">✨</span>
                            {products.length > 0
                                ? `${totalCount} products`
                                : 'No products found'}
                            {budget && ` (Under $${budget})`}
                        </h2>
                    </div>

                    {products.length > 0 && (
                        <>
                            {renderProductCards(products)}
                            {renderPagination()}
                        </>
                    )}
                </section>
            )}
        </div>
    );
}

export default App;
