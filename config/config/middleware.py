class RecentProductsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.view_count = 10
    
    def __call__(self, request):
        response = self.get_response(request)
        history = request.session.get("recent_views", [])
        if request.resolver_match and request.resolver_match.view_name == "catalog:product_detail":
            slug = request.resolver_match.kwargs.get("slug")
            if slug:
                history = [slug] + [item for item in history if item != slug]
                request.session["recent_views"] = history[:self.view_count]
                request.session.modified = True
        
        return response