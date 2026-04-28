function app() {
    return {
        // State
        feeds: [],
        selectedFeeds: [],
        search: '',
        dateFrom: '',
        dateTo: '',
        articles: [],
        page: 0,
        pageSize: 20,
        hasMore: true,
        showModal: false,
        currentArticle: null,

        // Initialize
        async init() {
            await this.loadFeeds();
            await this.loadArticles();
        },

        // Load feeds for sidebar
        async loadFeeds() {
            const res = await fetch('/api/feeds?active_only=true');
            this.feeds = await res.json();
        },

        // Build query string from filters
        buildQuery() {
            const params = new URLSearchParams();
            if (this.selectedFeeds.length > 0) {
                // FastAPI expects repeated query params like feed_id=1&feed_id=2
                this.selectedFeeds.forEach(id => params.append('feed_id', id));
            }
            if (this.search.trim()) {
                params.append('search', this.search.trim());
            }
            if (this.dateFrom) {
                params.append('date_from', this.dateFrom + 'T00:00:00');
            }
            if (this.dateTo) {
                params.append('date_to', this.dateTo + 'T23:59:59');
            }
            params.append('skip', (this.page * this.pageSize).toString());
            params.append('limit', this.pageSize.toString());
            return params.toString();
        },

        // Fetch articles from API
        async loadArticles() {
            this.page = 0; // reset pagination when filters change
            this.articles = [];
            const query = this.buildQuery();
            const res = await fetch('/api/articles?' + query);
            const data = await res.json();
            this.articles = data;
            this.hasMore = data.length === this.pageSize;
        },

        // Load more articles (infinite scroll simulation)
        async loadMore() {
            this.page++;
            const query = this.buildQuery();
            const res = await fetch('/api/articles?' + query);
            const data = await res.json();
            this.articles = this.articles.concat(data);
            this.hasMore = data.length === this.pageSize;
        },

        // Refresh feeds via API
        async refreshFeeds() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = '⏳ Refreshing...';
            await fetch('/api/refresh', { method: 'POST' });
            await this.loadArticles();
            btn.disabled = false;
            btn.textContent = '🔄 Refresh now';
        },

        // Open detail modal
        openArticle(article) {
            this.currentArticle = article;
            this.showModal = true;
        },

        // Format date for display
        formatDate(isoString) {
            if (!isoString) return '';
            const date = new Date(isoString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
            });
        }
    };
}
