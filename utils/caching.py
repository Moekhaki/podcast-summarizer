import os
import hashlib
from typing import TypeVar, Callable, Any
from functools import wraps

T = TypeVar('T')

class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_path(self, content: str) -> str:
        """Generate cache file path from content hash"""
        hasher = hashlib.md5()
        hasher.update(content.encode('utf-8'))
        return os.path.join(self.cache_dir, f"{hasher.hexdigest()}.txt")
        
    def get_cached(self, content: str) -> str | None:
        """Retrieve cached content if it exists"""
        cache_path = self._get_cache_path(content)
        if os.path.exists(cache_path):
            print(f"[Cache] Loading from {cache_path}")
            with open(cache_path, 'r') as f:
                return f.read()
        return None
        
    def save_to_cache(self, content: str, result: str) -> None:
        """Save result to cache"""
        cache_path = self._get_cache_path(content)
        print(f"[Cache] Saving to {cache_path}")
        with open(cache_path, 'w') as f:
            f.write(result)

def with_cache(cache_dir: str) -> Callable:
    """Decorator to add caching to any function"""
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        cache_manager = CacheManager(cache_dir)
        
        @wraps(func)
        def wrapper(self, content: str, *args, **kwargs) -> str:
            # Try to get from cache first
            cached_result = cache_manager.get_cached(content)
            if cached_result is not None:
                return cached_result
                
            # Generate new result if not cached
            result = func(self, content, *args, **kwargs)
            
            # Cache the new result
            cache_manager.save_to_cache(content, result)
            return result
            
        return wrapper
    return decorator