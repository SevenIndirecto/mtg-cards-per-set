from scrapy.extensions import httpcache
from scrapy.utils.httpobj import urlparse_cached


class DoNotCacheSearchPolicy(httpcache.DummyPolicy):
    def __init__(self, settings):
        self.ignore_patterns = settings.getlist("CUSTOM_HTTPCACHE_IGNORE_PATTERNS")
        super(DoNotCacheSearchPolicy, self).__init__(settings)

    def should_cache_request(self, request):
        for pattern in self.ignore_patterns:
            if pattern in urlparse_cached(request).path:
                return False
        return True

    def should_cache_response(self, response, request):
        # return True
        # TODO: trying to avoid caching stuff we shouldn't? - ie, when we get rate limited etc
        return super(DoNotCacheSearchPolicy, self).should_cache_response(response=response, request=request)
