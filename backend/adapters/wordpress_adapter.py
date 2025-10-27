"""
WordPress CMS Adapter - Schema Validator Pro
Simplified WordPress REST API integration for schema injection.

Features:
- WordPress REST API v2 integration
- Application Password authentication
- Schema injection to posts/pages
- Post retrieval and listing
"""

from typing import Dict, Any, List, Optional
import requests
from requests.auth import HTTPBasicAuth
import json


class WordPressAdapter:
    """
    WordPress CMS Adapter
    
    Simplified adapter for WordPress using REST API v2.
    Supports schema injection and basic post operations.
    """
    
    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress adapter
        
        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            app_password: Application Password (not regular password)
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self._session = requests.Session()
        self._session.auth = HTTPBasicAuth(username, app_password)
        
    def test_connection(self) -> bool:
        """
        Test connection to WordPress
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = self._session.get(
                f"{self.site_url}/wp-json",
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def test_authentication(self) -> bool:
        """
        Test authentication with WordPress
        
        Returns:
            bool: True if authentication successful
        """
        try:
            response = self._session.get(
                f"{self.api_base}/users/me",
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def inject_schema(self, post_id: int, schema: Dict[str, Any]) -> bool:
        """
        Inject Schema.org markup into WordPress post
        
        Args:
            post_id: WordPress post ID
            schema: Schema.org JSON-LD dictionary
            
        Returns:
            bool: True if injection successful
        """
        try:
            # Store schema in post meta
            url = f"{self.api_base}/posts/{post_id}"
            
            meta_data = {
                "meta": {
                    "_geo_schema": json.dumps(schema)
                }
            }
            
            response = self._session.post(
                url,
                json=meta_data,
                timeout=30
            )
            
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Get WordPress post by ID
        
        Args:
            post_id: WordPress post ID
            
        Returns:
            Dict containing post data, or None if not found
        """
        try:
            response = self._session.get(
                f"{self.api_base}/posts/{post_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def get_posts(self, per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """
        Get list of WordPress posts
        
        Args:
            per_page: Number of posts per page (max 100)
            page: Page number (1-based)
            
        Returns:
            List of post dictionaries
        """
        try:
            params = {
                "per_page": min(per_page, 100),
                "page": page
            }
            
            response = self._session.get(
                f"{self.api_base}/posts",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
    
    def search_posts(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Search for WordPress posts
        
        Args:
            query: Search query string
            per_page: Number of results (max 100)
            
        Returns:
            List of matching post dictionaries
        """
        try:
            params = {
                "search": query,
                "per_page": min(per_page, 100)
            }
            
            response = self._session.get(
                f"{self.api_base}/posts",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
    
    def get_schema(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Get stored schema from WordPress post
        
        Args:
            post_id: WordPress post ID
            
        Returns:
            Schema dictionary, or None if not found
        """
        try:
            post = self.get_post(post_id)
            if not post:
                return None
            
            # Get schema from post meta
            meta = post.get("meta", {})
            schema_json = meta.get("_geo_schema")
            
            if schema_json:
                if isinstance(schema_json, str):
                    return json.loads(schema_json)
                return schema_json
            return None
        except (json.JSONDecodeError, requests.exceptions.RequestException):
            return None
    
    def extract_content(self, post: Dict[str, Any]) -> str:
        """
        Extract plain text content from WordPress post
        
        Args:
            post: WordPress post dictionary
            
        Returns:
            Plain text content
        """
        # Get title
        title = post.get("title", {})
        if isinstance(title, dict):
            title_text = title.get("rendered", "")
        else:
            title_text = str(title)
        
        # Get content
        content = post.get("content", {})
        if isinstance(content, dict):
            content_text = content.get("rendered", "")
        else:
            content_text = str(content)
        
        # Simple HTML stripping (basic)
        import re
        content_text = re.sub(r'<[^>]+>', '', content_text)
        content_text = re.sub(r'\s+', ' ', content_text).strip()
        
        return f"{title_text}\n\n{content_text}"
    
    def get_post_url(self, post: Dict[str, Any]) -> str:
        """
        Get post URL
        
        Args:
            post: WordPress post dictionary
            
        Returns:
            Post URL
        """
        return post.get("link", "")
    
    def get_post_author(self, post: Dict[str, Any]) -> str:
        """
        Get post author name
        
        Args:
            post: WordPress post dictionary
            
        Returns:
            Author name (or "Unknown" if not found)
        """
        author_id = post.get("author")
        if not author_id:
            return "Unknown"
        
        try:
            response = self._session.get(
                f"{self.api_base}/users/{author_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                return user.get("name", "Unknown")
        except requests.exceptions.RequestException:
            pass
        
        return "Unknown"
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()

