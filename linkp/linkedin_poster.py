"""LinkedIn posting functionality."""

import requests
import json
import base64


class LinkedInPoster:
    """Post to LinkedIn using the API."""
    
    def __init__(self, client_id, client_secret, access_token, person_urn=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.person_urn = person_urn
        self.api_base = "https://api.linkedin.com/v2"
    
    def _parse_user_id_from_token(self):
        """Parse user ID from access token payload."""
        try:
            parts = self.access_token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded_bytes = base64.urlsafe_b64decode(payload)
                decoded_dict = json.loads(decoded_bytes.decode('utf-8'))
                
                user_id = decoded_dict.get('sub') or decoded_dict.get('user_id')
                return user_id
        except Exception as e:
            print(f"Could not parse token: {e}")
        
        return None
    
    def _get_current_user(self):
        """Get the current user's profile information."""
        url = f"{self.api_base}/me"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.get(url, headers=headers, params={"projection": "(id)"})
            response.raise_for_status()
            return response.json()
        except Exception as e1:
            print(f"Could not get user from /me: {e1}")
        
        author_id = self._parse_user_id_from_token()
        if author_id:
            return {"id": author_id}
        
        raise RuntimeError("Cannot get user ID. Please set LINKEDIN_PERSON_URN in linkp.env")
    
    def post_text_update(self, text):
        """Post a text update to LinkedIn."""
        author_urn = None
        
        if self.person_urn:
            author_urn = self.person_urn
        else:
            try:
                profile = self._get_current_user()
                author_id = profile.get("id")
                author_urn = f"urn:li:person:{author_id}"
            except Exception as e1:
                raise RuntimeError(f"Cannot get author ID. Please set LINKEDIN_PERSON_URN in linkp.env. Error: {e1}")
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        url = f"{self.api_base}/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error posting text update: {e}")
    
    def post_with_image(self, text, image_path):
        """Post to LinkedIn with an image."""
        asset_urn = self._upload_image(image_path)
        
        author_urn = None
        if self.person_urn:
            author_urn = self.person_urn
        else:
            try:
                profile = self._get_current_user()
                author_id = profile.get("id")
                author_urn = f"urn:li:person:{author_id}"
            except:
                raise RuntimeError("Cannot get author ID for image post")
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {
                            "text": "Daily development progress update"
                        },
                        "media": asset_urn,
                        "title": {
                            "text": "Development Progress"
                        }
                    }]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        url = f"{self.api_base}/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error posting with image: {e}")
    
    def _upload_image(self, image_path):
        """Upload an image to LinkedIn."""
        user_id = None
        if self.person_urn:
            user_id = self.person_urn.replace("urn:li:person:", "")
        else:
            try:
                user_info = self._get_current_user()
                user_id = user_info.get("id")
            except:
                user_id = self._parse_user_id_from_token()
        
        if not user_id:
            raise RuntimeError("Cannot get user ID for image upload")
        
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{user_id}",
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }
        
        register_url = f"{self.api_base}/assets"
        register_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            register_response = requests.post(
                f"{register_url}?action=registerUpload",
                json=register_payload,
                headers=register_headers
            )
            register_response.raise_for_status()
            register_data = register_response.json()
            
            value = register_data.get("value", {})
            upload_mechanism = value.get("uploadMechanism", {})
            upload_url_info = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
            upload_url = upload_url_info.get("uploadUrl")
            asset_urn = value.get("asset")
            
            if not upload_url or not asset_urn:
                raise RuntimeError("Failed to get upload URL or asset URN from LinkedIn")
            
            with open(image_path, 'rb') as image_file:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                upload_response = requests.put(upload_url, data=image_file, headers=headers)
                upload_response.raise_for_status()
            
            return asset_urn
            
        except Exception as e:
            raise RuntimeError(f"LinkedIn image upload error: {e}")
