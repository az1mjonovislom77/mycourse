from social_core.backends.github import GithubOAuth2
import requests

class CustomGithubOAuth2(GithubOAuth2):
    def request(self, url, *args, **kwargs):
        kwargs['verify'] = False
        return requests.get(url, *args, **kwargs)
