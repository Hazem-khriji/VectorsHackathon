export interface Product {
    id: number;
    category: string;
    rating: number;
    actual_price: number;
    discounted_price: number;
    image_url: string;
    product_url: string;
}

export interface SearchResponse {
    success: boolean;
    data: Product[];
    count: number;
    ai_response?: string;
    total_count?: number;
    total_pages?: number;
    current_page?: number;
    has_next?: boolean;
    has_prev?: boolean;
    error?: string;
}


