"""LinkedIn posting functionality."""

import requests
import json
import base64


class LinkedInPoster:
    """Post to LinkedIn using the API."""
    
    def __init__(self, client_id, client_secret, access_token, person_urn=None, linkedin_version="202503"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.person_urn = person_urn
        self.linkedin_version = linkedin_version
        self.api_base = "https://api.linkedin.com/v2"
        self.rest_base = "https://api.linkedin.com/rest"
    
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
    
    def _get_current_user(self, debug=False):
        """Get the current user's profile information."""
        url = f"{self.api_base}/userinfo"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": self.linkedin_version
        }

        if debug:
            print(f"[DEBUG] Requesting user info from: {url}")
            print(f"[DEBUG] Headers: {headers}")

        try:
            response = requests.get(url, headers=headers)
            if debug:
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response text: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e1:
            print(f"Could not get user from /userinfo: {e1}")
            if debug and hasattr(e1, 'response') and e1.response is not None:
                print(f"[DEBUG] Error response: {e1.response.text}")

        author_id = self._parse_user_id_from_token()
        if author_id:
            if debug:
                print(f"[DEBUG] Parsed user_id from token: {author_id}")
            return {"id": author_id}

        raise RuntimeError("Cannot get user ID. Please set LINKEDIN_PERSON_URN in linkp.env")
    
    def post_text_update(self, text, debug=False):
        """Post a text update to LinkedIn."""
        author_urn = None

        if self.person_urn:
            author_urn = self.person_urn
        else:
            try:
                profile = self._get_current_user(debug=debug)
                author_id = profile.get("id")
                author_urn = f"urn:li:person:{author_id}"
            except Exception as e1:
                if debug:
                    print(f"[DEBUG] Error getting author ID: {e1}")
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
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": self.linkedin_version
        }

        if debug:
            print(f"[DEBUG] Posting text update to: {url}")
            print(f"[DEBUG] Headers: {headers}")
            print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, json=payload, headers=headers)
            if debug:
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response text: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                except Exception:
                    error_detail = "Could not read error response text."
                if debug:
                    print(f"[DEBUG] Error posting text update: {e}\nLinkedIn response: {error_detail}")
                raise RuntimeError(f"Error posting text update: {e}\nLinkedIn response: {error_detail}")
            else:
                if debug:
                    print(f"[DEBUG] Error posting text update: {e}")
                raise RuntimeError(f"Error posting text update: {e}")
    
    def post_with_image(self, text, image_path, debug=False):
        """Post to LinkedIn with an image."""
        asset_urn = self._upload_image(image_path, debug=debug)

        author_urn = None
        if self.person_urn:
            author_urn = self.person_urn
        else:
            try:
                profile = self._get_current_user(debug=debug)
                author_id = profile.get("id")
                author_urn = f"urn:li:person:{author_id}"
            except Exception as e1:
                if debug:
                    print(f"[DEBUG] Error getting author ID for image post: {e1}")
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
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": self.linkedin_version
        }

        if debug:
            print(f"[DEBUG] Posting image update to: {url}")
            print(f"[DEBUG] Headers: {headers}")
            print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, json=payload, headers=headers)
            if debug:
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response text: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                except Exception:
                    error_detail = "Could not read error response text."
                if debug:
                    print(f"[DEBUG] Error posting with image: {e}\nLinkedIn response: {error_detail}")
                raise RuntimeError(f"Error posting with image: {e}\nLinkedIn response: {error_detail}")
            else:
                if debug:
                    print(f"[DEBUG] Error posting with image: {e}")
                raise RuntimeError(f"Error posting with image: {e}")
    
    def _upload_image(self, image_path, debug=False):
        """Upload an image to LinkedIn."""
        user_id = None
        if self.person_urn:
            user_id = self.person_urn.replace("urn:li:person:", "")
        else:
            try:
                user_info = self._get_current_user(debug=debug)
                user_id = user_info.get("id")
            except Exception as e1:
                if debug:
                    print(f"[DEBUG] Error getting user ID for image upload: {e1}")
                user_id = self._parse_user_id_from_token()
                if debug:
                    print(f"[DEBUG] Parsed user_id from token for image upload: {user_id}")

        if not user_id:
            if debug:
                print("[DEBUG] No user ID found for image upload.")
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

        register_url = f"{self.rest_base}/images?action=initializeUpload"
        register_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": self.linkedin_version
        }

        if debug:
            print(f"[DEBUG] Registering image upload at: {register_url}")
            print(f"[DEBUG] Headers: {register_headers}")
            print(f"[DEBUG] Payload: {json.dumps(register_payload, indent=2)}")

        try:
            register_response = requests.post(
                register_url,
                json=register_payload,
                headers=register_headers
            )
            if debug:
                print(f"[DEBUG] Register response status: {register_response.status_code}")
                print(f"[DEBUG] Register response text: {register_response.text}")
            register_response.raise_for_status()
            register_data = register_response.json()

            # The new REST API response structure may differ; adjust as needed
            value = register_data.get("value", register_data)
            upload_url = value.get("uploadUrl") or value.get("uploadUrlInfo", {}).get("uploadUrl")
            asset_urn = value.get("image") or value.get("asset") or value.get("imageUrn")

            if debug:
                print(f"[DEBUG] upload_url: {upload_url}")
                print(f"[DEBUG] asset_urn: {asset_urn}")

            if not upload_url or not asset_urn:
                if debug:
                    print("[DEBUG] Failed to get upload URL or asset URN from LinkedIn REST API")
                raise RuntimeError("Failed to get upload URL or asset URN from LinkedIn REST API")

            with open(image_path, 'rb') as image_file:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                if debug:
                    print(f"[DEBUG] Uploading image to: {upload_url}")
                upload_response = requests.put(upload_url, data=image_file, headers=headers)
                if debug:
                    print(f"[DEBUG] Upload response status: {upload_response.status_code}")
                    print(f"[DEBUG] Upload response text: {upload_response.text}")
                upload_response.raise_for_status()

            return asset_urn

        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                except Exception:
                    error_detail = "Could not read error response text."
                if debug:
                    print(f"[DEBUG] LinkedIn image upload error: {e}\nLinkedIn response: {error_detail}")
                raise RuntimeError(f"LinkedIn image upload error: {e}\nLinkedIn response: {error_detail}")
            else:
                if debug:
                    print(f"[DEBUG] LinkedIn image upload error: {e}")
                raise RuntimeError(f"LinkedIn image upload error: {e}")
