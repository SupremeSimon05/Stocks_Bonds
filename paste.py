import requests

# Specify your Pastebin API key
API_KEY = 'ISVS84_pLDjmy9DjykhgJ6FE5qgIaLQV'

def get_user_pastes(username):
    """
    Retrieve all pastes from a user on Pastebin.

    Parameters:
    - username: The username whose pastes you want to retrieve.

    Returns:
    - A list of pastes retrieved from the user.
    """
    url = 'https://pastebin.com/api/api_userposts.php'  # Correct API endpoint
    params = {
        'api_dev_key': API_KEY,
        'api_user_name': username,
        'api_option': 'userposts',
        'api_results_limit': 100  # Maximum number of pastes to retrieve (adjust as needed)
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        pastes = response.text.splitlines()
        return pastes
    else:
        print(f"Failed to retrieve pastes: {response.status_code} - {response.text}")
        return None

def create_paste(content, paste_name=None):
    """
    Create a new paste on Pastebin using the Pull method.

    Parameters:
    - content: The content to be pasted.
    - paste_name: Optional name for the paste.

    Returns:
    - The URL of the created paste.
    """
    url = 'https://pastebin.com/api/api_post.php'
    params = {
        'api_dev_key': API_KEY,
        'api_option': 'paste',
        'api_paste_code': content,
        'api_paste_name': paste_name if paste_name else 'Untitled'
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to create paste: {response.status_code} - {response.text}")
        return None

# Example usage:
if __name__ == "__main__":
    paste_content = "This is the content of the new paste."
    paste_url = create_paste(paste_content, paste_name="My New Paste")
    if paste_url:
        print("New paste created:", paste_url)
    # Get all pastes from a user
    user_pastes = get_user_pastes('Stocks_bot')
    if user_pastes:
        print("User's pastes:")
        for paste in user_pastes:
            print(paste)
    
    # Create a new paste